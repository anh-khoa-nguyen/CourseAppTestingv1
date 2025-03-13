from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.urls import path
from courses.models import Category, Course, Lesson, Tag, Comment
# Register your models here.
from django import forms
from ckeditor_uploader.widgets \
import CKEditorUploadingWidget

class LessonForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget) #ĐÚNG TÊN MODEL MỚI ĐƯỢC NHÉ

    class Meta:
        model = Lesson
        fields = '__all__'
    #Model Lesson tất cả các trường trong đó đè trường content

class MyLessonAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject','created_date','active','course']
    search_fields = ['subject']
    list_filter = ['id','created_date']
    readonly_fields = ['image_view']
    form = LessonForm

    def image_view(self, lesson):
        return mark_safe(f"<img src='/static/{lesson.image.name}' width='200' />") #Đánh dấu an toàn k phải mã độc

    class Media:
        css = {
            'all': ('/static/css/style.css',)
        }

class MyCourseAdminSite(admin.AdminSite):
    site_header = 'eCourseOnline'

    def get_urls(self):
        return [
            path('course-stats/', self.stats_view)
        ] + super().get_urls() #Các url có sẵn cộng thêm của mình

    def stats_view(self, request):
        course_stats = Category.objects.annotate(c=Count('course__id')).values('id','name','c')
        return TemplateResponse(request, 'admin/stats.html', {
            "course_stats": course_stats #Danh sách khóa học của danh mục
        })

admin_site = MyCourseAdminSite(name='iCourse')

admin_site.register(Category)
admin_site.register(Course)
admin_site.register(Lesson, MyLessonAdmin)
admin_site.register(Tag)
admin_site.register(Comment)