from django import forms
from .models import Post, Category , Comment


class PostForm(forms.ModelForm):
    category_id = forms.ModelChoiceField(
        queryset=Category.objects.using('mongo').all(),
        empty_label="Select a Category",
        required=False
    )

    class Meta:
        model = Post
        fields = ['title', 'category_id', 'excerpt', 'cover_image', 'content', 'meta_title', 'meta_description', 'keywords']
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a short summary...'}),
            'meta_description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Search engine description...'}),
            'keywords': forms.TextInput(attrs={'placeholder': 'django, python, web development'}),
        }
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Apna comment likho...',
                'class': 'form-control'
            })
        }
        labels = {'body': ''}