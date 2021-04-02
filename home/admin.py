from django.contrib import admin
from .models import User, Post, Comment
# Register your models here.
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
