from django.http import HttpResponse
from django.template import loader
from django.templatetags.static import static
from django.shortcuts import redirect, render
from django.urls import reverse
from django import forms

from app1.models import SubjectsAvailable, UserSemester, Schedule

import os
import sys

# Class untuk input preferensi subject dari form html
class InputSubjectPref(forms.Form):
    subject_name = forms.CharField(label='Input')
    subject_code = forms.CharField(label='Input')

# Class untuk input preferensi semester dari form html
class InputSemester(forms.Form):
    user_semester = forms.IntegerField(label='Input')

# Class untuk input aktivitas baru dari form html
class InputActivity(forms.Form):
    name = forms.CharField(label='input')
    day = forms.CharField(label='input')
    start_hour = forms.IntegerField(label='input')
    end_hour = forms.IntegerField(label='input')

"""
make_available adalah fungsi untuk menentukan mata kuliah apa yang
dapat diambil untuk semester tertentu. Hal ini bertujuan untuk mempercepat
searching dengan mengecilkan kemungkinan sebelum searching dimulai.
"""
def make_available(input_file, user_semester):
    for line in input_file:
        attribute_array = line.split() # Input berupa file .txt dimana 1 baris adalah satu subject dan informasi subject dipisah dengan whitespace
        if '-' in attribute_array: # Ada baris yang memiliki '-', hal ini bertujuan untuk mempermudah proses penulisan input manual
            continue

        if int(attribute_array[2]) == int(user_semester): # Filter dengan semester yang diinput
            subject = SubjectsAvailable( # SubjectsAvailable merupakan tabel database untuk menyimpan subject yang mungkin untuk sebuah semester
                # Setiap subject di SubjectsAvailable memiliki 10 atribut seperti tertera dibawah.
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
            subject.save() # Memasukkan subject ke dalam database

"""
add_activity adalah fungsi untuk menambah aktivitas maupun subject yang akan dipilih.
"""
def add_activity(attribute_array):
    subject = Schedule( # Schedule merupakan tabel database untuk menyimpan yang sudah dipilih, bukan menyimpan semua kombinasi jadwal
            name=attribute_array[0],
            subject_code=attribute_array[1],
            day=attribute_array[2],
            start_hour=attribute_array[3],
            end_hour=attribute_array[4],
            )
    subject.save()

# Fungsi redirect web dari schedule ke schedule/step1
def home(request):
    return redirect('../schedule/step1/')

"""
input_semester adalah fungsi view yang akan dijalankan apabila url /schedule/step1 diakses
"""
def input_semester(request):
    # Mengambil template html
    template = loader.get_template('input_semester.html')
    context = {}

    # Merefresh database setiap kali memulai input
    SubjectsAvailable.objects.all().delete()

    if request.method == 'POST':
        form = InputSemester(request.POST)
        if form.is_valid():
            # Mengambil input dari user
            user_semester = form.cleaned_data['user_semester']

            # Mengambil file input .txt jadwal dari static untuk diproses
            module_dir = os.path.dirname(__file__)
            file_path = os.path.join(module_dir, 'static/jadwal22-23.txt')
            input_file = open(file_path, 'r')
            
            # Menjalankan make_available dengan input user_semester dari user
            make_available(input_file, user_semester)

            # Merefresh database Schedule agar dapat memulai baru untuk proses input subject selanjutnya
            Schedule.objects.all().delete()

            # Setelah selesai memproses input semester, lanjut ke tahap 2 yaitu input subject yang dipreferensi
            return redirect('../step2/')
        else:
            form = input_semester(request.POST)

    return HttpResponse(template.render(context, request))

"""
input_subject adalah fungsi view yang akan dijalankan apabila url /schedule/step2 diakses
"""
def input_subject(request):
    #  Mengambil template html
    template = loader.get_template('input_subject.html')

    # Web akan memunculkan kemungkinan subject, maka akan diambil nilai distinct dari
    # SubjectsAvailable dan akan dioutputkan di web nantinya
    data = SubjectsAvailable.objects.values('name').distinct()

    # Mem passing kemungkinan subject ke html
    context = {"data": data}

    if request.method == 'POST':
        form = InputSubjectPref(request.POST)
        if form.is_valid():
            # Mengambil input dari user
            subject_name = form.cleaned_data['subject_name']
            subject_code = form.cleaned_data['subject_code']
            
            # Mengambil baris subject yang sesuai dengan yang diinputkan user untuk memeriksa waktunya nanti
            subject = SubjectsAvailable.objects.get(name=subject_name, subject_code=subject_code)

            # Mengambil semua subject yang dimasukkan ke table Schedule
            scheduled = Schedule.objects.all()

            # Memeriksa apakah subject yang akan diinput bertabrakan dengan yang sudah diinput sebelumnya
            flag = 0
            for item in scheduled:
                if (subject.day == item.day) and (int(subject.start_hour) < int(item.end_hour)) and (int(subject.end_hour) > int(item.start_hour)):
                    flag = 1
                    break

            # Memasukkan subject apabila waktu tidak bertabrakan
            if flag == 0:
                arr = []
                arr.append(subject.name)
                arr.append(subject.subject_code)
                arr.append(subject.day)
                arr.append(subject.start_hour)
                arr.append(subject.end_hour)
                add_activity(arr)

            # Mengambil isi tabel Schedule setelah dimasukkan dan mengisi context dengan isi tabel tersebut
            # context akan dipassing ke html untuk ditunjukkan di web
            this_schedule = Schedule.objects.all()
            context.update({"this_schedule": this_schedule})

            return HttpResponse(template.render(context, request))
        else:
            form = InputSubjectPref(request.POST)

    return HttpResponse(template.render(context, request))

def input_activity(request):
    # Mengambil template html
    template = loader.get_template('input_activity.html')
    context = {}

    # Mengambil hasil input sebelumnya untuk dibandingkan waktunya
    this_schedule = Schedule.objects.all()
    context.update({"this_schedule": this_schedule})

    form = InputActivity(request.POST)

    if form.is_valid():
        # Mengambil input aktivitas dari user
        name = form.cleaned_data['name']
        day = form.cleaned_data['day']
        start_hour = form.cleaned_data['start_hour']
        end_hour = form.cleaned_data['end_hour']
        
        scheduled = Schedule.objects.all()

        # Memeriksa apakah waktunya bertabrakan dengan yang sudah diinputkan sebelumnya
        flag = 0
        for item in scheduled:
            if (day == item.day) and (int(start_hour) < int(item.end_hour)) and (int(end_hour) > int(item.start_hour)):
                flag = 1
                break

        # Memasukkan aktivitas apabila waktunya tidak bertabrakan
        if flag == 0:
            arr = []
            arr.append(name)
            arr.append('-')
            arr.append(day)
            arr.append(start_hour)
            arr.append(end_hour)
            add_activity(arr)

        # Mengambil isi tabel Schedule setelah dimasukkan dan mengisi context dengan isi tabel tersebut
        # context akan dipassing ke html untuk ditunjukkan di web
        this_schedule = Schedule.objects.all()
        context.update({"this_schedule": this_schedule})

        return HttpResponse(template.render(context, request))
    else:
        form = InputActivity(request.POST)

    return HttpResponse(template.render(context, request))

"""
Activity adalah kelas yang mendefinisikan aktivitas dan subject yang akan dilakukan searching
"""
class Activity:
    def __init__(self, arr):
        self.name = arr[0]
        self.subject_code = arr[1]
        self.day = arr[2]
        self.start_hour = arr[3]
        self.end_hour = arr[4]

class Backtrack:
    def __init__(self):
        # Mengambil isi dari database yang sudah diisi input sebelumnya
        self.subject_arr = SubjectsAvailable.objects.all()
        self.schedule_queryset = Schedule.objects.all()

        # Mendefiniskan list path yang menjadi list sementara untuk hasil schedulenya
        self.path = []

        # Mengambil isi database Schedule dan memindahkannya ke sebuah list
        # agar dapat diperlakukan seperti list (schedule_queryset berupa queryset bukan list)
        for item in self.schedule_queryset:
            self.temp = []
            self.temp.append(item.name)
            self.temp.append(item.subject_code)
            self.temp.append(item.day)
            self.temp.append(item.start_hour)
            self.temp.append(item.end_hour)
            
            self.obj = Activity(self.temp)
            self.path.append(self.obj)

        # intervals adalah list tuple yang memiliki 3 elemen yaitu hari, jam mulai, dan jam akhir.
        # ketika sebuah aktivitas atau subject dimasukkan ke jadwal, atribut tersebut dari subject
        # dimasukkan ke dalam intervals yang nantinya akan digunakan untuk memeriksa waktu 
        # agar jadwalnya tidak bertabrakan
        self.intervals = []

        # schedule_set berfungsi untuk mencegah kombinasi subject yang sama dimasukkan ke dalam jadwal
        # Misal sudah menelusuri kemungkinan untuk Sistem_Operasi A dan Kecerdasan_Buatan B. Maka
        # apabila dalam path terisi Kecerdasan_Buatan B dan Sistem_Operasi A, searching tidak dilanjutkan
        self.schedule_set = set()

        # results akan menampung semua kemungkinan jadwal
        self.results = []

        # sks_total menghitung jumlah sks dari semua yang dimasukkan sebuah kemungkinan jadwal
        self.sks_total = 0

        for item in self.path:
            # mengambil day, start_hour, dan end_hour dan memasukkannya ke intervals
            self.temp = (item.day, item.start_hour, item.end_hour)
            self.intervals.append(self.temp)
            if item.subject_code == '-':
                continue

            # mengambil nilai sks dan menjumlahkannya ke sks_total
            self.subject_sks = SubjectsAvailable.objects.get(name=item.name, subject_code=item.subject_code)
            self.sks_total += self.subject_sks.sks
        
    def backtrack(self):
        # Ini merupakan  base case dari rekursi. Setelah menemui kondisinya, isi dari path
        # bisa dianggap sebagai jadwal yang komplit sehingga kita masukkan ke dalam variable results
        # dan rekursi akan berakhir
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

            # Setelah diperiksa, maka subject akan dimasukkan. Subject akan dimasukkan ke dalam path,
            # lalu hari, jam mulai dan jam akhirnya akan dimasukkan ke intervasl, total sksnya akan ditambahkan,
            # dan nama subjectnya akan dimasukkan ke schedule_set
            self.path.append(a)
            self.intervals.append((a.day, a.start_hour, a.end_hour))
            self.sks_total += a.sks
            self.schedule_set.add(self.temp)

            # Memanggil rekursi dengan perubahan yang dilakukan
            self.backtrack()

            # Membalikkan perubahan dari sebelumnya, schedule_set tidak dibalikkan karena merupakan set untuk kombinasi subject,
            # bukan set subject. Lebih jelasnya di pendefinisian schedule_set
            self.path.pop()
            self.intervals.pop()
            self.sks_total -= a.sks

"""
result adalah fungsi view yang dipanggil setelah selesai menginput.
diakses dengan url /schedule/result
"""
def result(request):
    bt = Backtrack()
    bt.backtrack()

    template = loader.get_template('result.html')
    arr = []

    # Mengambil 5 output pertama dari yang dihasilkan
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
