from django.conf.urls import url
from django.http.response import Http404, HttpResponse
from django.shortcuts import render
from .models import User, Post, Comment, Images
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
        images = request.FILES.getlist("images")
        url = "".join(random.choices(
            string.ascii_uppercase+string.digits, k=10))
        while Post.objects.filter(url=url).exists():
            url = "".join(random.choices(
                string.ascii_letters+string.digits, k=10))
        post = Post.objects.create(
            title=title, content=content, creator=request.user, url=url)    
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
    return render(request, "home/Post.html", {"title": post.title[:10], "post": post})


def search(request):
    q = request.GET["q"]
    if q == "":
        return render(request, "home/Search.html", {"title": "Search", "query": q, "result": {}})
    users = (User.objects.filter(username__iexact=q) | User.objects.filter(first_name__iexact=q) | User.objects.filter(last_name__iexact=q) | User.objects.filter(email__iexact=q) | User.objects.filter(url__iexact=q) | User.objects.filter(
        username__icontains=q) | User.objects.filter(first_name__icontains=q) | User.objects.filter(last_name__icontains=q) | User.objects.filter(email__icontains=q) | User.objects.filter(url__icontains=q)).exclude(username="admin")
    return render(request, "home/Search.html", {"title": "Search", "query": q, "result": users})


def friend(request):
    username = request.POST["friend"]
    request.user.friends.add(User.objects.get(username=username))
    return redirect("/u/"+User.objects.get(username=username).url)


def unfriend(request):
    username = request.POST["friend"]
    request.user.friends.remove(User.objects.get(username=username))
    return redirect("/u/"+User.objects.get(username=username).url)


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


def deletep(request):
    post_url = request.POST["post_url"]
    post_user = request.POST["user"]
    if request.user.username == post_user:
        Post.objects.get(url=post_url).delete()
    return redirect("/u/"+request.user.url)


def likep(request):
    post_url = request.POST["post_url"]
    this_post = Post.objects.get(url=post_url)
    if request.user not in this_post.likers.all():
        this_post.likers.add(request.user)
    else:
        this_post.likers.remove(request.user)
    return redirect("/p/"+post_url)


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


def deletec(request):
    comment_id = request.POST["comment_id"]
    comment_user = request.POST["user"]
    parentpost = Comment.objects.get(id=comment_id)
    if comment_user == request.user.username:
        Comment.objects.get(id=comment_id).delete()
    return redirect("/p/"+parentpost.parent_post.url)


def deleteu(request):
    delete_user = request.POST["user"]
    delete_user = User.objects.get(username=delete_user)
    if delete_user == request.user:
        auth.logout(request)
        delete_user.delete()
    return redirect("/")

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

def edit(request):
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        images = request.FILES.getlist("images")
        post_url = request.POST["post_url"]
        post = Post.objects.get(url=post_url)
        post.title=title
        post.content=content
        post.images_set.all().delete()  
        for image in images:
            photo=Images.objects.create(post=post,image=image)
        post.save()
        return redirect("/p/"+post_url)
    else:
        if request.GET:
            this_user=request.GET["user"]
            post_url=request.GET["post_url"]
            post=Post.objects.get(url=post_url)
            if request.user.username==this_user:
                return render(request,"home/Create.html",{"title":"Edit Post","post":post})
            else:
                return redirect("/create/")
        else:
            return redirect("/create/")

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
            code_input = ""
            if 'input' in request.POST:
                run_data['input'] = request.POST['input']
                code_input = run_data['input']

            """
      Make call to /run/ endpoint of HackerEarth API
      and save code and result in database
      """
            r = requests.post(RUN_URL, data=run_data)
            r = r.json()
            cs = ""
            rss = ""
            rst = ""
            rsm = ""
            rso = ""
            rsstdr = ""
            try:
                cs = r['compile_status']
            except:
                pass
            try:
                rss = r['run_status']['status']
            except:
                pass
            try:
                rst = r['run_status']['time_used']
            except:
                pass
            try:
                rsm = r['run_status']['memory_used']
            except:
                pass
            try:
                rso = r['run_status']['output_html']
            except:
                pass
            try:
                rsstdr = r['run_status']['stderr']
            except:
                pass

            # code_response = codes.objects.create(
            #     code_id=r['code_id'],
            #     code_content=source,
            #     lang=lang,
            #     code_input=code_input,
            #     compile_status=cs,
            #     run_status_status=rss,
            #     run_status_time=rst,
            #     run_status_memory=rsm,
            #     run_status_output=rso,
            #     run_status_stderr=rsstdr
            # )
            # code_response.save()
            return JsonResponse(r, safe=False)
    else:
        return HttpResponseForbidden()
