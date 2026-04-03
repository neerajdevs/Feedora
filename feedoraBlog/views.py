from django.shortcuts import render, get_object_or_404 
from django.contrib.auth import get_user_model
from ContentModule.models import *
from AuthModule.models import *
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.core.cache import cache # Redis cache import kiya
from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string


def index(request):
    category_name = request.GET.get('category')
    
    # 1. Cache Key banayein (Har category ka alag cache hona chahiye)
    cache_key = f"feed_posts_{category_name}" if category_name else "feed_posts_all"
    
    # 2. Redis se pucho: "Kya tumhare paas ye data pehle se hai?"
    cached_posts = cache.get(cache_key)
    
    if cached_posts is not None:
        # Agar RAM (Redis) mein data mil gaya, toh DB query bacha li!
        posts = cached_posts
        print("Data Redis (Cache) se aaya hai! 🚀") # Terminal mein check karne ke liye
    
    else:
        # Agar Cache mein nahi hai, toh Database (MongoDB) se laao
        print("Data MongoDB (Database) se aaya hai! 🐢")
        
        posts = Post.objects.using('mongo').filter(status='published').order_by('-published_at')
        if category_name:
            try:
                active_category = Category.objects.using('mongo').get(name=category_name)
                posts = posts.filter(category_id=str(active_category.id))
            except Category.DoesNotExist:
                pass
        
        # Database query ko evaluate karne ke liye list() mein convert karein
        posts = list(posts)
        
        # 3. Agli baar ke liye is data ko Redis mein save (set) kar do
        # 60 * 15 = 900 seconds (15 minutes tak cache rahega)
        cache.set(cache_key, posts, timeout=60 * 15)

    categories = Category.objects.using('mongo').all()
    top_posts = Post.objects.using('mongo').filter(status='published').order_by('-view_count')[:3]
    posts_list = Post.objects.using('mongo').filter(status='published').order_by('-published_at')
    paginator = Paginator(posts_list, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # --- NAYA AJAX LOGIC ---
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Nayi posts ko snippet mein daal kar HTML string bana lo
        html = render_to_string('feed_posts_snippet.html', {'page_obj': page_obj})
        
        # JSON mein HTML aur ye batao ki aage aur posts hain ya nahi
        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next()
        })
    # ------------------------

    return render(request, 'index.html', {
        'posts': posts,
        'category': categories,
        'top_posts': top_posts,
        'active_category': category_name,
        "page_obj": page_obj
    })


User = get_user_model()



# Number format karne ka helper (1200 -> 1.2k)
def format_count(num):
    if not num:
        return "0"
    if num >= 1000000:
        return f"{num / 1000000:.1f}M"
    elif num >= 1000:
        return f"{num / 1000:.1f}k"
    return str(num)

@login_required
def user_dashboard(request):
    user_id = request.user.id
    user = get_object_or_404(User, id=user_id)
    
    # 1. Get all posts by this user
    posts = Post.objects.using('mongo').filter(author_id=user_id).order_by('-created_at')
    post_count = posts.count()
    
    # 2. Total Views (Python loop fallback for safety with MongoDB)
    total_views = 0
    for post in posts:
        total_views += post.view_count or 0

    # NAYA: Total Dislikes
    total_dislikes = Like.objects.using('mongo').filter(
        post__author_id=user_id, 
        reaction_type='dislike'
    ).count()

    # 3. SMART APPROACH: Total Likes directly from Like model
    # Logic: Un sabhi likes ko count karo jinki post ka author ye user hai, aur reaction 'like' hai.
    total_likes = Like.objects.using('mongo').filter(
        post__author_id=user_id, 
        reaction_type='like'
    ).count()

    return render(request, 'User_dashboard.html', {
        'user_profile': user,
        'posts': posts,
        'post_count': post_count,
        'total_views': format_count(total_views),
        'total_likes': format_count(total_likes),
        'total_dislikes': format_count(total_dislikes),
    })