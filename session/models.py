from django.db import models
from django.contrib.auth.models import AbstractUser
from messagewpp.models import PlaceTrigal

# Create your models here.
class AdminWebUser(AbstractUser):
    place = models.ForeignKey(PlaceTrigal, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=100, blank=False, null=False)

    def __str__(self):
        return f"{self.email} - {self.place}"


class MessageAI(models.Model):
    ask = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.ask + self.answer

    
