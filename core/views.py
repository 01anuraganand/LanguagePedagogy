from django.shortcuts import render
import time, os, nltk

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from . models import Image
from core.forms import ImageForm

from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

from dotenv import load_dotenv
load_dotenv()

# Create your views here.

def index_home(request):
    return render(request, 'core/html/indexhome.html')

def fileformaterror(request):
    return render(request, 'html/fileformat.html')

def upload_photo(request):    
    to_delete = Image.objects.all()
    to_delete.delete()
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    form  = ImageForm()
    img = Image.objects.all()
    return form, img
    

def extract_text_from_image(request, image_file_path):
    cvkey = os.environ['COG_CV_KEY']
    cvendpoint = os.environ['COG_CV_ENDPOINT']
    credential = CognitiveServicesCredentials(cvkey)
    cv_client = ComputerVisionClient(cvendpoint, credential)
    
    with open(image_file_path, 'rb') as raw_image:
        process_image = cv_client.read_in_stream(raw_image, raw = True)

        process_location = process_image.headers['Operation-Location']
        process_id = process_location.split("/")[-1]

        while True:
            read_result = cv_client.get_read_result(process_id)
            if read_result.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
                break;
            time.sleep(1)
        if read_result.status == OperationStatusCodes.succeeded:
            for page in read_result.analyze_result.read_results:
                for line in page.lines:
                    print(line.text)
    return read_result.analyze_result.read_results
    


def render_upload_photo_extract_text(request):
    form = img = read = None

    form , img = upload_photo(request)
    img_path = [str(x.photo.url) for x in img] 
    if len(img_path) > 0:
        try:
            read = extract_text_from_image(request,image_file_path='core'+ img_path[0])
        except:
            return render(request,'core/html/fileformat.html')

    return render(request, 'core/html/img_data_extract.html', {'form': form, 'img': img, 'text_line': read})

def pos_tagger(request, text):
    stopword = set(stopwords.words('english'))
    sentence_tokenized = sent_tokenize(text)

    storesentence = []
    for i in sentence_tokenized:
        storesentence.append(i)
    
    word_tokenize = []
    for i in storesentence:
        word_tokenize.append(nltk.word_tokenize(i))

    tagged = []
    for i in word_tokenize:
        tagged.append(nltk.pos_tag(i))
    a = []
    b = []
    for i in tagged:
        for j in i:
            a.append(j[0])
            b.append(j[1])

    tagged_res = {a[i]: b[i] for i in range(len(a))}
    return text, storesentence, tagged_res
    

def get_text_for_pos(request):
    text =storesentence= tagged = None
    if request.method == 'POST':
        text = request.POST.get('text')
        text, storesentence, tagged,  = pos_tagger(request, text)
    return render(request, 'core/html/pos_tagging.html', {'text': text, 'text_sentence': storesentence, 'tagged': tagged})