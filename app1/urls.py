from django.urls import path
from . import views, cspalgo

app_name = 'app1'

# URLConf
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.aboutUs, name='aboutUs'),
    path('features/', views.features, name='features'),
    path('schedule/', cspalgo.home, name='csphome'),
    path('schedule/step1/', cspalgo.input_semester, name='input_semester'),
    path('schedule/step2/', cspalgo.input_subject, name='input_subject'),
    path('schedule/step3/', cspalgo.input_activity, name='input_activity'),
    path('schedule/result/', cspalgo.result, name='result'),
]
