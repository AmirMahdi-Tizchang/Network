import json
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Follow, Like


def index(request):
    posts = Post.objects.order_by('-date')
    page_number = request.GET.get("page", 1)
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "page_obj": page_obj
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            next_url = request.POST.get("next", request.GET.get("next", reverse("index")))
            return redirect(next_url)
        else:
            return render(request, "network/login.html", {
                "alert": True,
                "banner": "Denied",
                "status": "danger",
                "message": "Invalid username and/or password."
            })
    else:
        next_url = request.GET.get("next", "")
        return render(request, "network/login.html", {"next": next_url})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if not (username and password and email and confirmation):
            return render(request, "network/register.html", {
                "alert": True,
                "banner": "Missing inputs",
                "status": "danger",
                "message": "all inputs field must be provided!"
            })

        if password != confirmation:
            return render(request, "network/register.html", {
                "alert": True,
                "banner": "Error",
                "status": "danger",
                "message": "passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            Follow.objects.create(user=user)
        except IntegrityError:
            return render(request, "network/register.html", {
                "alert": True,
                "banner": "Username already taken",
                "status": "warning",
                "message": "try another again."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def new(request):
    if request.method == "POST":
        try:
            Post.objects.create(author=request.user, content=request.POST["content"])
        except:
            return render(request, "network/index.html", {
                "alert": True,
                "banner": "Oops",
                "status": "danger",
                "message": "something went wrong!"
            })
    return HttpResponseRedirect(reverse("index"))


def user(request, tag):
    try:
        user = User.objects.filter(username=tag).first()
        posts = Post.objects.filter(author=user).order_by('-date')
        page_number = request.GET.get("page", 1)
        paginator = Paginator(posts, 10)
        page_obj = paginator.get_page(page_number)
        following = Follow.objects.filter(user=user).exclude(following__isnull=True).count()
        follower = Follow.objects.filter(following=user).count()
        followed = Follow.objects.filter(user=request.user, following=user).exists() if request.user.is_authenticated else False

        return render(request, "network/profile.html", {
            "existence": True,
            "followed": followed,
            "username": tag,
            "following": following,
            "follower": follower,
            "post_count": posts.count(),
            "page_obj": page_obj
        })

    except:
        return render(request, "network/profile.html", {
            "alert": True,
            "banner": "404",
            "status": "warning",
            "message": "user doesn't exist!",
            "username": tag
        })


@login_required
def follow(request):
    if request.method == 'POST':
        try:
            username = User.objects.get(username=request.POST["username"])
        except User.DoesNotExist:
            return user(request, request.POST["username"])

        followed = Follow.objects.filter(user=request.user, following=username)

        if followed.exists():
            followed.delete()
            return user(request, request.POST["username"])
        else:
            Follow.objects.create(user=request.user, following=username)
            return user(request, request.POST["username"])


@login_required
def following(request):
    try:
        following_user = Follow.objects.filter(user=request.user).values_list('following', flat=True)
        posts = Post.objects.filter(author__in=following_user).order_by('-date')

        # Get page number from query parameters
        page_number = request.GET.get("page", 1)
        paginator = Paginator(posts, 10)
        page_obj = paginator.get_page(page_number)

        return render(request, "network/following.html", {
            "page_obj": page_obj
        })
    except:
        return HttpResponseRedirect(reverse("index"))


@csrf_exempt
@login_required
def edit(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            post_id = data.get("id")
            content = data.get("content")

            post = Post.objects.filter(id=post_id).first()

            if not post or post.author != request.user:
                raise PermissionDenied("No right to edit")

            post.content = content
            post.save()
            return JsonResponse({"message": "Post updated successfully!"})

        except PermissionDenied as e:
            return JsonResponse({"error": str(e)}, status=403)
        except Exception as e:
            return JsonResponse({"error": "Unexpected error"}, status=500)


@csrf_exempt
@login_required
def like(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            id = data.get("id")
            post = Post.objects.get(id=id)

            existing_like = Like.objects.filter(user=request.user, liked=post)
            if existing_like.exists():
                existing_like.delete()
            else:
                Like.objects.create(user=request.user, liked=post)

            like_count = Like.objects.filter(liked=post).count()
            return JsonResponse({"success": True, "likes": like_count})
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
