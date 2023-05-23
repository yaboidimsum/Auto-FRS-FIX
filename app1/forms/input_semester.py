from django import forms

class input_semester(forms.Form):
    user_semester = forms.IntegerField(label='Input')
