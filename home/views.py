from django.shortcuts import render

# Create your views here.

register = True


def home(request):
    global register
    if request.method == "POST":
        register = request.POST.get('register') == "True"
    return render(request, "home/home.html", {"register": register})
