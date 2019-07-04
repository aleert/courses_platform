from typing import List

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import cached_property

from .fields import OrderField


class Subject(models.Model):
    """Subject to tag courses with it."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, primary_key=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    """Course that consist of modules."""
    owner = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name='courses_created',
        on_delete=models.CASCADE,
    )
    subject = models.ForeignKey(
        to=Subject,
        related_name='courses',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    students = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        related_name='courses_joined',
        blank=True,
    )
    teachers = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        related_name='courses_teaches',
        blank=True,
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    overview = models.TextField()
    price = models.PositiveIntegerField(default=0, help_text='Price in USD')
    created = models.DateTimeField(auto_now_add=True)
    open_date = models.DateField()
    is_enroll_open = models.BooleanField(default=True)
    visible = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created', )
        unique_together = ('owner', 'title', )

    def __str__(self):
        return self.title

    @cached_property
    def get_max_score(self):
        return sum([module.get_max_score() for module in self.modules.all()])


class Module(models.Model):
    """Course module."""
    course = models.ForeignKey(
        Course,
        related_name='modules',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ('order', )

    def __str__(self):
        return "{0}. {1}".format(self.order, self.title)

    @cached_property
    def get_max_score(self):
        """Maximum score one can get by completing all module assignments."""
        raise NotImplementedError

    def all_items(self):
        items = []
        for item in self.items.all():
                    items.append(item)
        return items


class Item(models.Model):
    """Item with content."""
    CONTENTS_RELATED = [
        'text_related',
        'file_related',
        'image_related',
        'video_related',
    ]
    ASSIGNMENTS_RELATED = [
        'stringassignment_related',
        'choicesassignment_related',
        'multiplechoicesassignment_related',
    ]
    module = models.ForeignKey(
        to=Module,
        on_delete=models.CASCADE,
        related_name='items',
    )
    order = OrderField(for_fields=['module'], blank=True)

    def str(self):
        return f'Item {self.order} of module {self.module.id}'

    def all_contents(self):
        contents = []
        for content_type in Item.CONTENTS_RELATED:
            if hasattr(self, content_type):
                contents.extend(getattr(self, content_type).all())
        for assign_type in Item.ASSIGNMENTS_RELATED:
            if hasattr(self, assign_type):
                contents.extend(getattr(self, assign_type).all())
        return contents


class ContentBase(models.Model):
    """Base class for different content types (video, pics etc)."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(class)s_related',
        on_delete=models.CASCADE,
    )
    # sets to lowercase model name at save()
    content_type = models.CharField(max_length=20, blank=True, editable=False)
    title = models.CharField(max_length=250, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    order = OrderField(for_fields=['item'], blank=True)
    item = models.ForeignKey(
        to=Item,
        on_delete=models.CASCADE,
        related_name='%(class)s_related'
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=('content_type', 'id', )),
        ]

    def __str__(self):
        return f'Content {self.title}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.content_type = self._meta.model_name
        return super().save(force_insert=force_insert, force_update=force_update, using=using,
                            update_fields=update_fields)


class Text(ContentBase):
    """Text content for modules."""
    content = models.TextField()

    def __str__(self):
        return f'Text item: {self.content}'


class File(ContentBase):
    """Files attached to modules."""
    file = models.FileField(upload_to='files')

    def __str__(self):
        return f'File {self.file.name}'


class Image(ContentBase):
    """Images in modules."""
    file = models.ImageField(upload_to='images')

    def __str__(self):
        return f'Image {self.file.name}'


class Video(ContentBase):
    """Videos for modules stored as urls to external resources."""
    url = models.URLField()

    def __str__(self):
        return f'Video at {self.url}'


class BaseAssignment(ContentBase):

    owner = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name='%(class)s_related',
        on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        to=Item,
        related_name='%(class)s_related',
        on_delete=models.CASCADE
    )
    max_score = models.PositiveSmallIntegerField()
    max_attempts = models.PositiveSmallIntegerField(
        default=0,
        help_text='Specify 0 for unlimited attempts.'
    )
    paid_only = models.BooleanField(
        default=False,
        help_text='True if available only to users who bought a course.'
    )

    class Meta:
        abstract = True

    def validate_submission(self, submitted_answer):
        """Validate submission and return score earned."""
        raise NotImplementedError


class StringAssignment(BaseAssignment):
    """Compare string with expected one and give max_score if correct."""

    answer = models.CharField(max_length=200)
    question = models.TextField()

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

