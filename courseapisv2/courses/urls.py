from django.urls import path, include
# Mặc dù ngang cấp nhưng Django bắt from
from . import views
from rest_framework import routers
from courses import views

r = routers.DefaultRouter()
r.register('categories',  views.CategoryViewSet, basename='categories')
r.register('courses',  views.CourseViewSet, basename='courses')
r.register('lessons', views.LessonViewSet, basename='lessons')
r.register('users', views.UserViewSet, basename='users')
r.register('comments', views.CommentViewSet, basename='comments')

urlpatterns = [
    # path('', views.index),
    path('', include(r.urls)),  # Gọi views.CategoryViewSet
]


