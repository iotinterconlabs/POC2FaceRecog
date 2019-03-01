from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.template import RequestContext
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from recognize.aws_util import *
from datetime import datetime



# Create your views here.
@csrf_exempt
def index(request):
    template = loader.get_template('recognize/index.html')

    if request.method == 'POST':
        user_name = request.POST['username']
        for file in request.FILES.getlist('image'):
            upload_images_to_bucket(user_name, file)     
        response = {'status' : 'Uploaded'}
        return render(request, 'recognize/index.html', response)
    else:        
        return HttpResponse(template.render())

@csrf_exempt
def match(request):
    template = loader.get_template('recognize/match.html')
    now = '{:%Y%m%d%H%M%S}'.format(datetime.now())

    if request.method == 'POST':
        file = request.FILES.get('image')
        bucket_name, key = upload_images_to_bucket(now, file)
        person_name, score = match_person(bucket_name, key)
        delete_match_bucket(now)
        print("##################")
        print(person_name, score)
        response = {'Person' : person_name, 'Score' : score}
        return render(request, 'recognize/match.html', response)
    else:        
        return HttpResponse(template.render())