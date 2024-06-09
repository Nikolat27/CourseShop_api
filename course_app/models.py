from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from django.utils.text import slugify

from accounts_app.models import User


# Create your models here.


class Category(models.Model):
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="sub_categories", null=True, blank=True)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Language(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(max_length=75, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="categories",
                                 null=True, blank=True)
    instructors = models.ManyToManyField(User, related_name="instructor_courses")
    description = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, related_name="language_courses", null=True,
                                 blank=True)
    thumbnail = models.ImageField(upload_to="course_thumbnails", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.PositiveSmallIntegerField(default=0)
    slug = models.SlugField(unique=True, null=True, blank=True, allow_unicode=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.title:
            self.slug = slugify(self.title, allow_unicode=True)

        self.updated_at = timezone.now()
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.category.title}"

    def discounted_price(self):
        if self.discount_percentage > 0:
            discount_price = (self.price * self.discount_percentage) / 100
            final_price = self.price - discount_price
            return final_price
        else:
            return self.price

    def show_image(self):
        if self.thumbnail:
            return format_html(f"<img src={self.thumbnail.url} width='150px' height='90px'>")

    def is_discounted(self):
        if self.discount_percentage > 0:
            return True
        else:
            return False


class Season(models.Model):
    title = models.CharField(max_length=75)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_seasons")

    def __str__(self):
        return f"{self.title} - Course: {self.course.title}"


class Lecture(models.Model):
    title = models.CharField(max_length=75)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="season_lectures")
    file = models.FileField(upload_to="courses/files/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - Seasons: {self.season.title}"


class Requirements(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_requirements")
    title = models.CharField(max_length=75)

    def __str__(self):
        return self.title
