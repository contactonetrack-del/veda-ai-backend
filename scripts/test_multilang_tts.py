"""
Multi-Language TTS Test Script
Verifies all 10 Indian languages work correctly
"""
import os
import sys
import time
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.parler_tts import get_tts_service, LANGUAGE_NAMES, LANGUAGE_MODELS

# Sample text in each language
TEST_TEXTS = {
    "hi": "नमस्ते, मैं वेदा एआई हूँ।",              # Hindi
    "bn": "নমস্কার, আমি বেদা এআই।",                # Bengali
    "te": "నమస్కారం, నేను వేదా ఏఐ ని।",          # Telugu
    "mr": "नमस्कार, मी वेदा एआय आहे।",            # Marathi
    "ta": "வணக்கம், நான் வேதா AI.",               # Tamil
    "ur": "السلام علیکم، میں ویدا اے آئی ہوں۔",     # Urdu
    "kn": "ನಮಸ್ಕಾರ, ನಾನು ವೇದಾ AI.",               # Kannada
    "pa": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਮੈਂ ਵੇਦਾ ਏਆਈ ਹਾਂ।",        # Punjabi
    "or": "ନମସ୍କାର, ମୁଁ ବେଦା AI।",                # Odia
    "as": "নমস্কাৰ, মই বেদা AI।",                  # Assamese
    "gui": "નમસ્તે, હું વેદા AI છું.",              # Gujarati
    "ml": "നമസ്കാരം, ഞാൻ വേദ AI ആണ്.",          # Malayalam
    "sa": "नमः, अहम् वेदा AI अस्मि।",              # Sanskrit
    "ne": "नमस्ते, म वेदा AI हुँ।",                # Nepali
    "mai": "प्रणाम, हम वेदा AI छी।",               # Maithili
    "sat": "ᱡᱚᱦᱟᱨ, ᱤᱧ ᱵᱮᱫᱟ AI ᱠᱟᱱᱟᱧ।",             # Santali
    "kas": "اسلام علیکم، مے چُھ ناو ویدا AI।",      # Kashmiri
    "kok": "नमस्कार, हांव वेदा AI आसां।",            # Konkani
    "snd": "السلام عليڪم، مان ويدا AI آهيان।",      # Sindhi
    "mni": "খুরুমজরি, ঐহাক ত্বেদা AI নি।",         # Manipuri
    "doi": "नमस्ते, मैं वेदा AI हां।",               # Dogri
    "brx": "गोजोननाय, आं वेदा AI।",                 # Bodo
    "hne": "राम राम, मैं वेदा AI हरंव।",             # Chhattisgarhi
    "wsg": "ಜೋಹಾರ್, ನನ್ನ್ ವೇದಾ AI ಅಂದಾ।",           # Gondi
    "bho": "प्रणाम, हम वेदा एআই বানি।",            # Bhojpuri (uses Hindi TTS)
}

def test_all_languages():
    print("\n" + "="*60)
    print("🌐 VEDA AI - Multi-Language TTS Test")
    print("="*60)
    
    tts = get_tts_service()
    print(f"\n📊 TTS Status: {tts.get_status()}")
    print(f"📋 Supported Languages: {list(LANGUAGE_NAMES.keys())}")
    
    results = []
    
    for lang_code, text in TEST_TEXTS.items():
        lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)
        model = LANGUAGE_MODELS.get(lang_code, "fallback")
        
        print(f"\n{'─'*50}")
        print(f"🔊 Testing: {lang_name} ({lang_code})")
        print(f"   Model: {model}")
        print(f"   Text: {text[:40]}...")
        
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                output_path = tmp.name
            
            start = time.time()
            success = tts.synthesize(text, lang_code, output_path)
            latency = (time.time() - start) * 1000
            
            if success and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / 1024  # KB
                print(f"   ✅ SUCCESS | {latency:.0f}ms | {file_size:.1f}KB")
                results.append((lang_code, lang_name, "✅", latency))
                os.unlink(output_path)
            else:
                print(f"   ❌ FAILED")
                results.append((lang_code, lang_name, "❌", 0))
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append((lang_code, lang_name, "❌", 0))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"\n{'Language':<15} {'Code':<6} {'Status':<8} {'Latency':<10}")
    print("-"*45)
    
    passed = 0
    for lang_code, lang_name, status, latency in results:
        lat_str = f"{latency:.0f}ms" if latency > 0 else "N/A"
        print(f"{lang_name:<15} {lang_code:<6} {status:<8} {lat_str:<10}")
        if status == "✅":
            passed += 1
    
    print("-"*45)
    print(f"Total: {passed}/{len(results)} languages working")
    
    if passed == len(results):
        print("\n🎉 ALL LANGUAGES WORKING!")
    else:
        print(f"\n⚠️ {len(results) - passed} language(s) need attention")
    
    print("\n" + "="*60 + "\n")
    return passed == len(results)

if __name__ == "__main__":
    success = test_all_languages()
    sys.exit(0 if success else 1)
