from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from yatube.settings import ITEMS_PER_PAGE

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    posts_total = post_list.count()
    paginator = Paginator(post_list, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'posts_total': posts_total, }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    posts_total = post_list.count()
    paginator = Paginator(post_list, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'group': group, 'page': page, 'posts_total': posts_total, }
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    posts_total = posts.count()
    paginator = Paginator(posts, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_current = paginator.get_page(page_number)
    followers = author.follower.count()
    following = author.following.count()
    follows = None
    if request.user.is_authenticated:
        follows = Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
    return render(
        request,
        'posts/profile.html',
        {'author': author,
         'posts_total': posts_total,
         'username': username,
         'page': page_current,
         'followers': followers,
         'following': following,
         'follows': follows}
    )


def post_view(request, username, post_id):
    post_current = get_object_or_404(
        Post, id=post_id, author__username=username
    )
    author = post_current.author
    posts = author.posts.all()
    posts_total = posts.count()
    followers = author.follower.count()
    following = author.following.count()
    follows = None
    if request.user.is_authenticated:
        follows = Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
    # ШТОА
    form = CommentForm(instance=None)
    comments = Comment.objects.filter(post=post_current)
    context = {
        'author': author,
        'posts_total': posts_total,
        'post_current': post_current,
        'username': username,
        'post_id': post_id,
        'followers': followers,
        'following': following,
        'follows': follows,
        'form': form,
        'comments': comments
    }
    return render(
        request,
        'posts/post.html',
        context
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(
        request,
        'posts/new_post.html',
        {'form': form}
    )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    if post.author != request.user:
        return redirect('post', username, post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    # так в тренажере. уточнить, для чего два раза проверяется POST:
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('post', username, post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post
    }
    return render(
        request,
        'posts/new_post.html',
        # {'form': form,
        #  'is_edit': True,
        #  }
        context
    )


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        # почему commit=False (тут и везде)?
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('post', username, post_id)
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    posts_total = post_list.count()
    paginator = Paginator(post_list, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'follow.html',
        {'page': page, 'posts_total': posts_total, }
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.filter(author=author, user=request.user).delete()
    return redirect('profile', username)


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
