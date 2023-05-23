from django import forms

class InputActivity(forms.Form):
    subject_name = forms.CharField(label='Input')
    subject_code = forms.CharField(label='Input')

class InputSemester(forms.Form):
    user_semester = forms.IntegerField(label='Input')
