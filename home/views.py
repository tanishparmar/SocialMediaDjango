from django.shortcuts import render
from .models import User, Post
from django.contrib import auth
from django.contrib import messages
import string
import random
from django.shortcuts import redirect

# Create your views here.

register = True


def home(request):
    if request.user.is_authenticated:
        return redirect("/wall")
    else:
        global register
        if request.method == "POST":
            if "Change" in request.POST:
                register = request.POST.get('register') == "True"
            elif "Register" in request.POST:
                first_name = request.POST["first_name"]
                last_name = request.POST["last_name"]
                email = request.POST["email"]
                username = request.POST["username"]
                password = request.POST["password"]
                confirmPassword = request.POST["confirmPassword"]
                if password == confirmPassword:
                    if User.objects.filter(username=username).exists():
                        messages.error(
                            request, "Username Taken. User Not Created.")
                    elif User.objects.filter(email=email).exists():
                        messages.error(
                            request, "Email Already Exists. User Not Created.")
                    else:
                        url = "".join(random.choices(
                            string.ascii_uppercase+string.digits, k=10))
                        while User.objects.filter(url=url).exists():
                            url = "".join(random.choices(
                                string.ascii_letters+string.digits, k=10))
                        user = User.objects.create(
                            first_name=first_name, last_name=last_name, email=email, username=username, url=url)
                        user.set_password(password)
                        user.save()
                        register = False
                        return render(request, "home/Home.html", {"register": register, "title": "Home"})
                else:
                    messages.error(
                        request, "Passwords don't match. User Not Created.")
            elif "Signin" in request.POST:
                username = request.POST["username"]
                password = request.POST["password"]
                user = auth.authenticate(username=username, password=password)
                if user is not None:
                    auth.login(request, user)
                    return redirect("/wall")
                else:
                    messages.error(request, "Invalid Credentials.")
        return render(request, "home/Home.html", {"register": register, "title": "Home"})


def logout(request):
    auth.logout(request)
    return redirect("/")


def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        url = "".join(random.choices(
            string.ascii_uppercase+string.digits, k=10))
        while Post.objects.filter(url=url).exists():
            url = "".join(random.choices(
                string.ascii_letters+string.digits, k=10))
        post = Post.objects.create(
            title=title, content=content, creator=request.user, url=url)
        return redirect("/wall")
    return render(request, "home/Create.html", {"title": "Create Post"})


def wall(request):
    your_posts = request.user.post_set.all()
    for user in request.user.friends.all():
        your_posts=your_posts|user.post_set.all()
    your_posts=your_posts.order_by("-updatedTime")
    if len(your_posts) == 0:
        messages.error(
            request, "You have no posts yet. Create your First Post")
        return redirect("/create")
    return render(request, "home/Wall.html", {"your_posts": your_posts, "title": "Your Wall"})


def view_404(request, *args, **kwargs):
    return render(request, "home/404.html", {"title": "404 Error"})


def user_pages(request, user_slug):
    user = User.objects.get(url=user_slug)
    is_friend=False
    if user != request.user:
        friend=True
        if user in request.user.friends.all() :
            is_friend=True
        else:
            is_friend=False
    else:
        friend=False
    user_posts = user.post_set.all()
    followers=0
    for user_guy in User.objects.all():
        if user in user_guy.friends.all():
            followers+=1
    follows=len(user.friends.all())
    return render(request, "home/User.html", {"title":user.username,"this_user": user, "posts": user_posts,"friend":friend,"is_friend":is_friend,"followers":followers,"follows":follows})


def post_pages(request, post_slug):
    post = Post.objects.get(url=post_slug)
    return render(request, "home/Post.html", {"title":post.title[:10], "post": post})

def search(request):
    q = request.GET["q"]
    users = User.objects.filter(username__iexact=q) | User.objects.filter(first_name__iexact=q) | User.objects.filter(last_name__iexact=q) | User.objects.filter(email__iexact=q) | User.objects.filter(url__iexact=q) | User.objects.filter(
        username__icontains=q) | User.objects.filter(first_name__icontains=q) | User.objects.filter(last_name__icontains=q) | User.objects.filter(email__icontains=q) | User.objects.filter(url__icontains=q)
    return render(request, "home/Search.html", {"title": "Search", "query": q, "result": users})

def friend(request):
    username=request.POST["friend"]
    request.user.friends.add(User.objects.get(username=username))
    return redirect("/u/"+User.objects.get(username=username).url)

def unfriend(request):
    username=request.POST["friend"]
    request.user.friends.remove(User.objects.get(username=username))
    return redirect("/u/"+User.objects.get(username=username).url)