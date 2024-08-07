from django.db import models
from users.models import CustomUser
# Create your models here.
class InstaLink(models.Model):
    url = models.CharField(max_length=255)
    is_valid = models.BooleanField(default=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.user.username)