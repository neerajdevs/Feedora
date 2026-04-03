from django.urls import path , include
from .views import *

urlpatterns = [
    path('search/', search_posts, name='search'),
    path('feeds/' , feeds , name='Feeds' ),
    path("add/", add_post, name="addPost"),
    path("edit/<slug:slug>/", edit_post, name="EditPost"),
    path("delete/<slug:slug>/", delete_post, name="DeletePost"),
    path("<slug:slug>/", view_post, name="ViewPost"),
    path('comment/add/<uuid:id>/', add_comment, name='add_comment'),
    path('comment/delete/<uuid:id>/', delete_comment, name='delete_comment'),
    path('react/<uuid:id>/', toggle_reaction, name='toggle_reaction'),
    path('post/<slug:slug>/analytics/', post_analytics, name='post_analytics'),
]
