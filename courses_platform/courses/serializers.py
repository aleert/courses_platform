from django.db import IntegrityError
from django.utils.text import slugify
from rest_framework import serializers
from django.db.models import ObjectDoesNotExist
from rest_framework.exceptions import NotAcceptable, NotFound
from rest_framework.reverse import reverse

from common.serializers import ListSerializerWithoutNulls
from . import models


#####################
# Content serializers
#####################

# All of the content contain id field so that it can be patched in ModuleItems view

def get_content_serializer_class(content_type: str):
    contents = {
        'text': TextSerializer,
        'file': FileSerializer,
        'image': ImageSerializer,
        'video': VideoSerializer,
        'stringassignment': StringAssignmentSerializer,
        'choicesassignment': ChoicesAssignmentSerializer,
        'multiplechoicesassignment': MultipleChoicesAssignmentSerializer,
    }

    return contents[content_type]


class ContentSerializer(serializers.Serializer):
    """Serializer that can handle display and creation of different content types."""

    def to_representation(self, instance):
        serializer_class = get_content_serializer_class(instance.content_type)
        url = reverse(
            'courses:content_detail',
            args=[instance.content_type, instance.pk, ],
            request=self.context.get('request'),
        )
        ret = {**serializer_class(instance).data, 'url': url}
        return ret

    def to_internal_value(self, data):
        request = self.context.get('request')
        owner_pk = request.user.pk
        item_pk = self.context.get('item_pk')
        return {**data, 'owner_id': owner_pk, 'item_pk': item_pk}


class StringAssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.StringAssignment
        fields = (
            'content_type',
            'max_score',
            'max_attempts',
            'paid_only',
            'answer',
            'id',
        )
        read_only_fields = ('content_type', 'id')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        if not (request and (request.user.pk == instance.owner_id or request.user.is_staff)):
            ret['answer'] = None
        return ret


class ChoicesAssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ChoicesAssignment
        fields = (
            'content_type',
            'max_score',
            'max_attempts',
            'paid_only',
            '_choices',
            'answer',
            'order',
            'id',
        )
        read_only_fields = ('content_type', 'id')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request', None)
        if not (request and (request.user.pk == instance.owner_id or request.user.is_staff)):
            ret['answer'] = None
        return ret


class MultipleChoicesAssignmentSerializer(serializers.ModelSerializer):
    choices = serializers.CharField(source='_choices')

    class Meta:
        model = models.MultipleChoicesAssignment
        fields = (
            'content_type',
            'max_score',
            'max_attempts',
            'paid_only',
            'choices',
            '_correct_choices',
            'order',
            'id',
        )
        read_only_fields = ('content_type', 'id', )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request', None)
        if not (request and (request.user.pk == instance.owner_id or request.user.is_staff)):
            ret['_correct_choices'] = []
        return ret


class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Text
        fields = (
            'content_type',
            'content',
            'title',
            'order',
            'id',
        )
        read_only_fields = ('content_type', 'id')


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.File
        fields = (
            'content_type',
            'title',
            'file',
            'order',
            'id',
        )
        read_only_fields = ('content_type', 'id')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = (
            'content_type',
            'title',
            'file',
            'order',
            'id',
        )
        read_only_fields = ('content_type', 'id', )


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Video
        fields = (
            'content_type',
            'title',
            'url',
            'order',
            'id',
        )
        read_only_fields = ('content_type', 'id', )


#####################################
# Serializers without related objects
#####################################

class SubjectWithoutCoursesSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Subject
        fields = ('title', 'url')
        extra_kwargs = {
            'url': {
                'view_name': 'courses:subject_detail'
            },
        }

    def to_internal_value(self, data):
        ret = super().to_internal_value(data=data)
        ret['slug'] = slugify(data['title'])
        return ret


class CourseWithoutModulesSerializer(serializers.HyperlinkedModelSerializer):

    subject = SubjectWithoutCoursesSerializer(required=False)

    class Meta:
        model = models.Course
        list_serializer_class = ListSerializerWithoutNulls
        fields = (
            'title',
            'overview',
            'url',
            'subject',
            'price',
            'open_date',
        )
        extra_kwargs = {
            'url': {
                'view_name': 'courses:course_detail'
            }
        }

    def create(self, validated_data):
        subject = validated_data.pop('subject', None)
        subject_obj = None
        if subject:
            try:
                subject_obj = models.Subject.objects.get(title=subject['title'])
            except ObjectDoesNotExist:
                raise NotFound(detail='Subject does not exist')
        validated_data['subject_id'] = subject_obj.pk if subject_obj else None
        try:
            instance = super().create(validated_data)
        except IntegrityError:
            raise NotAcceptable(detail='You already have course with such a title.')
        return instance

    def to_representation(self, instance):
        # if accessed from view check whether course should be displayed to user
        # (to restrict courses in SubjectDetailView)
        request = self.context.get('request')
        if bool(
            not request
            or instance.visible
            or request.user.is_staff
            or request.user == instance.owner
        ):
            return super().to_representation(instance)
        else:
            return None


