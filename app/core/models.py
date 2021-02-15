from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, email, password=None):
        """Creates and saves a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Tags to be tied to pips"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.PointField(geography=True, default=Point(0.0, 0.0))
    
    def __str__(self):
        return self.name


class Reminder(models.Model):
    """Reminders to be tied to pips"""
    title = models.CharField(max_length=255)
    date = models.DateField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    pip = models.ForeignKey('Pip', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title


class Pip(models.Model):

    CATEGORY_OPTIONS = [
        ('FAMILY', 'FAMILY'),
        ('FRIEND', 'FRIEND'),
        ('COLLEAGUE', 'COLLEAGUE'),
        ('ACQUAINTANCE', 'ACQUAINTANCE'),
        ('POI', 'POI')
    ]

    category = models.CharField(choices=CATEGORY_OPTIONS, max_length=255)
    name = models.CharField(max_length=255)
    date_met = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    location = models.PointField(geography=True, blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    phone = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Note(models.Model):
    """Note to be tied to pips"""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notes_owner",blank=True,null=True, on_delete=models.CASCADE)
    pip = models.ForeignKey('Pip', on_delete=models.SET_NULL, null=True)
    pinned = models.BooleanField(default=False)
    note_title = models.CharField(max_length=400)
    note_content = models.TextField(max_length=20000, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.note_title
