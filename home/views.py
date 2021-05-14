from django.conf.urls import url
from django.http.response import Http404, HttpResponse
from django.shortcuts import render
from .models import User, Post, Comment, Images
from django.contrib import auth
from django.contrib import messages
import string
import random
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

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
        source=request.POST["source"]
        lang=request.POST["lang"]
        images=[]
        for i in range(len(request.FILES)):
            images.append(request.FILES["image"+str(i)])
        print(images)
        url = "".join(random.choices(
            string.ascii_uppercase+string.digits, k=10))
        while Post.objects.filter(url=url).exists():
            url = "".join(random.choices(
                string.ascii_letters+string.digits, k=10))
        post = Post.objects.create(
            title=title, content=content, creator=request.user, url=url,code=source,lang=lang)    
        for image in images:
            photo=Images.objects.create(post=post,image=image)
        post.save()
        return redirect("/p/"+post.url)
    return render(request, "home/Create.html", {"title": "Create Post"})


def wall(request):
    your_posts = request.user.creator.all()
    for user in request.user.friends.all():
        your_posts = your_posts | user.creator.all()
    your_posts = your_posts.order_by("-updatedTime")
    if len(your_posts) == 0:
        messages.error(
            request, "You have no posts yet. Create your First Post")
        return redirect("/create")
    return render(request, "home/Wall.html", {"your_posts": your_posts, "title": "Your Wall"})


def view_404(request, *args, **kwargs):
    return render(request, "home/404.html", {"title": "404 Error"})


def user_pages(request, user_slug):
    user = User.objects.get(url=user_slug)
    is_friend = False
    user_posts = user.creator.all()
    followers = 0
    for user_guy in User.objects.all():
        if user in user_guy.friends.all():
            followers += 1
    follows = len(user.friends.all())
    if request.user.is_authenticated:
        if user != request.user:
            friend = True
            if user in request.user.friends.all():
                is_friend = True
            else:
                is_friend = False
        else:
            friend = False
    else:
        friend = False
    return render(request, "home/User.html", {"title": user.username, "this_user": user, "posts": user_posts, "friend": friend, "is_friend": is_friend, "followers": followers, "follows": follows})


def post_pages(request, post_slug):
    try:
        post = Post.objects.get(url=post_slug)
    except Post.DoesNotExist:
        raise Http404()
    if post.code:
        return render(request, "home/Post.html", {"title": "View Post", "post": post,"code_content":post.code,"lang":post.lang})
    else:
        return render(request, "home/Post.html", {"title": "View Post", "post": post})


def search(request):
    q = request.GET["q"]
    if q == "":
        return render(request, "home/Search.html", {"title": "Search", "query": q, "result": {}})
    users = (User.objects.filter(username__iexact=q) | User.objects.filter(first_name__iexact=q) | User.objects.filter(last_name__iexact=q) | User.objects.filter(email__iexact=q) | User.objects.filter(url__iexact=q) | User.objects.filter(
        username__icontains=q) | User.objects.filter(first_name__icontains=q) | User.objects.filter(last_name__icontains=q) | User.objects.filter(email__icontains=q) | User.objects.filter(url__icontains=q)).exclude(username="admin")
    return render(request, "home/Search.html", {"title": "Search", "query": q, "result": users})

@login_required
def friend(request):
    username = request.POST["friend"]
    request.user.friends.add(User.objects.get(username=username))
    return redirect("/u/"+User.objects.get(username=username).url)

@login_required
def unfriend(request):
    username = request.POST["friend"]
    request.user.friends.remove(User.objects.get(username=username))
    return redirect("/u/"+User.objects.get(username=username).url)

@login_required
def comment(request):
    if request.method == "POST":
        content = request.POST["content"]
        post_url = request.POST["post_url"]
        post = Post.objects.get(url=post_url)
        comment = Comment.objects.create(
            creator=request.user, parent_post=post, content=content)
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect("/")

@login_required
def deletep(request):
    post_url = request.POST["post_url"]
    post_user = request.POST["user"]
    if request.user.username == post_user:
        Post.objects.get(url=post_url).delete()
    return redirect("/u/"+request.user.url)

@login_required
def likep(request):
    post_url = request.POST["post_url"]
    this_post = Post.objects.get(url=post_url)
    if request.user not in this_post.likers.all():
        this_post.likers.add(request.user)
    else:
        this_post.likers.remove(request.user)
    return redirect("/p/"+post_url)

