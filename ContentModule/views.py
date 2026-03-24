from django.shortcuts import render , redirect , get_object_or_404
from .models import Category , Post 
from django.contrib.auth.decorators import login_required
from .form import PostForm

def category_list(request):
    categories = Category.objects.all().order_by("-created_at")

    return render(request, "category_list.html", {
        "categories": categories
    })

def feeds(request):
    post = Post.objects.all()
    category = Category.objects.all()
    print(category)
    return render(request , "feeds.html" ,  {post : 'posts' , "category": category})

@login_required
def add_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            
            post.author_id = request.user.id
            post.author_username = request.user.username
            
            category_id = form.cleaned_data.get("category")
            if category_id:
                post.category = Category.objects.using("mongo").get(id=category_id)
            
            if 'save_draft' in request.POST:
                post.status = 'draft'
            elif 'publish' in request.POST:
                post.status = 'published'
                
            post.save(using="mongo") 

            return redirect("Dashboard")
    else:
        form = PostForm()

    return render(request, "addPost.html", {
        "form": form
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Category

@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post.objects.using('mongo'), slug=slug)

    if request.user.id != post.author_id:
        return redirect("Dashboard")

    categories = Category.objects.using('mongo').all()

    if request.method == "POST":
        post.title = request.POST.get("title")
        post.content = request.POST.get("content")
        post.category_id = request.POST.get("category")
        
        if 'save_draft' in request.POST:
            post.status = 'draft'
        elif 'publish' in request.POST:
            post.status = 'published'

        post.save(using='mongo')
        
        return redirect("ViewPost", slug=post.slug)

    return render(request, "editPost.html", {
        "post": post,
        "categories": categories
    })

@login_required
def delete_post(request, slug):

    post = get_object_or_404(Post, slug=slug)

    if request.user.id == post.author_id :
        post.delete()

    return redirect("Dashboard")


def view_post(request, slug):
    post = get_object_or_404(Post.objects.using('mongo'), slug=slug)
    
    post.view_count += 1
    post.save(using='mongo')
    
    category_name = None
    if post.category_id:
        try:
            category = Category.objects.using('mongo').get(id=post.category_id)
            category_name = category.name
        except Category.DoesNotExist:
            pass

    return render(request, "viewPost.html", {
        "post": post,
        "category_name": category_name
    })

    