class ModuleWithoutItemsSerializer(serializers.HyperlinkedModelSerializer):
    """Use to provide url and other module info, but without items."""

    class Meta:
        model = models.Module
        fields = ('title', 'description', 'order', 'url', )
        extra_kwargs = {
            'url': {
                'view_name': 'courses:module_detail',
            }
        }


##################################
# Serializers with related objects
##################################

class SubjectSerializer(serializers.HyperlinkedModelSerializer):

    courses = CourseWithoutModulesSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = models.Subject
        fields = ('title', 'url', 'courses', )
        extra_kwargs = {
            'url': {
                'view_name': 'courses:subject_detail'
            }
        }


class CourseSerializer(serializers.ModelSerializer):

    modules = ModuleWithoutItemsSerializer(many=True, read_only=True)
    subject = SubjectWithoutCoursesSerializer(required=False)

    class Meta:
        model = models.Course
        fields = ('title', 'overview', 'subject', 'price', 'open_date', 'modules', )

    def update(self, instance, validated_data):
        # can replace subject but cannot update nested modules
        subject = validated_data.pop('subject', None)
        validated_data.pop('modules', None)
        if subject:
            try:
                subject_obj = models.Subject.objects.get(title=subject['title'])
                validated_data['subject_id'] = subject_obj.pk if subject_obj else None
            except ObjectDoesNotExist:
                raise NotFound(detail='Subject does not exist')
        instance = super().update(instance, validated_data)
        return instance


class ItemSerializer(serializers.ModelSerializer):
    """Serializer that supports nested Content creation."""

    content = ContentSerializer(source='all_contents', many=True, required=False)
    url = serializers.HyperlinkedIdentityField(view_name='courses:item_detail')
    module_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Item
        fields = ('module_url', 'url', 'order', 'content', )

    def get_module_url(self, obj):
        return reverse(
            'courses:module_detail',
            args=[obj.module.pk],
            request=self.context.get('request')
        )

    def update(self, instance, validated_data):
        request = self.context.get('request', None)
        contents = validated_data.pop('all_contents')
        instance = super().update(instance, validated_data=validated_data)
        if request.method == 'PUT':

            for item in instance.all_contents():
                item.delete()

            for content in contents:
                serializer_class = get_content_serializer_class(content['content_type'])
                owner_id = request.user.pk
                serializer = serializer_class(data=content)
                if serializer.is_valid():
                    serializer.save(owner_id=owner_id, item_id=self.context.get('item_pk'))
                else:
                    raise serializers.ValidationError(detail=serializer.errors)

        elif request.method == 'PATCH':

            for content in contents:
                serializer_class = get_content_serializer_class(content['content_type'])
                owner_id = request.user.pk
                try:
                    content_instance = serializer_class.Meta.model.objects.get(pk=content['pk'])
                except KeyError:
                    raise serializers.ValidationError('Provide pk for all contents if using PATCH.')
                serializer = serializer_class(content_instance, data=content)
                if serializer.is_valid():
                    serializer.save(owner_id=owner_id, item_id=self.context.get('item_pk'))
                else:
                    raise serializers.ValidationError(detail=serializer.errors)

        return instance

    def create(self, validated_data):
        request = self.context.get('request')
        contents = validated_data.pop('all_contents')
        module_id = self.context.get('module_id')
        data = {**validated_data, 'module_id': module_id}
        instance = super().create(validated_data=data)
        for content in contents:
            serializer_class = get_content_serializer_class(content['content_type'])
            owner_id = request.user.pk
            serializer = serializer_class(data=content)
            if serializer.is_valid():
                serializer.save(owner_id=owner_id, item_id=instance.pk)
            else:
                raise serializers.ValidationError(detail=serializer.errors)
        return instance


class ModuleSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)
    course = CourseWithoutModulesSerializer()
    items_url = serializers.SerializerMethodField()

    class Meta:
        model = models.Module
        fields = (
            'title',
            'url',
            'items_url',
            'description',
            'course',
            'order',
            'items',
        )
        extra_kwargs = {
            'url': {
                'view_name': 'courses:module_detail',
            },
        }

    def get_items_url(self, obj):
        return reverse(
            'courses:module_items',
            args=[obj.pk],
            request=self.context.get('request', None)
        )
