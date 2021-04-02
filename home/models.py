from djongo import models

# Create your models here.


class Tag(models.Model):
    tag = models.CharField(max_length=100)

    class Meta:
        abstract = True


class User(models.Model):
    full_name = models.CharField(max_length=200, null=True)
    username = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    securepassw = models.CharField(max_length=500)
    # like_tags = models.ArrayField(Tag, null=True, blank=True)
    # dislike_tags = models.ArrayField(Tag, null=True, blank=True)
    # posts = multiple posts
    # friends = other users

    def __str__(self):
        return(self.username)


class Post(models.Model):
    createdTime = models.DateTimeField(auto_now_add=True)
    updatedTime = models.DateTimeField(auto_now=True)
    # creator = user that created it
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    # Comments(optional)
    # image/s(optional)
    # code(optional)


class Comment(models.Model):
    # creator = user that created it
    createdTime = models.DateTimeField(auto_now_add=True)
    updatedTime = models.DateTimeField(auto_now=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    # Replys=array of comments(optional)
