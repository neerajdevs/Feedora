from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from ckeditor_uploader.fields import RichTextUploadingField
import uuid

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
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author_id = models.IntegerField()
    author_username = models.CharField(max_length=150)
    
    category_id = models.CharField(max_length=255, null=True, blank=True)

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = RichTextUploadingField()
    cover_image = models.ImageField(upload_to="posts/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    


class Like(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    REACTION_CHOICES = [(LIKE, 'Like'), (DISLIKE, 'Dislike')]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES, null=True, blank=True, )
 
    class Meta:
        unique_together = ('post', 'user')  # ek user ek hi reaction de sakta hai

    def __str__(self):
        return f"{self.user} - {self.reaction_type} on {self.post}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, 
                                on_delete=models.CASCADE, related_name='replies')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"

    def is_reply(self):
        return self.parent is not None