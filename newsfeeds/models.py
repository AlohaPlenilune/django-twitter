from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from tweets.models import Tweet


class NewsFeed(models.Model):
    # user represents who can see this tweet rather than who post this tweet.
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    # the order in the NewsFeed model should not depend on other models,
    # so we need created_at
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        unique_together = (('user', 'tweet'),)
        ordering = ( '-created_at',)

    def __str__(self):
        return f'{self.created_at} inbox of {self.user}: {self.tweet}'
