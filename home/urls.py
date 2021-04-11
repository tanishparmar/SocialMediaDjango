from django.urls import path
from . import views


urlpatterns = [
    path('', views.home),
    path("logout/", views.logout),
    path("wall", views.wall),
    path("create/", views.create),
    path("u/<str:user_slug>/",views.user_pages),
    path("p/<str:post_slug>/",views.post_pages),
    path("search",views.search)
]
