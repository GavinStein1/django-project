from django import forms


class NewPostForm(forms.Form):
    image = forms.ImageField()
    caption = forms.CharField(max_length=240, required=False)


class ImageForm(forms.Form):
    image = forms.ImageField()


class EditProfileForm(forms.Form):

    def __init__(self, choices, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['posts'].choices = choices
    profile_pic = forms.ImageField(required=False)
    bio = forms.CharField(max_length=240, required=False)
    posts = forms.MultipleChoiceField(choices=(), widget=forms.CheckboxSelectMultiple, required=False)
