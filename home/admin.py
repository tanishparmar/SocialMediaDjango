from django.contrib import admin
from .models import User, Post, Comment, Like_Tags, Dislike_Tags, Reply
# Register your models here.

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like_Tags)
admin.site.register(Dislike_Tags)
admin.site.register(Reply)
