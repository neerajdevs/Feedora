from django.shortcuts import render , redirect , get_object_or_404
from .models import Category , Post 
from django.contrib.auth.decorators import login_required
from .form import PostForm ,  CommentForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Comment, Like
from django.db.models import Q
from django.http import JsonResponse # Ise file ke top par zaroor add karein
from django.core.cache import cache 



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
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import render_to_string # Agar snippets use karne ho

def search_posts(request):
    query = request.GET.get('q', '').strip()
    
    if query:
        # Standard ORM search
        posts_list = Post.objects.using('mongo').filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(author_username__icontains=query) |
            Q(keywords__icontains=query)
        ).filter(status='published').order_by('-published_at') # Check karna ki field published_at hai ya created_at
    else:
        posts_list = []

    # 1. FIX: Pagination Add ki (Sirf 10 result ek baar mein)
    paginator = Paginator(posts_list, 10) 
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 2. FIX: AJAX for "Live Search" dropdown (Bina enter dabaye search)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # JSON format mein chhota data bhejenge taaki typing fast ho
        results = []
        for post in page_obj:
            results.append({
                'title': post.title,
                'slug': post.slug, # Link banane ke liye
                'author': post.author_username,
            })
        return JsonResponse({
            'results': results, 
            'has_next': page_obj.has_next()
        })

    # Normal full-page search ke liye
    return render(request, 'search.html', {
        'page_obj': page_obj, # Ab HTML mein 'posts' ki jagah 'page_obj' use karna
        'query': query
    })


@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author_id = request.user.id
            post.author_username = request.user.username
            
            # Cache clear karne ke liye category ka naam save kar lenge
            category_name = None 
            
            if form.cleaned_data.get('category_id'):
                category_obj = form.cleaned_data['category_id']
                post.category_id = str(category_obj.id)
                category_name = category_obj.name # Category ka naam nikal liya
            
            if 'publish' in request.POST:
                post.status = 'published'
            elif 'save_draft' in request.POST:
                post.status = 'draft'
                
            post.save(using='mongo')
            
            # --- REDIS CACHE INVALIDATION LOGIC ---
            # Agar post DB mein 'published' save hui hai, toh purana cache udao!
            if post.status == 'published':
                
                # 1. Main 'All Posts' wala feed cache delete karo
                cache.delete("feed_posts_all")
                print("🧹 Main Feed Cache Cleared!") # Terminal mein check karne ke liye
                
                # 2. Agar kisi specific category mein post daali hai, toh us category ka cache bhi delete karo
                if category_name:
                    cache.delete(f"feed_posts_{category_name}")
                    print(f"🧹 Category '{category_name}' Cache Cleared!")
            # --------------------------------------
            
            return redirect('Dashboard')
    else:
        form = PostForm()
        
    return render(request, 'addPost.html', {'form': form})


@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post.objects.using('mongo'), slug=slug)
    
    # Check if the user is the author
    if post.author_id != request.user.id:
        return redirect('IndexPage')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)
            
            if form.cleaned_data['category_id']:
                updated_post.category_id = str(form.cleaned_data['category_id'].id)
            
            if 'publish' in request.POST:
                updated_post.status = 'published'
            elif 'save_draft' in request.POST:
                updated_post.status = 'draft'
                
            updated_post.save(using='mongo')
            # Naye slug par redirect karo (agar title change hua ho toh)
            return redirect('ViewPost', slug=updated_post.slug) 
    else:
        # Pre-select category in dropdown
        initial_data = {}
        if post.category_id:
            try:
                cat = Category.objects.using('mongo').get(id=post.category_id)
                initial_data['category_id'] = cat
            except Category.DoesNotExist:
                pass
                
        form = PostForm(instance=post, initial=initial_data)
        
    return render(request, 'editPost.html', {'form': form, 'post': post})

@login_required
def delete_post(request, slug):

    post = get_object_or_404(Post, slug=slug)

    if request.user.id == post.author_id :
        post.delete()

    return redirect("Dashboard")



