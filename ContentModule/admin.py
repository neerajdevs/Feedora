from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title")

    # disable heavy filters
    list_filter = ()





@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ( 'id' , 'body', 'created_at')
    search_fields = ('author_username', 'body')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        obj.save(using='mongo')

    def delete_model(self, request, obj):
        obj.delete(using='mongo')

    def get_queryset(self, request):
        return super().get_queryset(request).using('mongo')