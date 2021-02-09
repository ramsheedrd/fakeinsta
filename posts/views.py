from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import PostAddForm
from .models import Post, Like

# Create your views here.


@login_required
def home_view(request):
    posts = Post.objects.all().prefetch_related("post_likes").select_related("user")
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


def like_toggle(request, post_id):
    post = Post.objects.get(id=post_id)
    user = request.user

    try:
        already_liked = Like.objects.get(post=post, user=user)
        already_liked.delete()
    except Like.DoesNotExist:
        Like.objects.create(post=post, user=user)

    return redirect("posts:home")
