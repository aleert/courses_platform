from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    pass


class Profile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    about_myself = models.TextField(blank=True, default='')
    date_of_birth = models.DateField(null=True, blank=True)



