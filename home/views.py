from django.shortcuts import render
from .models import User
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
                        return render(request, "home/home.html", {"register": register})
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
        return render(request, "home/home.html", {"register": register})


def logout(request):
    auth.logout(request)
    return redirect("/")


def wall(request):
    return render(request, "home/wall.html")
