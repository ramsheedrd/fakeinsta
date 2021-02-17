from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import HttpResponse, redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .forms import PostAddForm
from .models import Comment, Like, Post

# Create your views here.


@login_required
def home_view(request):
    posts = Post.objects.all().prefetch_related("post_likes", 'post_comments', 'post_comments__user').select_related("user")
    likes = Like.objects.filter(post__in=posts, user=request.user).values_list("post", flat=True)

    def is_liked_add(p):
        p.is_liked = p.id in likes
        return p

    posts = list(map(is_liked_add, posts))
    return render(request, "posts/home.html", {"posts": posts})


@login_required
def add_post(request):
    if request.method == "POST":
        form = PostAddForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "successful")
            return redirect("posts:home")
        else:
            return render(request, "posts/add_post.html", {"form": form})
    else:

        form = PostAddForm()
        return render(request, "posts/add_post.html", {"form": form})


@login_required
def like_toggle(request, post_id):
    post = get_object_or_404(Post, id = post_id)
    user = request.user
    response = {}
    try:
        already_liked = Like.objects.get(post=post, user=user)
        already_liked.delete()
        response['status'] = 'dislike'
    except Like.DoesNotExist:
        Like.objects.create(post=post, user=user)
        response['status'] = 'like'

    response['count'] = Like.objects.filter(post=post).count()

    return JsonResponse(response)


@login_required
@csrf_exempt
def add_comment(request):
    post_id = request.POST.get('post_id')
    comment = request.POST.get('comment')

    post = get_object_or_404(Post, id = post_id)
    user = request.user

    Comment.objects.create(user=user, post=post, comment=comment)
    return JsonResponse({'user':user.first_name, 'comment':comment})


@login_required
def delete_post(request, post_id, next):
    post = get_object_or_404(Post, id = post_id)
    if request.user == post.user:
        post.delete()
        return redirect(next)
    else:
        return HttpResponseNotFound()