@login_required
def likec(request):
    comment_id = request.POST["comment_id"]
    post_user = request.POST["user"]
    this_comment = Comment.objects.get(id=comment_id)
    if User.objects.get(username=post_user) not in this_comment.likers_comment.all():
        this_comment.likers_comment.add(User.objects.get(username=post_user))
        this_comment.likes = len(this_comment.likers_comment.all())
        this_comment.save()
    else:
        this_comment.likers_comment.remove(
            User.objects.get(username=post_user))
        this_comment.likes = len(this_comment.likers_comment.all())
        this_comment.save()
    return redirect("/p/"+this_comment.parent_post.url)

@login_required
def deletec(request):
    comment_id = request.POST["comment_id"]
    comment_user = request.POST["user"]
    parentpost = Comment.objects.get(id=comment_id)
    if comment_user == request.user.username:
        Comment.objects.get(id=comment_id).delete()
    return redirect("/p/"+parentpost.parent_post.url)

@login_required
def deleteu(request):
    delete_user = request.POST["user"]
    delete_user = User.objects.get(username=delete_user)
    if delete_user == request.user:
        auth.logout(request)
        delete_user.delete()
    return redirect("/")

@login_required
def update_dp(request):
    user=request.POST["user"]
    image=request.FILES.get("image")
    this_user=User.objects.get(username=user)
    if user==request.user.username:
        if this_user.profile_picture:
            this_user.profile_picture.delete()
        this_user.profile_picture=image
        this_user.save()
    return redirect("/u/"+this_user.url)

@login_required
def edit(request):
    if request.method == "POST":
        this_user=request.POST["user"]
    else:
        this_user=request.GET["user"]
    if request.user.is_authenticated and request.user.username==this_user:
        if request.method == "POST":
            title = request.POST["title"]
            content = request.POST["content"]
            source=request.POST["source"]
            lang=request.POST["lang"]
            images=[]
            for i in range(len(request.FILES)):
                images.append(request.FILES["image"+str(i)])
            post_url = request.POST["post_url"]
            post = Post.objects.get(url=post_url)
            post.title=title
            post.content=content
            post.code=source
            post.lang=lang
            post.images_set.all().delete()  
            for image in images:
                photo=Images.objects.create(post=post,image=image)
            post.save()
            return redirect("/p/"+post_url)
        else:
            if request.GET:
                post_url=request.GET["post_url"]
                post=Post.objects.get(url=post_url)
                return render(request,"home/Create.html",{"title":"Edit Post","post":post,"code_content":post.code,"lang":post.lang})
            else:
                return redirect("/create/")
    else:
        return redirect("/")

@login_required
def editc(request):
    if request.method == "POST":
        this_user=request.POST["user"]
    else:
        this_user=request.GET["user"]
    if request.user.is_authenticated and request.user.username==this_user:
        if request.method == "POST":
            comment_id=request.POST["comment_id"]
            content=request.POST["content"]
            comment=Comment.objects.get(id=comment_id)
            comment.content=content
            comment.save()
            return redirect("/p/"+comment.parent_post.url)
        else:
            if request.GET:
                comment_id=request.GET["comment_id"]
                comment=Comment.objects.get(id=comment_id)
                return render(request,"home/EditComment.html",{"title":"Edit Post","comment":comment})
            else:
                return redirect("/")
    else:
        return redirect("/")

@login_required
def editu(request):
    if request.method == "POST":
        this_user=request.POST["user"]
    else:
        this_user=request.GET["user"]
    if request.user.is_authenticated and request.user.username==this_user:
        if request.method == "POST":
            this_user=User.objects.get(username=this_user)
            first_name=request.POST["first_name"]
            last_name=request.POST["last_name"]
            username=request.POST["username"]
            email=request.POST["email"]
            password=request.POST["password"]
            confirmPassword=request.POST["confirmPassword"]
            image=request.FILES.get("image")
            if not first_name:
                messages.error(request, "First Name not set. Please try again.")
                return render(request,"home/EditUser.html",{"title":"Edit User","this_user":this_user})
            if not last_name:
                messages.error(request, "Last Name not set. Please try again.")
                return render(request,"home/EditUser.html",{"title":"Edit User","this_user":this_user})
            if not username:
                messages.error(request, "Username not set. Please try again.")
                return render(request,"home/EditUser.html",{"title":"Edit User","this_user":this_user})
            if User.objects.filter(username=username) and username!=this_user.username:
                messages.error(request, "Username already exists. Please try again.")
                return render(request,"home/EditUser.html",{"title":"Edit User","this_user":this_user})
            if not email:
                messages.error(request, "Email not set. Please try again.")
                return render(request,"home/EditUser.html",{"title":"Edit User","this_user":this_user})
            if not password:
                messages.error(request, "Password not set. Please try again.")
                return render(request,"home/EditUser.html",{"title":"Edit User","this_user":this_user})
            if not confirmPassword:
                messages.error(request, "Please fill in the Confirm Password and try again.")
                return render(request,"home/EditUser.html",{"title":"Edit User","this_user":this_user})
            if password!=confirmPassword:
                messages.error(request, "Passwords don't match. Please try again.")
                return render(request,"home/EditUser.html",{"title":"Edit User","this_user":this_user})
            if not image:
                messages.error(request, "Profile Picture not specified. Please try again.")
                return render(request,"home/EditUser.html",{"title":"Edit User","this_user":this_user})
            this_user.first_name=first_name
            this_user.last_name=last_name
            this_user.email=email
            this_user.username=username
            this_user.set_password(password)
            this_user.profile_picture.delete()
            this_user.profile_picture=image
            this_user.save()
            user=auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect("/u/"+this_user.url)
        else:
            if request.GET:
                messages.error(request, "Username Taken. User Not Created.")
                return render(request,"home/EditUser.html",{"title":"Edit User","this_user":User.objects.get(username=this_user)})
            else:
                return redirect("/")
    else:
        return redirect("/")

