from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from likes.models import Like
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

    # Composite index needs to be created in class Meta
    class Meta:
        index_together = (
            ('user', 'created_at'),
        )
        ordering = ('user', 'created_at')


    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')


    # @property
    # def comments(self):
    #     # return Comment.objects.filter(tweet=self)
    #     return self.comment_set.all()
#

    def __str__(self):
        return f'{self.created_at} {self.user}: {self.content}'



