from django.urls import path , include
from .views import *
urlpatterns = [
    path('feeds/' , feeds , name='Feeds' ),
    path("add/", add_post, name="addPost"),
    path("edit/<slug:slug>/", edit_post, name="EditPost"),
    path("delete/<slug:slug>/", delete_post, name="DeletePost"),
    path("<slug:slug>/", view_post, name="ViewPost"),
]
