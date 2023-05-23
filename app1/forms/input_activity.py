from django import forms

class input_activity(forms.Form):
    subject_name = forms.CharField(label='Input')
    subject_code = forms.CharField(label='Input')
