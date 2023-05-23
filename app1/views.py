from django.http import HttpResponse
from django.template import loader

# Create your views here.

def home(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context, request))

def aboutUs(request):
    template = loader.get_template('aboutus.html')
    context = {}
    return HttpResponse(template.render(context, request))

def features(request):
    template = loader.get_template('features.html')
    context = {}
    return HttpResponse(template.render(context, request))
