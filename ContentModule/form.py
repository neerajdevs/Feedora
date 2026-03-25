from django import forms
from .models import Post, Category , Comment

class PostForm(forms.ModelForm):
    category = forms.ChoiceField(choices=[])

    class Meta:
        model = Post
        fields = ["title", "content", "category" ,"status"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.using('mongo').all()
        self.fields['category'].choices = [('', '---------')] + [(str(cat.id), cat.name) for cat in categories]


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