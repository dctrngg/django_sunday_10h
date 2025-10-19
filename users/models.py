from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100, default='Anonymous', blank=True)
    email = models.EmailField(unique=True)
    age = models.IntegerField(default=18, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default.png')

    def __str__(self):
        return self.name
