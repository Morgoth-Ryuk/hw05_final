from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Group, Follow
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import PostForm, CommentForm
from .utils import paginator_calculate


User = get_user_model()
QUANTITY_OF_POSTS_ON_PAGE = 10
FEW_QUANTITY_OF_POSTS_ON_PAGE = 2


def index(request):
    """
    Главная страница.
    """
    post_list = Post.objects.order_by('-pub_date')
    page_obj = paginator_calculate(request,
                                   post_list,
                                   QUANTITY_OF_POSTS_ON_PAGE)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def groups(request, slug):
    """
    Посты Группы.
    """
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all().order_by('-pub_date')
    page_obj = paginator_calculate(request,
                                   post_list,
                                   QUANTITY_OF_POSTS_ON_PAGE)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """
    Профиль.
    """
    author = get_object_or_404(User, username=username)
    post_list = author.posts.order_by('-pub_date')
    post_count = post_list.count()
    page_obj = paginator_calculate(request,
                                   post_list,
                                   FEW_QUANTITY_OF_POSTS_ON_PAGE)

    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    template = 'posts/profile.html'
    context = {
        'author': author,
        'post_list': post_list,
        'page_obj': page_obj,
        'post_count': post_count,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """
    Посты автора.
    """
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    post_count = post.author.posts.count()
    author = post.author
    date_of_post = post.pub_date
    comments = post.comments.all
    form = CommentForm(request.POST or None)
    context = {
        'author': author,
        'post_count': post_count,
        'post': post,
        'date_of_post': date_of_post,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """
    Создание поста.
    """
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user.username)
    form = PostForm()
    template = 'posts/create_post.html'
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """
    Редактирование поста.
    """
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    group = post.group
    if post.author == request.user:
        if request.method == 'POST':
            form = PostForm(
                request.POST, files=request.FILES or None, instance=post
            )
            if form.is_valid():
                post = form.save()
                return redirect('posts:post_detail', post_id=post.id)
        else:
            form = PostForm(files=request.FILES or None, instance=post)
            context = {'form': form,
                       'post': post,
                       'group': group,
                       'is_edit': is_edit, }
            return render(request, 'posts/create_post.html', context)
    else:
        return redirect('posts:post_detail', post_id=post.id)
    return redirect('posts:post_detail', post_id=post.id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_calculate(request,
                                   post_list,
                                   QUANTITY_OF_POSTS_ON_PAGE)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    author = User.objects.get(username=username)
    is_follower = Follow.objects.filter(user=user, author=author)
    if user != author and not is_follower.exists():
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username=author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect('posts:profile', username=author)
