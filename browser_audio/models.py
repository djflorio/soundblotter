from django.db import models
from accounts.models import Account

# Create your models here.
class AudioRecording(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    file_url = models.CharField(max_length=200)
    
    def __str__(self):
        return self.title