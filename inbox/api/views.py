from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from notifications.models import Notification

from inbox.api.serializers import NotificationSerializer


class NotificationViewSet(
    viewsets.GenericViewSet,
    # list all notifications(include a list() method)是一个很通用的方法，可以看是如何实现的
    viewsets.mixins.ListModelMixin,
):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('unread',) # without this, cannot filter by unread = True / False

    def get_queryset(self):
        # can also use the following method (django的反查机制)
        return Notification.objects.filter(recipient=self.request.user)
        # return self.request.user.notifications.all()

    @action(methods=['GET'], detail=False, url_path='unread-count')
    def unread_count(self, request, *args, **kwargs):
        # GET /api/notifications/unread-count/
        # 如果代码量比较多，一下子看不到get_queryset()是如何筛选的，可以这样写：
        # Notification.objects.filter(
        #     recipient=self.request.user,
        #     unread=True
        # ).count()
        count = self.get_queryset().filter(unread=True).count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='mark-all-as-read')
    def mark_all_as_read(self, request, *args, **kwargs):
        # Notification.objects.update() # SQL update
        # query_set method
        updated_count = self.get_queryset().update(unread=False) # 批量操作
        return Response({'marked_count': updated_count}, status=status.HTTP_200_OK)