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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")


class Comment(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    content = models.TextField()

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:30]