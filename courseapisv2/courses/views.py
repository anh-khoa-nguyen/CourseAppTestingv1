from django.shortcuts import render
#Action
# Create your views here.

from django.http import HttpResponse
from courses import serializers, paginators, perms
from courses.models import Category, Course, Lesson, Tag, User, Comment, Like

from rest_framework import viewsets, generics, status, parsers, permissions
from courses.models import Category

from rest_framework.decorators import action
from rest_framework.response import Response

def index(request):
    return HttpResponse('Hello, World!')

class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.filter(active=True) #chỉ lấy những thằng nào
    serializer_class = serializers.CategorySerializer
#Xong 2 dòng trên chỉ mới là phương thức, vì vậy cần kế thừa generics

class CourseViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Course.objects.filter(active=True) #chỉ lấy những thằng nào
    serializer_class = serializers.CourseSerializer
    pagination_class = paginators.CoursePaginator

    def get_queryset(self):
        queryset = self.queryset
        q = self.request.query_params.get('q')  # Tất cả queryparam nằm trong request
        if q:
            queryset = queryset.filter(name__icontains=q)


        cate_id = self.request.query_params.get('category_id')
        if cate_id:
            queryset = queryset.filter(category_id=cate_id)  # Không join để lấy ID, một gạch
        return queryset

    @action(methods=['get'], url_path ='lessons', detail = True)  # Nếu detail false thì không có course_id
    def get_lesson(self, request, pk):
        lessons = self.get_object().lesson_set.filter(active=True)  # Tập hợp các bài học của khóa học
        return Response(serializers.LessonSerializer(lessons, many=True).data, status.HTTP_200_OK)  # data là dữ liệu json

class LessonViewSet(viewsets.ViewSet, generics.RetrieveAPIView): #Retrieve = chi tiết
    queryset = Lesson.objects.prefetch_related('tags').filter(active=True) #Để nó fetch sẵn, tại lúc nào cũng lấy: sử dụng prefetch
    serializer_class  = serializers.LessonDetailsSerializer

    def get_permissions(self):
        if self.action in['add_comment', 'like']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()] #Trả về mảng

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return serializers.AuthenticatedLessonDetailsSerializer

        return serializers.LessonDetailsSerializer

    @action(methods=['GET'], url_path='comments', detail=True) #Đang trên một bài học
    def get_comments(self, request, pk):
        queryset = self.filter_queryset(self.get_queryset())

        comments = self.get_object().comment_set.select_related('user').order_by('-id') #Bây giờ muốn biết user nào đã tạo comment để hiện ra, truy vấn kiểu này thì tốn tới 100 truy vấn mới trả được user
        #Lấy comment ra là join luôn user luôn

        paginator = paginators.CommentPaginator()

        page = paginator.paginate_queryset(comments, request)
        if page is not None:
            serializer = serializers.CommentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response(serializers.CommentSerializer(comments, many=True).data)

    @action(methods=['POST'], url_path='comments', detail=True) #Mình phải biết bài gì mình mới comment được
    def add_comment(self, request, pk):
        c = self.get_object().comment_set.create(content=request.data.get('content'), user=request.user) #create bỏ vào get_object, cập nhật
        # Chứng thực mới được vào, nếu chỉ bỏ user vào thì có khả năng nó lấy user của người khác gửi lên, vậy nên ta dùng user đã chứng thực.
        # Comment.objects.create(content...)
        return Response(serializers.CommentSerializer(c).data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], url_path='like', detail=True)
    def like(self, request, pk):
        li, created = Like.objects.get_or_create(lesson=self.get_object(),
                                                 user = request.user) #Chưa có sẽ tạo ra, khi đó created sẽ là true, có rồi thì tiến hành lấy ra
        if not created:
            li.active = not li.active
            li.save()

        return Response(serializers.AuthenticatedLessonDetailsSerializer(self.get_object()).data)

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser, ] #post avatar

    #Get_current_user cần phải chứng thực, có khả năng request.user là anonnymous
    def get_permissions(self):
        if self.action in['get_current_user']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()] #Trả về mảng

    @action(methods=['get', 'patch'], url_path='current-user',
            detail=False)  # Không gửi id, chỉ khi nào chứng thực mới v
    def get_current_user(self, request):  # Không có pk vì details = False
        user = request.user
        # request.user #Một khi đã chứng thực thì đây là user nè, trách nhiệm là serializer thằng này ra
        if request.method.__eq__('PATCH'):
            for k, v in request.data.items():  # Trả về từ điển
                setattr(user, k, v)  # <=> user.first_name = v --> key = value
            user.save()

        return Response(serializers.UserSerializer(user).data)

class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [perms.CommentOwner]

