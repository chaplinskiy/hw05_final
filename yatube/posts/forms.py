from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)
        labels = {
            'text': 'Текст',
            'group': 'Группа',
            'image': 'Изображение'
        }
        help_texts = {
            'text': 'Обязательно',
            'group': 'Необязательно',
            'image': 'Необязательно',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст',
        }
        help_texts = {
            'text': 'Обязательно (раз уж взялись комментировать)'
        }
