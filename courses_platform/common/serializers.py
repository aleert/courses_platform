from django.db import models

from rest_framework import serializers


class ListSerializerWithoutNulls(serializers.ListSerializer):
    """List serializer that will omit null from response if result of item serialization was None."""

    def to_representation(self, data):
        iterable = data.all() if isinstance(data, models.Manager) else data
        ret = []
        for item in iterable:
            # check only None to keep 0, False and other falsy values
            if self.child.to_representation(item) is not None:
                ret.append(self.child.to_representation(item))

        return ret
