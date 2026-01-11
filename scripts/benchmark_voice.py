"""
Latency Benchmark for VEDA AI Voice Pipeline
Measures: ASR latency, TTS latency, and E2E pipeline latency
"""
import os
import sys
import time
import asyncio
import tempfile
import wave
import struct

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.whisper_asr import asr_service
from app.services.parler_tts import get_tts_service

# Sample Hindi text for testing
TEST_TEXT = "नमस्ते, मैं वेदा एआई हूँ। मैं आपकी कैसे मदद कर सकता हूँ?"

def generate_test_audio(duration_sec=3, sample_rate=16000):
    """Generate a simple test audio file (silence with some noise)"""
    import random
    
    num_samples = int(duration_sec * sample_rate)
    audio_data = bytes([random.randint(100, 156) for _ in range(num_samples * 2)])  # 16-bit
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        with wave.open(f.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data)
        return f.name

def benchmark_asr(audio_path, runs=3):
    """Benchmark ASR latency"""
    latencies = []
    
    for i in range(runs):
        start = time.time()
        result = asr_service.transcribe(audio_path)
        latency = (time.time() - start) * 1000  # ms
        latencies.append(latency)
        print(f"  ASR Run {i+1}: {latency:.0f}ms")
    
    avg = sum(latencies) / len(latencies)
    return avg, min(latencies), max(latencies)

def benchmark_tts(text, runs=3):
    """Benchmark TTS latency"""
    latencies = []
    tts = get_tts_service()
    
    for i in range(runs):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name
        
        start = time.time()
        tts.synthesize(text, "", output_path)
        latency = (time.time() - start) * 1000  # ms
        latencies.append(latency)
        print(f"  TTS Run {i+1}: {latency:.0f}ms")
        
        # Cleanup
        os.unlink(output_path)
    
    avg = sum(latencies) / len(latencies)
    return avg, min(latencies), max(latencies)

def benchmark_e2e(runs=3):
    """Benchmark full E2E pipeline (simulated)"""
    latencies = []
    tts = get_tts_service()
    
    for i in range(runs):
        # Generate test audio
        audio_path = generate_test_audio(duration_sec=2)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name
        
        start = time.time()
        
        # Step 1: ASR
        asr_result = asr_service.transcribe(audio_path)
        asr_time = time.time() - start
        
        # Step 2: "LLM" (simulated with test response)
        llm_start = time.time()
        response_text = TEST_TEXT  # In real scenario, this would call the LLM
        llm_time = time.time() - llm_start
        
        # Step 3: TTS
        tts_start = time.time()
        tts.synthesize(response_text, "", output_path)
        tts_time = time.time() - tts_start
        
        total_latency = (time.time() - start) * 1000  # ms
        latencies.append(total_latency)
        
        print(f"  E2E Run {i+1}: {total_latency:.0f}ms (ASR: {asr_time*1000:.0f}ms, TTS: {tts_time*1000:.0f}ms)")
        
        # Cleanup
        os.unlink(audio_path)
        os.unlink(output_path)
    
    avg = sum(latencies) / len(latencies)
    return avg, min(latencies), max(latencies)

def main():
    print("\n" + "="*60)
    print("VEDA AI Voice Pipeline - Latency Benchmark")
    print("="*60)
    
    # Generate test audio
    print("\n📝 Generating test audio...")
    test_audio = generate_test_audio()
    
    # Benchmark ASR
    print("\n🎤 Benchmarking ASR (Whisper)...")
    asr_avg, asr_min, asr_max = benchmark_asr(test_audio)
    
    # Benchmark TTS
    print("\n🔊 Benchmarking TTS (MMS)...")
    tts_avg, tts_min, tts_max = benchmark_tts(TEST_TEXT)
    
    # Benchmark E2E
    print("\n🔄 Benchmarking E2E Pipeline...")
    e2e_avg, e2e_min, e2e_max = benchmark_e2e()
    
    # Cleanup
    os.unlink(test_audio)
    
    # Summary
    print("\n" + "="*60)
    print("📊 BENCHMARK RESULTS")
    print("="*60)
    print(f"\n{'Component':<15} {'Avg':<10} {'Min':<10} {'Max':<10}")
    print("-"*45)
    print(f"{'ASR':<15} {asr_avg:>7.0f}ms {asr_min:>7.0f}ms {asr_max:>7.0f}ms")
    print(f"{'TTS':<15} {tts_avg:>7.0f}ms {tts_min:>7.0f}ms {tts_max:>7.0f}ms")
    print(f"{'E2E Pipeline':<15} {e2e_avg:>7.0f}ms {e2e_min:>7.0f}ms {e2e_max:>7.0f}ms")
    
    # Performance assessment
    print("\n" + "="*60)
    print("📈 PERFORMANCE ASSESSMENT")
    print("="*60)
    
    if e2e_avg < 1000:
        print("✅ EXCELLENT: < 1 second E2E latency (natural conversation)")
    elif e2e_avg < 2500:
        print("✅ GOOD: < 2.5 seconds E2E latency (acceptable for MVP)")
    elif e2e_avg < 5000:
        print("⚠️ ACCEPTABLE: < 5 seconds E2E latency (needs optimization)")
    else:
        print("❌ NEEDS WORK: > 5 seconds E2E latency")
    
    print("\n📌 Optimization Suggestions:")
    if asr_avg > 500:
        print("  - Consider GPU acceleration for Whisper")
    if tts_avg > 500:
        print("  - Consider lighter TTS model or GPU acceleration")
    if e2e_avg > 2500:
        print("  - Implement streaming pipeline (parallel ASR/TTS)")
    
    print("\n" + "="*60)
    print("✅ Benchmark Complete")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
