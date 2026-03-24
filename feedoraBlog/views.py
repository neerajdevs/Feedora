from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from ContentModule.models import *
from AuthModule.models import *

def index(request):

    return render(request , 'index.html')

User = get_user_model()

def user_dashboard(request):
    user_id = request.user.id
    user = get_object_or_404(User, id=user_id)
    posts = Post.objects.using('mongo').filter(author_id=user_id)
    
    return render(request, 'User_dashboard.html', {
        'user_profile': user,
        'posts': posts
    })



