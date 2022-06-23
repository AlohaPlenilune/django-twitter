from django.contrib.auth.models import User
from django.db import models
from utils.time_helpers import utc_now

# Create your models here.


class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        help_text='who post this tweet',
        null=True,
    )
    content = models.CharField(max_length=255)
    # CharField max length is 65535。不是一开始就开好，会不断*2。之所以是256 -1，是因为后面有\0表示结束
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

    def __str__(self):
        return f'{self.created_at} {self.user}: {self.content}'



