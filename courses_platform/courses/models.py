from typing import List

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils.functional import cached_property

from .fields import OrderField


class Subject(models.Model):
    """Subject to tag course with it."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    """Course that consist of modules."""
    owner = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                              related_name='courses_created',
                              on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,
                                related_name='courses',
                                on_delete=models.CASCADE)
    students = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                      related_name='courses_joined',
                                      blank=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    price = models.PositiveIntegerField(default=0, help_text='Price in USD')
    created = models.DateTimeField(auto_now_add=True)
    open_date = models.DateField()
    is_enroll_open = models.BooleanField(default=False)

    @cached_property
    def get_max_score(self):
        return

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title


class Module(models.Model):
    """Course module."""
    course = models.ForeignKey(Course,
                               related_name='modules',
                               on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "{0}. {1}".format(self.order, self.title)

    @cached_property
    def get_max_score(self):
        return

    @cached_property
    def all_items(self):
        items = []
        for item in self.items.all():
            for item_type in Item.ITEMS_RELATED:
                if hasattr(item, item_type):
                    items.append(getattr(item, item_type))
        return items


class Item(models.Model):
    ITEMS_RELATED = ['text_related', 'file_related', 'image_related', 'video_related']
    module = models.ForeignKey(to=Module,
                               on_delete=models.CASCADE,
                               related_name='items')
    order = OrderField(for_fields=['module'])

    @cached_property
    def all_items(self):
        items = []
        for item_type in Item.ITEMS_RELATED:
            if hasattr(self, item_type):
                items.extend(getattr(self, item_type).all())
        return items


class ItemBase(models.Model):
    """Base class for different content types (video, pics etc)."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name='%(class)s_related',
                              on_delete=models.CASCADE)
    item_type = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    # order all items througout, not by item_type
    order = OrderField(for_fields=['item'], blank=True)
    item = models.ForeignKey(to=Item,
                             on_delete=models.CASCADE,
                             related_name='%(class)s_related')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.item_type = self._meta.model_name
        return super().save(force_insert=force_insert, force_update=force_update, using=using,
                            update_fields=update_fields)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Text(ItemBase):
    """Text content for modules."""
    content = models.TextField()

    def __str__(self):
        return f'Text item: {self.content}'


class File(ItemBase):
    """Files attached to modules."""
    file = models.FileField(upload_to='files')

    def __str__(self):
        return f'File {self.file.name}'


class Image(ItemBase):
    """Images in modules."""
    file = models.ImageField(upload_to='images')

    def __str__(self):
        return f'Image {self.file.name}'


class Video(ItemBase):
    """Videos for modules stored as urls to external resources."""
    url = models.URLField()

    def __str__(self):
        return f'Video at {self.url}'


class Assignment(models.Model):
    TEXTS_RELATED = ['stringassignment_related', 'choicesassignment_related', 'multiplechoicesassignment_related']
    module = models.ForeignKey(to=Module,
                               on_delete=models.CASCADE,
                               related_name='assignments')


class BaseAssignment(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name='%(class)s_related',
                              on_delete=models.CASCADE)
    assignment = models.ForeignKey('Assignment',
                                   related_name='%(class)s_related',
                                   on_delete=models.CASCADE)
    max_score = models.PositiveSmallIntegerField()
    max_attempts = models.PositiveSmallIntegerField(default=0, help_text='Specify 0 for unlimited attempts.')
    paid_only = models.BooleanField(default=False, help_text='True if available only to users who bought a course.')

    class Meta:

        abstract = True

    def validate_submission(self, submitted_answer):
        """Validate submission and return score earned."""
        return self.max_score


class StringAssignment(BaseAssignment):
    """Compare string with expected one and give max_score if correct."""
    answer = models.CharField(max_length=200)

    def validate_submission(self, submitted_answer):
        if submitted_answer.lower() == self.answer.lower():
            return self.max_score
        return 0


class ChoicesAssignment(BaseAssignment):
    """Select one answer from a list."""
    # must be split with ',_' escape sequence
    _choices = models.TextField()
    answer = models.CharField(max_length=80)

    @cached_property
    def choices(self):
        return self._choices.split(',_')

    def validate_submission(self, submitted_answer):
        if submitted_answer == self.answer:
            return self.max_score
        return 0


class MultipleChoicesAssignment(BaseAssignment):
    # must be split with ',_' escape sequence
    _choices = models.TextField()
    _correct_choices = models.TextField()

    @cached_property
    def choices(self):
        return self._choices.split(',_')

    @cached_property
    def correct_choices(self):
        return self._correct_choices.split(',_')

    def validate_submission(self, submitted_answers: List[str]):
        num_correct_choices = len(self.correct_choices)
        correct_answers = sum(1 if answer in self.correct_choices else 0 for answer in submitted_answers)
        if not correct_answers:
            return 0
        # if there are at least one correct answer min score is 1
        return round(correct_answers*self.max_score/num_correct_choices) or 1

