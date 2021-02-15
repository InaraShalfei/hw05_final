from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Group
from .forms import CommentForm, PostForm

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page, "paginator": paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page, "paginator": paginator})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "profile.html", {"author": user,
                                            "page": page, "paginator": paginator})


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=user)
    form = CommentForm()
    return render(request, "post.html", {"author": user,
                                         "post": post,
                                         "form": form})


def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect("post", username=username, post_id=post_id)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("post", username=username, post_id=post_id)
    return render(request, "new.html", {"username": username,
                                        "post": post, "form": form})


@login_required
def new_post(request):
    form = PostForm(request.POST or None,  files=request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect("index")
    return render(request, "new.html", {"form": form})


def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.method == "POST":
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            form.save()
            return redirect("add_comment", username=username, post_id=post.id)
    return render(request, "post.html", {"author": post.author,
                                         "post": post,
                                         "form": form})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
