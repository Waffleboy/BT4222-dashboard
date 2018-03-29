from django import forms

class replyForm(forms.Form):
	reply = forms.CharField(label = 'reply', max_length = 280, widget=forms.TextInput(attrs={'name': 'reply', 'placeholder': 'Your reply', 'class': 'form-control' }))