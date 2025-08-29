from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    content = models.CharField(max_length=256)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ID {self.id}: {self.content[:16]}... Posted By {self.author.username} At {self.get_date()}"

    def get_date(self):
        return self.date.strftime("%b %d, %Y")

    def serialize(self):
        return {
            "id": self.id,
            "author": self.author.username,
            "content": self.content,
            "date": self.get_date()
        }

    get_date.short_description = "Date Posted"


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    following = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="following")


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ul")
    liked = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True, related_name="liked")
