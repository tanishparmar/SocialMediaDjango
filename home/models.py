from djongo import models
from django.contrib.auth.hashers import make_password
import uuid
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=200, unique=True)
    url = models.CharField(max_length=200, unique=True)
    email = models.CharField(max_length=100, null=True)
    password = models.CharField(max_length=500)
    friends = models.ManyToManyField("self", symmetrical=False)
    profile_picture = models.ImageField(upload_to="home/static/home/images/profile_pics/",
                              verbose_name='Image',null=True)
    def delete(self, *args, **kwargs):
        self.profile_picture.delete()
        super(User, self).delete(*args, **kwargs)

    def __str__(self):
        return(self.username)


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.CharField(max_length=200, unique=True)
    createdTime = models.DateTimeField(auto_now_add=True)
    updatedTime = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100, null=True)
    content = models.CharField(max_length=500, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True,related_name="creator")
    likers=models.ManyToManyField(User,related_name="likers")
    code=models.TextField(null=True)
    lang=models.CharField(null=True,max_length=10)

    def __str__(self):
        return(self.title)


class Images(models.Model):
    post = models.ForeignKey(Post, default=None,on_delete=models.CASCADE)
    image = models.ImageField(upload_to="home/static/home/images/post_images/",
                              verbose_name='Image')
    def delete(self, *args, **kwargs):
        self.image.delete()
        super(Images, self).delete(*args, **kwargs)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True,related_name="creator_comment")
    parent_post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True,related_name="parent_post")
    createdTime = models.DateTimeField(auto_now_add=True)
    updatedTime = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=500, null=True)
    likers_comment=models.ManyToManyField(User,related_name="likers_comment")
    likes = models.IntegerField(default=0)

    def __str__(self):
        return(self.creator.full_name+" : "+self.content[:10])