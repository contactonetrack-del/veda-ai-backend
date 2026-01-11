"""
Whisper-Hindi Fine-tuning Script (4GB VRAM Optimized)
Uses LoRA + bitsandbytes 4-bit quantization.
"""
import torch
import os
from datasets import load_dataset, Audio
from transformers import (
    WhisperFeatureExtractor,
    WhisperTokenizer,
    WhisperProcessor,
    WhisperForConditionalGeneration,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from dataclasses import dataclass
from typing import Any, Dict, List, Union

# 1. Configuration
MODEL_ID = "openai/whisper-tiny"  # Tiny is safest for 4GB
LANGUAGE = "hindi"
TASK = "transcribe"
OUTPUT_DIR = "./whisper-tiny-hi-lora"

def train():
    # 2. Load Dataset (Common Voice 11 - Hindi)
    # Note: Requires 'huggingface-cli login' or HF_TOKEN
    print("Loading dataset...")
    common_voice = load_dataset("mozilla-foundation/common_voice_11_0", "hi", split="train", streaming=True)
    common_voice = common_voice.cast_column("sentence", Audio(sampling_rate=16000))
    
    # 3. Load Model & Processor
    print("Loading model and processor...")
    processor = WhisperProcessor.from_pretrained(MODEL_ID, language=LANGUAGE, task=TASK)
    tokenizer = WhisperTokenizer.from_pretrained(MODEL_ID, language=LANGUAGE, task=TASK)
    feature_extractor = WhisperFeatureExtractor.from_pretrained(MODEL_ID)

    # 4. Prepare Model for 4-bit training
    model = WhisperForConditionalGeneration.from_pretrained(
        MODEL_ID, 
        load_in_4bit=True, 
        device_map="auto"
    )
    model = prepare_model_for_kbit_training(model)

    # 5. Setup LoRA
    config = LoraConfig(
        r=32, 
        lora_alpha=64, 
        target_modules=["q_proj", "v_proj"], 
        lora_dropout=0.05, 
        bias="none"
    )
    model = get_peft_model(model, config)
    model.print_trainable_parameters()

    # 6. Data Collator
    @dataclass
    class DataCollatorSpeechSeq2SeqWithPadding:
        processor: Any

        def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
            input_features = [{"input_features": feature["input_features"]} for feature in features]
            batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")
            label_features = [{"input_ids": feature["labels"]} for feature in features]
            labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")
            labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
            if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
                labels = labels[:, 1:]
            batch["labels"] = labels
            return batch

    data_collator = DataCollatorSpeechSeq2SeqWithPadding(processor=processor)

    # 7. Training Arguments
    training_args = Seq2SeqTrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=1e-3,
        warmup_steps=50,
        max_steps=500,
        gradient_checkpointing=True,
        fp16=True,
        evaluation_strategy="no",
        save_steps=100,
        logging_steps=10,
        report_to=["tensorboard"],
        remove_unused_columns=False,
        label_names=["labels"],
    )

    # 8. Trainer
    trainer = Seq2SeqTrainer(
        args=training_args,
        model=model,
        train_dataset=common_voice,
        data_collator=data_collator,
        tokenizer=processor.feature_extractor,
    )

    # 9. Start Training
    print("Starting fine-tuning...")
    model.config.use_cache = False
    trainer.train()
    trainer.save_model(OUTPUT_DIR)
    print(f"Fine-tuning complete. Model saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    train()
