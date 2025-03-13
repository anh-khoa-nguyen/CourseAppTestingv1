from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField

# Create your models here.
class User(AbstractUser):
    pass

#Mỗi đối tượng đều có
class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True) #Mỗi lần cập nhật tự lấy ngày hiện tại

    class Meta:
        abstract = True

class Category(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Course model
class Course(BaseModel):
    subject = models.CharField(max_length=255)
    description = models.TextField()
    image = CloudinaryField(null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT) #Cấm xóa luôn, bảo vệ Category khi có khóa học

    def __str__(self):
        return self.subject

# Lesson model
class Lesson(BaseModel):
    subject = models.CharField(max_length=255)
    content = RichTextField()
    image = CloudinaryField(null=True)

    course = models.ForeignKey(Course, on_delete=models.CASCADE) #Khi khóa học xóa thì tất cả bài học hủy
    tags = models.ManyToManyField("Tag")
    def __str__(self):
        return self.subject


class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
#
# Comment model
class Comment(BaseModel):
    content = models.TextField()
    image = models.ImageField(upload_to='lessons/', null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.lesson.subject}"
#
# # Rating model
# class Rating(BaseModel):
#     rating = models.DecimalField(max_digits=2, decimal_places=1)
#     lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='ratings')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return f"Rating {self.rating} by {self.user.username} for {self.lesson.subject}"
#
# # Tag model

#
# # LessonTag model
# class LessonTag(models.Model):
#     lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='lesson_tags')
#     tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='lesson_tags')
#
#     def __str__(self):
#         return f"{self.tag.name} - {self.lesson.subject}"

class Interaction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user_id} - {self.lesson_id}'

    class Meta:
        abstract = True

class Like(Interaction):
    class Meta:
        unique_together = ('user', 'lesson')