def code(request):
    return render(request, "home/Code.html", {"title": "Code"})


# Writing the code for executing code
import requests, json, os
from django.http import JsonResponse, HttpResponseForbidden
COMPILE_URL = "https://api.hackerearth.com/v3/code/compile/"
RUN_URL = "https://api.hackerearth.com/v3/code/run/"
CLIENT_SECRET = os.environ['HE_CLIENT_SECRET']
permitted_languages = ["C", "CPP", "CSHARP", "CLOJURE", "CSS", "HASKELL", "JAVA",
                       "JAVASCRIPT", "OBJECTIVEC", "PERL", "PHP", "PYTHON", "R", "RUBY", "RUST", "SCALA"]
"""
Check if source given with the request is empty
"""


def source_empty_check(source):
    if source == "":
        response = {
            "message": "Source can't be empty!",
        }
        return JsonResponse(response, safe=False)


"""
Check if lang given with the request is valid one or not
"""


def lang_valid_check(lang):
    if lang not in permitted_languages:
        response = {
            "message": "Invalid language - not supported!",
        }
        return JsonResponse(response, safe=False)


"""
Handle case when at least one of the keys (lang or source) is absent
"""


def missing_argument_error():
    response = {
        "message": "ArgumentMissingError: insufficient arguments for compilation!",
    }
    return JsonResponse(response, safe=False)


"""
Method catering to AJAX call at /ide/compile/ endpoint,
makes call at HackerEarth's /compile/ endpoint and returns the compile result as a JsonResponse object
"""


def compileCode(request):
    if request.is_ajax():
        try:
            source = request.POST['source']
            # Handle Empty Source Case
            source_empty_check(source)

            lang = request.POST['lang']
            # Handle Invalid Language Case
            lang_valid_check(lang)

        except KeyError:
            # Handle case when at least one of the keys (lang or source) is absent
            missing_argument_error()

        else:
            compile_data = {
                'client_secret': CLIENT_SECRET,
                'async': 0,
                'source': source,
                'lang': lang,
            }

            r = requests.post(COMPILE_URL, data=compile_data)
            return JsonResponse(r.json(), safe=False)
    else:
        return HttpResponseForbidden()


"""
Method catering to AJAX call at /ide/run/ endpoint,
makes call at HackerEarth's /run/ endpoint and returns the run result as a JsonResponse object
"""


def runCode(request):
    if request.is_ajax():
        try:
            source = request.POST['source']
            # Handle Empty Source Case
            source_empty_check(source)

            lang = request.POST['lang']
            # Handle Invalid Language Case
            lang_valid_check(lang)

        except KeyError:
            # Handle case when at least one of the keys (lang or source) is absent
            missing_argument_error()

        else:
            # default value of 5 sec, if not set
            time_limit = request.POST.get('time_limit', 5)
            # default value of 262144KB (256MB), if not set
            memory_limit = request.POST.get('memory_limit', 262144)

            run_data = {
                'client_secret': CLIENT_SECRET,
                'async': 0,
                'source': source,
                'lang': lang,
                'time_limit': time_limit,
                'memory_limit': memory_limit,
            }

            # if input is present in the request
            # code_input = ""
            if 'input' in request.POST:
                run_data['input'] = request.POST['input']
                # code_input = run_data['input']

            """
      Make call to /run/ endpoint of HackerEarth API
      and save code and result in database
      """
            r = requests.post(RUN_URL, data=run_data)
            r = r.json()

            # code_response = codes.objects.create(
            #     code_id=r['code_id'],
            #     code_content=source,
            #     lang=lang
            # )
            # code_response.save()
            return JsonResponse(r, safe=False)
    else:
        return HttpResponseForbidden()
