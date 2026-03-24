from django.urls import path , include
from . import views
urlpatterns = [
    path("profile/<str:username>/" , views.view_profile , name="Profile"),
    path("update/<str:username>/" , views.update_profile , name="UpdateProfile"),
]
