# from rest_framework.authtoken import serializers
from notifications.models import Notification
from rest_framework import serializers

class  NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        # user1 followed you(recipient)
        # actor = user1
        # verb = 'followed'

        # user1 liked your tweet tweet1
        # actor = user1
        # target = tweet1
        # verb = 'liked your tweet'
        # 之所以让verb独立出来，可以方便前端不同语言的显示，如：
        # verb = "给你的帖子{target}点了赞"
        # verb = "like your tweet {target}"

        model = Notification
        fields = (
            'id',
            'actor_content_type',
            'actor_object_id',
            'verb',
            'action_object_content_type', # 可以看看文档中对这两个有什么例子，
            'action_object_object_id', # 本app中用不到这俩
            'target_content_type',
            'target_object_id',
            'timestamp',
            'unread',
        )