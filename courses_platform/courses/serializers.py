from collections import defaultdict

from rest_framework import serializers

from . import models


class StringAssignmentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.StringAssignment
        fields = (
            'owner',
            'max_score',
            'max_attempts',
            'paid_only',
            'answer',
        )


#####################
# Item serializers
#####################

class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Text
        fields = ('item_type', 'content', 'title', 'order')


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.File
        fields = ('item_type', 'title', 'file', 'order')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = ('item_type', 'title', 'file', 'order')


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Video
        fields = ('item_type', 'title', 'url', 'order')


class ItemSerializer(serializers.Serializer):
    texts = TextSerializer
    files = FileSerializer
    images = ImageSerializer
    videos = VideoSerializer
    order = serializers.IntegerField(required=False)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        sorted_items = defaultdict(list)
        for item in instance.all_items:
            sorted_items[item._meta.model_name + 's'].append(item)
        returned_dict = {key: getattr(self, key)(sorted_items[key], many=True).data for key in sorted_items.keys()}
        module_url = ModuleWithoutItemsSerializer(instance.module, context={'request': None}).data['url']
        ret['module'] = module_url
        ret.move_to_end('module', last=False)
        ret.update(returned_dict)
        return ret


class ModuleSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = models.Module
        fields = ('title', 'description', 'course', 'order', 'items')
        extra_kwargs = {
            'url': {
                'view_name': 'courses:module_detail',
            }
        }


class ModuleWithoutItemsSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Module
        fields = ('title', 'description', 'course', 'order', 'url')
        extra_kwargs = {
            'url': {
                'view_name': 'courses:module_detail',
            }
        }
