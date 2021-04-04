from djongo import models
from django.contrib.auth.hashers import make_password
import uuid
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Like_Tags(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.CharField(max_length=100)

    def __str__(self):
        return(self.tag)


class Dislike_Tags(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.CharField(max_length=100)

    def __str__(self):
        return(self.tag)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=200, unique=True)
    url = models.CharField(max_length=200, unique=True)
    email = models.CharField(max_length=100, null=True)
    password = models.CharField(max_length=500)
    like_tags = models.ManyToManyField(Like_Tags)
    dislike_tags = models.ManyToManyField(Dislike_Tags)
    friends = models.ManyToManyField("self", symmetrical=True)

    def __str__(self):
        return(self.username)


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createdTime = models.DateTimeField(auto_now_add=True)
    updatedTime = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100, null=True)
    content = models.CharField(max_length=500, null=True)
    creator = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    # image/s(optional)[One to Many]
    # code(optional)[One to Many]

    def __str__(self):
        return(self.title)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4, editable=False)
    creator = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True)
    parent_post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True)
    createdTime = models.DateTimeField(auto_now_add=True)
    updatedTime = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=500, null=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    def __str__(self):
        return(self.creator.full_name+" : "+self.content[:10])


class Reply(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4, editable=False)
    parent_comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, null=True)
    creator = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True)
    createdTime = models.DateTimeField(auto_now_add=True)
    updatedTime = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=500, null=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    replys = models.ManyToManyField("self", symmetrical=False)

    def __str__(self):
        return(self.creator.full_name+" : "+self.content[:10])
