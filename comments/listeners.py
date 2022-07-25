from utils.listeners import invalidate_object_cache

def incr_comments_count(sender, instance, created, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return

    # handle new comment
    Tweet.objects.filter(id=instance.tweet_id)\
        .update(comments_count=F('comments_count') + 1)
    # 只是invalid memcached 是不够的，因为不仅在memcached里面存了，还在redis里面存了list
    # 但是如果把每次都有人点赞时让redis里面存的list也失效，则会频繁失效，失去了我们希望达到的效果
    # 所以我们更应该做的是让comments_count的更新和cache invalidation的过程解绑
    # invalidate_object_cache(sender=Tweet, instance=instance.tweet)

def decr_comments_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    # handle comment deletion
    Tweet.objects.filter(id=instance.tweet_id)\
        .update(comments_count=F('comments_count') - 1)
    #invalidate_object_cache(sender=Tweet, instance=instance.tweet)
