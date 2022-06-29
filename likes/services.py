from django.contrib.contenttypes.models import ContentType

from likes.models import Like


class LikeService(object):
    @classmethod
    def has_liked(cls, user, target):
        # the user passed in here is request.user. It can be anonymous user
        # It's better to judge if the user is anonymous here rather than at upper level,
        # so that can reduce repeated codes.
        if user.is_anonymous:
            return False
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user,
        ).exists()
