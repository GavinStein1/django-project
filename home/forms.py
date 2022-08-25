from django import forms

from .models import Post, Comment


class NewPostForm(forms.Form):
    image = forms.ImageField()
    caption = forms.CharField(max_length=240, required=False)


class ImageForm(forms.Form):
    image = forms.ImageField()


class ModelPostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['image', 'caption']


class EditProfileForm(forms.Form):

    def __init__(self, choices, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['posts'].choices = choices
    profile_pic = forms.ImageField(required=False)
    bio = forms.CharField(max_length=240, required=False)
    posts = forms.MultipleChoiceField(choices=(), widget=forms.CheckboxSelectMultiple, required=False)


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text']

