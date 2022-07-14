from django.core import serializers
from utils.json_encoder import JSONEncoder


class DjangoModelSerializer:

    @classmethod
    def serialize(cls, instance):
        # Django serializers need a QuerySet or list data to do serialization
        # So we need to use [] around instance.
        return serializers.serialize('json', [instance], cls=JSONEncoder)

    @classmethod
    def deserialize(cls, serialized_data):
        # .object is required to get the object data of primitive model type,
        # otherwise will get DeserializedObject type rather than ORM object
        # will return the original object
        return list(serializers.deserialize('json', serialized_data))[0].object