from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Post, UserProfile

class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Post
        fields = ['title', 'content', 'category']

from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class RegistrationForm(forms.Form):
    email = forms.EmailField()

class LoginForm(forms.Form):
    email = forms.EmailField()


class EmailForm(forms.Form):
    subject = forms.CharField(label='Тема', max_length=100)
    message = forms.CharField(label='Сообщение', widget=forms.Textarea)
