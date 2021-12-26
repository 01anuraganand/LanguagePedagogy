from django.shortcuts import render
from django.conf import settings
import os, requests, uuid
import azure.cognitiveservices.speech as speech_sdk

from langpedagogy.settings import MEDIA_ROOT
from . models import AudioModel
import time
from dotenv import load_dotenv
load_dotenv()

# Load the cognitive service KEY, ENDPOINT, LOCATION from .env
key = os.environ['KEY']
endpoint = os.environ['ENDPOINT']
location = os.environ['LOCATION']
# Set up the header information, which includes our subscription key
headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Ocp-Apim-Subscription-Region': location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

# Create your views here.
def index(request):
    return render(request,'translator/html/index.html')

def text_translate(request):
    if request.method == 'POST':
        # Read the text and language type from form
        original_text = request.POST.get('text')
        #target_language = request.POST.get('language')
        language = request.POST.get('language').split('#')
        target_language = language[0]
        target_voice = language[1]
        # Indicate that we want to translate and the API version (3.0) and the target language
        path = '/translate?api-version=3.0'
        # Add the target language parameter
        target_language_parameter = '&to=' + target_language
        # Create the full URL
        constructed_url = endpoint + path + target_language_parameter

        # Create the body of the request with the text to be translated
        body = [{ 'text': original_text }]

        # Make the call using post
        translator_request = requests.post(constructed_url, headers=headers, json=body)
        # Retrieve the JSON response
        translator_response = translator_request.json()
        # Retrieve the translation
        translated_text = translator_response[0]['translations'][0]['text']
        stream, _ = text_speech(request, translated_text, target_language, target_voice)
    return translated_text, original_text, target_language, target_voice, stream

def text_speech(request, text, language, voice):
    #os.remove('translator/static/audio/file.wav')
    # Load the cognitive service SPEECH_KEY
    Speechkey = os.environ['COG_SPEECH_KEY']
    speech_config = speech_sdk.SpeechConfig(subscription=Speechkey, region=location)
    speech_config.speech_synthesis_language = language
    speech_config.speech_synthesis_voice_name = voice
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    
    stream = speech_sdk.AudioDataStream(speech_synthesizer.speak_text_async(text).get())
    
    path = os.path.join(settings.MEDIA_ROOT,'audio/' + 'file.wav')
    
    stream.save_to_wav_file(path)
    to_delete = AudioModel.objects.all()
    to_delete.delete()
    save_file = AudioModel()
    path = 'audio/'+'file.wav'
    save_file.audio.name = path
    save_file.save()

    return stream, speech_config

def text_translate_render(request):
    translated_text, original_text, target_language, target_voice, stream = text_translate(request)
    audio_file = AudioModel.objects.get()
    stream = audio_file
    return render(request, 'translator/html/results.html',{'translated_text':translated_text,'original_text':original_text,'target_language':target_language, 'speech': target_voice, 'stream': stream})

def text_speech_render(request):
    stream = None
    if request.method == 'POST':
        text = request.POST.get('text')
        language = request.POST.get('language').split('#')
        target_language = language[0]
        target_voice = language[1]
        #Speechkey = os.environ['COG_SPEECH_KEY']
        #speech_config = speech_sdk.SpeechConfig(subscription=Speechkey, region=location)

        #a = speech_sdk.AutoDetectSourceLanguageConfig(text)
        if len(text)> 0:
            stream, speech_config  = text_speech(request, text, language=target_language,voice=target_voice)  
            audio_file = AudioModel.objects.get()
            stream = audio_file

    return render(request, 'translator/html/speech.html',{'stream': stream})

def pronunciationcheck(request):
    text = path = recognized_text = pronunciation_assessment_result = None

    speech_key, service_region = os.environ['COG_SPEECH_KEY'], os.environ['LOCATION']
    speech_config = speech_sdk.SpeechConfig(subscription=speech_key, region=service_region)
    if request.method == 'POST':
        text = request.POST.get('text')

    if request.method == 'POST':
        recognized_text = request.POST.get('pronunciationspeech')
        speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        stream = speech_sdk.AudioDataStream(speech_synthesizer.speak_text_async(recognized_text).get())
        orig_path = os.path.join(settings.MEDIA_ROOT,'audio/' + 'file.wav')
    
        stream.save_to_wav_file(orig_path)
        to_delete = AudioModel.objects.all()
        to_delete.delete()
        save_file = AudioModel()
        path = 'audio/'+'file.wav'
        save_file.audio.name = path
        save_file.save()
    
        audio_config = speech_sdk.audio.AudioConfig(filename=orig_path)
        pronunciation_assessment_config = speech_sdk.PronunciationAssessmentConfig(
                reference_text=text,
                grading_system=speech_sdk.PronunciationAssessmentGradingSystem.HundredMark,
                granularity=speech_sdk.PronunciationAssessmentGranularity.Phoneme)
                
        speech_recognizer = speech_sdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        # apply the pronunciation assessment configuration to the speech recognizer
        pronunciation_assessment_config.apply_to(speech_recognizer)
        result = speech_recognizer.recognize_once()
        pronunciation_assessment_result = speech_sdk.PronunciationAssessmentResult(result)
        
    


    return text, recognized_text, pronunciation_assessment_result

def pronunciation_page(request):
    return render(request, 'translator/html/pronunciation.html')

def pronunciationresult(request):
    try:
        text, recognized_text, pronunciation_assessment_result = pronunciationcheck(request)
        if text == '':
            textnotfound = True
            return render(request,'translator/html/speaknotgenerated.html',{'textnotfound' : textnotfound})
    except:
        voicenotfound = True
        return render(request, 'translator/html/speaknotgenerated.html',{'voicenotfound': voicenotfound})

    return render(request, 'translator/html/pronunciationresult.html',{'original_text': text, 'recognized_text': recognized_text,'pronunciation':pronunciation_assessment_result})