"""
VEDA AI Backend - Services Tests
Unit tests for core services
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTTSService:
    """Test Text-to-Speech service"""
    
    def test_language_models_defined(self):
        """Test that language models are defined"""
        from app.services.parler_tts import LANGUAGE_MODELS, LANGUAGE_NAMES
        
        assert len(LANGUAGE_MODELS) >= 15, "Should support at least 15 languages"
        assert "hi" in LANGUAGE_MODELS, "Should support Hindi"
        assert "en" in LANGUAGE_MODELS, "Should support English"
        assert len(LANGUAGE_NAMES) >= 15, "Should have names for languages"
    
    def test_language_coverage(self):
        """Test 22 scheduled languages are supported"""
        from app.services.parler_tts import LANGUAGE_MODELS
        
        scheduled_languages = [
            "hi", "bn", "te", "mr", "ta", "ur", "kn", "pa",
            "or", "as", "gui", "ml", "sa", "ne", "mai", "sat",
            "kas", "kok", "snd", "mni", "doi", "brx"
        ]
        
        for lang in scheduled_languages:
            assert lang in LANGUAGE_MODELS, f"Missing scheduled language: {lang}"


class TestReasoningEngine:
    """Test reasoning engine"""
    
    def test_reasoning_engine_exists(self):
        """Test reasoning engine can be imported"""
        from app.services.reasoning_engine import reasoning_engine
        
        assert reasoning_engine is not None
        assert hasattr(reasoning_engine, "chain_of_thought")
        assert hasattr(reasoning_engine, "tree_of_thought")
        assert hasattr(reasoning_engine, "self_consistency")


class TestDomainExperts:
    """Test domain expert agents"""
    
    def test_experts_defined(self):
        """Test that domain experts are defined"""
        from app.agents.domain_experts import (
            CareerCoachAgent,
            MentalHealthAgent,
            StudyTutorAgent
        )
        
        assert CareerCoachAgent.name == "Career Coach"
        assert MentalHealthAgent.name == "Mental Wellness Guide"
        assert StudyTutorAgent.name == "Study Tutor"


# Run with: pytest tests/test_services.py -v
