from django.http import HttpResponse
from django.template import loader
from django.templatetags.static import static
from django.shortcuts import redirect, render
from django.urls import reverse
from django import forms

from app1.models import SubjectsAvailable, UserSemester, Schedule

import os
import sys

# Forms for inputting data
class InputSubjectPref(forms.Form):
    subject_name = forms.CharField(label='Input')
    subject_code = forms.CharField(label='Input')

class InputSemester(forms.Form):
    user_semester = forms.IntegerField(label='Input')

class InputActivity(forms.Form):
    name = forms.CharField(label='input')
    day = forms.CharField(label='input')
    start_hour = forms.IntegerField(label='input')
    end_hour = forms.IntegerField(label='input')

def make_available(input_file, user_semester):
    for line in input_file:
        attribute_array = line.split()
        if '-' in attribute_array:
            continue

        if int(attribute_array[2]) == int(user_semester):
            subject = SubjectsAvailable(
                    name=attribute_array[0],
                    subject_code=attribute_array[1],
                    semester=attribute_array[2],
                    sks=attribute_array[3],
                    day=attribute_array[4],
                    start_hour=attribute_array[5],
                    end_hour=attribute_array[6],
                    class_name=attribute_array[7],
                    lecturer=attribute_array[8],
                    status=attribute_array[9],
                    )
            subject.save()

def add_activity(attribute_array):
    subject = Schedule(
            name=attribute_array[0],
            subject_code=attribute_array[1],
            day=attribute_array[2],
            start_hour=attribute_array[3],
            end_hour=attribute_array[4],
            )
    subject.save()

def home(request):
    return redirect('../schedule/step1/')

def input_semester(request):
    template = loader.get_template('input_semester.html')
    context = {}

    SubjectsAvailable.objects.all().delete()
    if request.method == 'POST':
        form = InputSemester(request.POST)
        if form.is_valid():
            user_semester = form.cleaned_data['user_semester']
            module_dir = os.path.dirname(__file__)
            file_path = os.path.join(module_dir, 'static/jadwal22-23.txt')
            input_file = open(file_path, 'r')
            
            make_available(input_file, user_semester)

            Schedule.objects.all().delete()

            return redirect('../step2/')
        else:
            form = input_semester(request.POST)

    return HttpResponse(template.render(context, request))

def input_subject(request):
    template = loader.get_template('input_subject.html')
    data = SubjectsAvailable.objects.values('name').distinct()
    context = {"data": data}

    if request.method == 'POST':
        form = InputSubjectPref(request.POST)
        if form.is_valid():
            subject_name = form.cleaned_data['subject_name']
            subject_code = form.cleaned_data['subject_code']
            
            subject = SubjectsAvailable.objects.get(name=subject_name, subject_code=subject_code)
            scheduled = Schedule.objects.all()

            flag = 0
            for item in scheduled:
                if (subject.day == item.day) and (int(subject.start_hour) < int(item.end_hour)) and (int(subject.end_hour) > int(item.start_hour)):
                    flag = 1
                    break

            if flag == 0:
                arr = []
                arr.append(subject.name)
                arr.append(subject.subject_code)
                arr.append(subject.day)
                arr.append(subject.start_hour)
                arr.append(subject.end_hour)
                add_activity(arr)

            this_schedule = Schedule.objects.all()
            context.update({"this_schedule": this_schedule})

            return HttpResponse(template.render(context, request))
        else:
            form = InputSubjectPref(request.POST)

    return HttpResponse(template.render(context, request))

def input_activity(request):
    template = loader.get_template('input_activity.html')
    context = {}
    this_schedule = Schedule.objects.all()
    context.update({"this_schedule": this_schedule})

    form = InputActivity(request.POST)

    if form.is_valid():
        name = form.cleaned_data['name']
        day = form.cleaned_data['day']
        start_hour = form.cleaned_data['start_hour']
        end_hour = form.cleaned_data['end_hour']
        
        scheduled = Schedule.objects.all()

        flag = 0
        for item in scheduled:
            if (day == item.day) and (int(start_hour) < int(item.end_hour)) and (int(end_hour) > int(item.start_hour)):
                flag = 1
                break

        if flag == 0:
            arr = []
            arr.append(name)
            arr.append('-')
            arr.append(day)
            arr.append(start_hour)
            arr.append(end_hour)
            add_activity(arr)

        this_schedule = Schedule.objects.all()
        context.update({"this_schedule": this_schedule})

        return HttpResponse(template.render(context, request))
    else:
        form = InputActivity(request.POST)

    return HttpResponse(template.render(context, request))

class Activity:
    def __init__(self, arr):
        self.name = arr[0]
        self.subject_code = arr[1]
        self.day = arr[2]
        self.start_hour = arr[3]
        self.end_hour = arr[4]

class Backtrack:
    def __init__(self):
        self.subject_arr = SubjectsAvailable.objects.all()
        self.schedule_queryset = Schedule.objects.all()
        self.path = []

        for item in self.schedule_queryset:
            self.temp = []
            self.temp.append(item.name)
            self.temp.append(item.subject_code)
            self.temp.append(item.day)
            self.temp.append(item.start_hour)
            self.temp.append(item.end_hour)
            
            self.obj = Activity(self.temp)
            self.path.append(self.obj)

        self.intervals = []
        self.schedule_set = set()
        self.results = []
        self.sks_total = 0
        for item in self.path:
            self.temp = (item.day, item.start_hour, item.end_hour)
            self.intervals.append(self.temp)
            if item.subject_code == '-':
                continue

            self.subject_sks = SubjectsAvailable.objects.get(name=item.name, subject_code=item.subject_code)
            self.sks_total += self.subject_sks.sks
        
    def backtrack(self):
        if self.sks_total > 18:
            if self.path:
                self.path = self.path
                self.path_res = tuple(self.path.copy())
                self.results.append(self.path_res)
            return

        for a in self.subject_arr:
            self.flag = 0

            # Memeriksa apakah mata kuliah sudah diambil atau tidak
            for subj in self.path:
                if a.name == subj.name:
                    self.flag = 1
                    break

            # Memeriksa apakah waktu sudah terpakai atau tidak
            for times in self.intervals:
                if (a.day == times[0]) and (int(a.start_hour) < int(times[2])) and (int(a.end_hour) > int(times[1])):
                    self.flag = 1
                    break

            # Memeriksa apakah kombinasinya sudah ada atau tidak
            self.temp = self.path.copy()
            self.temp.append(a)
            self.temp.sort(key= lambda x: x.name)
            self.temp = tuple(self.temp)
            if self.temp in self.schedule_set:
                self.flag = 1

            if self.flag == 1:
                continue

            self.path.append(a)
            self.intervals.append((a.day, a.start_hour, a.end_hour))
            self.sks_total += a.sks
            self.schedule_set.add(self.temp)

            self.backtrack()

            self.path.pop()
            self.intervals.pop()
            self.sks_total -= a.sks

def result(request):
    bt = Backtrack()
    bt.backtrack()

    template = loader.get_template('result.html')
    arr = []
    if len(bt.results) > 5:
        arr.append(bt.results[0])
        arr.append(bt.results[1])
        arr.append(bt.results[2])
        arr.append(bt.results[3])
        arr.append(bt.results[4])
        context = {"res": arr}
    else:
        context = {"res": bt.results}

    return HttpResponse(template.render(context, request))
