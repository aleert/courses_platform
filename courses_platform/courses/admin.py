from django.contrib import admin

from .models import (ChoicesAssignment, Course, File, Image, Item, Module,
                     MultipleChoicesAssignment, StringAssignment, Subject, Text, Video)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title', )}


class ModuleInline(admin.StackedInline):
    """Inline for adding modules."""
    model = Module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Course admin with module inline."""
    list_display = ['title', 'subject', 'created']
    list_filter = ['created', 'subject']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title', )}
    inlines = [ModuleInline]


class ImageInline(admin.StackedInline):
    model = Image


class TextInline(admin.StackedInline):
    model = Text


class FileInline(admin.StackedInline):
    model = File


class VideoInline(admin.StackedInline):
    model = Video


class StringAssignmentInline(admin.StackedInline):
    model = StringAssignment


class ChoicesAssignmentInline(admin.StackedInline):
    model = ChoicesAssignment


class MultipleChoicesAssignmentInline(admin.StackedInline):
    model = MultipleChoicesAssignment


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    fields = ['module']
    inlines = [
        ImageInline, TextInline, FileInline, VideoInline,
        StringAssignmentInline, ChoicesAssignmentInline, MultipleChoicesAssignmentInline
    ]


class ItemInline(admin.StackedInline):
    fields = ['module', 'order']
    model = Item
    show_change_link = True


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    inlines = [ItemInline]
