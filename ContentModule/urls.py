from django.urls import path , include
from .views import *

urlpatterns = [
    path('feeds/' , feeds , name='Feeds' ),
    path("add/", add_post, name="addPost"),
    path("edit/<slug:slug>/", edit_post, name="EditPost"),
    path("delete/<slug:slug>/", delete_post, name="DeletePost"),
    path("<slug:slug>/", view_post, name="ViewPost"),
    path('add/<int:id>/', add_comment, name='add_comment'),
    path('delete/<int:id>/', delete_comment, name='delete_comment'),
    path('react/<int:id>/', toggle_reaction, name='toggle_reaction'),
]
