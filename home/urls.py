from django.urls import path
from . import views


urlpatterns = [
    path('', views.home),
    path("logout/", views.logout),
    path("wall/", views.wall),
    path("create/", views.create),
    path("u/<str:user_slug>/",views.user_pages),
    path("p/<str:post_slug>/",views.post_pages),
    path("search/",views.search),
    path("friend/",views.friend),
    path("unfriend/",views.unfriend),
    path("comment/",views.comment),
    path("deletep/",views.deletep),
    path("deletec/",views.deletec),
    path("deleteu/",views.deleteu),
    path("code/",views.code),
    path("code/compile/",views.compileCode),
    path("code/run/",views.runCode),
    path("likep/",views.likep),
    path("likec/",views.likec),
    path("update_dp/",views.update_dp),
    path("edit/",views.edit),
    path("editc/",views.editc),
    path("editu/",views.editu),
]
