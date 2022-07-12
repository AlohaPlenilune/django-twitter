def invalidate_following_cache(sender, instance, **kwargs):
    # import FriendshipService within the function to avoid circular referring
    #
    from friendships.services import FriendshipService
    FriendshipService.invalidate_following_cache(instance.from_user_id)