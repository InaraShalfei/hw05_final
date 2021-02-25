from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .models import Follow, Group, Post
from .forms import CommentForm, PostForm

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.ITEMS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page, "paginator": paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.ITEMS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group,
                                          "page": page, "paginator": paginator})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, settings.ITEMS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    following = request.user.is_authenticated and Follow.objects.filter(author=author, user=request.user).exists()
    return render(request, "profile.html", {"author": author,
                                            "page": page,
                                            "paginator": paginator, "following": following})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm()
    comments = post.comments.all()
    return render(request, "post.html", {"author": post.author,
                                         "post": post,
                                         "form": form,
                                         "comments": comments.all()})


def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect("post", username=username, post_id=post_id)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("post", username=username, post_id=post_id)
    return render(request, "new.html", {"username": username,
                                        "post": post, "form": form})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect("index")
    return render(request, "new.html", {"form": form})


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.method == "POST" and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        form.save()
        return redirect("add_comment",
                        username=username,
                        post_id=post.id)
    return render(request, "post.html", {"author": post.author,
                                         "post": post,
                                         "form": form})


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user).all()
    paginator = Paginator(post_list, settings.ITEMS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html",
                  {"page": page, "paginator": paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(author=author, user=request.user)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(Follow, user=request.user, author__username=username).delete()
    return redirect("profile", username=username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
