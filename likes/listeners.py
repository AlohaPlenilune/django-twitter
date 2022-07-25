def incr_likes_count(sender, instance, created, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        # TODO 给Comment使用类似的方法进行likes_count的统计
        return

    # should not use tweet.likes_count += 1; tweet.save()
    # because this manipulation is not atomic. should use update syntax
    # SQL query: UPDATE likes_count = likes_count + 1 FROM tweets_table WHERE id = <instance.object_id>
    # 没有F会产生并发问题
    Tweet.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') + 1)


def decr_likes_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        # TODO Comment likes_count
        return

    # handle tweet likes cancel
    Tweet.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') - 1)