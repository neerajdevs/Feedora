from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from ckeditor_uploader.fields import RichTextUploadingField
import uuid
import math
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField

User = get_user_model()

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Categorie'
        


class Post(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author_id = models.IntegerField()
    author_username = models.CharField(max_length=150)
    
    category_id = models.CharField(max_length=255, null=True, blank=True)

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    excerpt = models.TextField(max_length=500, blank=True, null=True) 
    content = RichTextUploadingField()
    cover_image = models.ImageField(upload_to="posts/", blank=True, null=True)
    
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(max_length=500, blank=True, null=True)
    keywords = models.CharField(max_length=255, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    is_featured = models.BooleanField(default=False) 
    is_trending = models.BooleanField(default=False) 
    reading_time = models.PositiveIntegerField(default=0) 

    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)

    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            original_slug = slugify(self.title)
            unique_slug = original_slug
            num = 1
            while Post.objects.using('mongo').filter(slug=unique_slug).exists():
                unique_slug = f'{original_slug}-{num}'
                num += 1
            self.slug = unique_slug
            
        if self.content:
            word_count = len(self.content.split())
            self.reading_time = math.ceil(word_count / 200)
            
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    


class Like(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    REACTION_CHOICES = [(LIKE, 'Like'), (DISLIKE, 'Dislike')]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    user_id = models.IntegerField(null=True, blank=True)  
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES, null=True, blank=True)

    class Meta:
        unique_together = ('post', 'user_id') 

    def __str__(self):
        return f"User ID {self.user_id} - {self.reaction_type} on {self.post}"


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author_id = models.IntegerField(null=True, blank=True)
    author_username = models.CharField(max_length=150, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, 
                                on_delete=models.CASCADE, related_name='replies')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author_id} on {self.post}"

    def is_reply(self):
        return self.parent is not None