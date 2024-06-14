from django.db import models
from django.db.models import Avg
from django.utils import timezone
from django.utils.html import format_html
from django.utils.text import slugify
from moviepy.editor import *
from accounts_app.models import User


# Create your models here.


class Category(models.Model):
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="sub_categories", null=True, blank=True)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Subtitle(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Language(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title


levels = (("All Levels", "All Levels"), ("Beginner", "Beginner"),
          ("Intermediate", "Intermediate"), ("Advanced", "Advanced"),)


class Course(models.Model):
    title = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="categories",
                                 null=True, blank=True)
    instructors = models.ManyToManyField(User, related_name="instructor_courses")
    description = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.PROTECT, related_name="language_courses", null=True,
                                 blank=True)
    thumbnail = models.ImageField(upload_to="course_thumbnails", null=True, blank=True)
    costly = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                help_text="If you did set the 'costly' field False, Do Not touch this field pls")
    discount_percentage = models.PositiveSmallIntegerField(default=0)
    subtitles = models.ManyToManyField(Subtitle)
    level = models.CharField(max_length=20, choices=levels, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, allow_unicode=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.title:
            self.slug = slugify(self.title, allow_unicode=True)

        self.updated_at = timezone.now()
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.category.title}"

    def average_review(self):
        review = self.comments.aggregate(reviews=Avg("rating"))
        avg = 0
        if review['reviews'] is not None:
            avg = float(review['reviews'])
        return avg

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
    title = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_seasons")

    def __str__(self):
        return f"{self.title} - Course: {self.course.title}"


class Lecture(models.Model):
    title = models.CharField(max_length=100)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="season_lectures")
    file = models.FileField(upload_to="courses/files/videos")
    duration = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - Seasons: {self.season.title}"

    def save(self, *args, **kwargs):
        if self.file:
            clip = VideoFileClip(self.file.path)
            self.duration = int(clip.duration)
            clip.close()
        super(Lecture, self).save(*args, **kwargs)


class Prerequisite(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_prerequisite")
    title = models.CharField(max_length=75)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_courses")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="user_courses")
    purchased_at = models.DateTimeField(auto_now_add=True)
    purchased_price = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


choices = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reviews")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True)
    rating = models.IntegerField(choices=choices, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} - {self.course.title} - {self.rating} - {self.text[:15]}"

    def time_difference(self):
        if self.created_at:
            now = timezone.now()
            time_difference = now - self.created_at
            time_difference = time_difference.total_seconds() / 60
            # To show the time like this '2.2' instead of '2.1123516123'
            return round(time_difference, 1)

    def save(self, *args, **kwargs):
        if self.parent:
            if self.rating:
                self.rating = None
        super(Review, self).save(*args, **kwargs)
