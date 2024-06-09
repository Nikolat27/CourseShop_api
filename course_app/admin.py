from django.contrib import admin
from . import models


# Register your models here.


# class SeasonInLine(admin.TabularInline):
#     model = models.Season


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    autocomplete_fields = ["parent"]


@admin.register(models.Language)
class LanguageAdmin(admin.ModelAdmin):
    search_fields = ["title"]


class LectureInLine(admin.TabularInline):
    model = models.Lecture


class RequirementsInLine(admin.TabularInline):
    model = models.Requirements


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_display = ("title", "price", "show_image")
    autocomplete_fields = ["category", "language"]
    inlines = [RequirementsInLine]


@admin.register(models.Season)
class SeasonAdmin(admin.ModelAdmin):
    autocomplete_fields = ["course"]
    inlines = [LectureInLine]
