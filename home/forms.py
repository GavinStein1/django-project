from django import forms

class NewPostForm(forms.Form):

    image = forms.ImageField()
    caption = forms.CharField(max_length=240)

class ImageForm(forms.Form):

    image = forms.ImageField()