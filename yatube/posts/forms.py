from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """
    Форма создания поста
    """
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(forms.ModelForm):
    """
    Форма создания  комментария
    """
    class Meta:
        model = Comment
        fields = ('text',)