def view_post(request, slug):
    post = get_object_or_404(Post.objects.using('mongo'), slug=slug)
    
    # --- UNIQUE VIEW TRACKING LOGIC ---
    session_key = f'viewed_post_{post.id}'
    
    # Agar is user ke session mein ye key nahi hai, tabhi view count badhao
    if not request.session.get(session_key, False):
        post.view_count += 1
        post.save(using='mongo')
        # Ab session mein yaad rakh lo ki isne dekh liya hai
        request.session[session_key] = True
    
    category_name = None
    if post.category_id:
        try:
            category = Category.objects.using('mongo').get(id=post.category_id)
            category_name = category.name
        except Category.DoesNotExist:
            pass

    likes = post.reactions.using('mongo').filter(reaction_type='like').count()
    dislikes = post.reactions.using('mongo').filter(reaction_type='dislike').count()
    
    user_reaction = None
    if request.user.is_authenticated:
        reaction = post.reactions.using('mongo').filter(user_id=request.user.id).first()
        if reaction:
            user_reaction = reaction.reaction_type

    comments = Comment.objects.using('mongo').filter(post=post).order_by('-created_at')

    return render(request, "viewPost.html", {
        "post": post,
        "category_name": category_name,
        "likes": likes,
        "dislikes": dislikes,
        "user_reaction": user_reaction,
        "comments": comments,
        "comment": comments
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
        comment.author_id = request.user.id
        comment.author_username = request.user.username
        comment.parent = parent
        comment.save()

        # 👇 NAYA AJAX RESPONSE LOGIC 👇
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'username': comment.author_username,
                'body': comment.body,
            })
        # 👆 YAHAN TAK 👆

    # Agar form normal tareeke se submit hua ho (Fallback)
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@require_POST
def delete_comment(request, id):
    comment = get_object_or_404(Comment.objects.using('mongo'), id=id)
    
    # Explicitly Post fetch kar rahe hain
    post = get_object_or_404(Post.objects.using('mongo'), id=comment.post_id)
    
    if request.user.id == comment.author_id:
        comment.delete(using='mongo')
        
    return redirect('ViewPost', slug=post.slug)


@login_required
@require_POST
def toggle_reaction(request, id):
    post = get_object_or_404(Post.objects.using('mongo'), id=id)
    reaction_type = request.POST.get('reaction_type')

    if reaction_type not in ['like', 'dislike']:
        return JsonResponse({'error': 'Invalid reaction'}, status=400)

    existing_reactions = Like.objects.using('mongo').filter(post=post, user_id=request.user.id)
    
    old_reaction_type = None
    if existing_reactions.exists():
        old_reaction_type = existing_reactions.first().reaction_type
        existing_reactions.delete()

    user_reaction = None

    if old_reaction_type != reaction_type:
        Like.objects.using('mongo').create(
            post=post, 
            user_id=request.user.id,
            reaction_type=reaction_type
        )
        user_reaction = reaction_type

    likes = post.reactions.using('mongo').filter(reaction_type='like').count()
    dislikes = post.reactions.using('mongo').filter(reaction_type='dislike').count()

    return JsonResponse({
        'likes': likes,
        'dislikes': dislikes,
        'user_reaction': user_reaction
    })




@login_required
def post_analytics(request, slug):
    # Security: Ensure ki sirf wahi user analytics dekhe jo post ka author hai
    post = get_object_or_404(Post.objects.using('mongo'), slug=slug, author_id=request.user.id)
    
    # Real-time data fetch
    total_likes = Like.objects.using('mongo').filter(post=post, reaction_type='like').count()
    total_dislikes = Like.objects.using('mongo').filter(post=post, reaction_type='dislike').count()
    total_comments = post.comments.count() # Agar related_name='comments' hai toh
    
    # Engagement Rate Calculate karna: ((Likes + Comments) / Views * 100)

    # Engagement Rate Calculate karna (with Dislike Penalty)
    engagement_rate = 0
    if post.view_count > 0:
        # Pura formula: Likes mein se dislikes hatao (agar negative ho jaye toh 0 maan lo)
        net_likes = max(0, total_likes - total_dislikes)
        
        # Ab rate calculate karo
        engagement_rate = round(((net_likes + total_comments) / post.view_count) * 100, 1)

    return render(request, 'post_analytics.html', {
        'post': post,
        'total_likes': total_likes,
        'total_dislikes': total_dislikes,
        'total_comments': total_comments,
        'engagement_rate': engagement_rate
    })
   