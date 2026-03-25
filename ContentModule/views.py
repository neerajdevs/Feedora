from django.shortcuts import render , redirect , get_object_or_404
from .models import Category , Post 
from django.contrib.auth.decorators import login_required
from .form import PostForm ,  CommentForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Comment, Like


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



@login_required
@require_POST
def add_comment(request, id):
    post = get_object_or_404(Post, id=id)
    form = CommentForm(request.POST)
    
    parent_id = request.POST.get('parent_id')  # reply ke liye
    parent = None
    if parent_id:
        parent = get_object_or_404(Comment, id=parent_id)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.parent = parent
        comment.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    comment.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@require_POST
def toggle_reaction(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    reaction_type = request.POST.get('reaction_type')  # 'like' ya 'dislike'

    if reaction_type not in ['like', 'dislike']:
        return JsonResponse({'error': 'Invalid reaction'}, status=400)

    reaction, created = Like.objects.get_or_create(
        post=post, user=request.user,
        defaults={'reaction_type': reaction_type}
    )

    if not created:
        if reaction.reaction_type == reaction_type:
            reaction.delete()  # same reaction dobara click = undo
        else:
            reaction.reaction_type = reaction_type  # like → dislike switch
            reaction.save()

    likes = post.reactions.filter(reaction_type='like').count()
    dislikes = post.reactions.filter(reaction_type='dislike').count()
    user_reaction = None
    try:
        user_reaction = post.reactions.get(user=request.user).reaction_type
    except Like.DoesNotExist:
        pass

    return JsonResponse({
        'likes': likes,
        'dislikes': dislikes,
        'user_reaction': user_reaction
    })
