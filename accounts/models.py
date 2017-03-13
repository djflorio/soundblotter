from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
import time

class AccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
            
        user = self.model(
            email = self.normalize_email(email),
            username = self.model.normalize_username(username)
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_superuser(self, email, username, password):
        user = self.create_user(
            email,
            username=username,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
    
class Account(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(
        verbose_name='username',
        max_length=100,
        unique=True,
    )
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField(null=True)
    pwreset_key = models.CharField(max_length=40, null=True)
    pwreset = models.BooleanField(default=False)
    pwreset_expires = models.DateTimeField(null=True)
    
    objects = AccountManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def get_full_name(self):
        return self.email
    
    def get_short_name(self):
        return self.email
    
    def __str__(self):
        return self.username
    
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
