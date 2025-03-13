from rest_framework import serializers
from courses.models import Category, Course, Lesson, Tag, User, Comment


class ItemSerializer(serializers.ModelSerializer):
	def to_representation(self, instance): #Tạo ra cái gì đó đại diện
		rep = super().to_representation(instance)
		rep['image'] = instance.image.url #Instance là đối tượng của Course, trả về đường dẫn tuyệt đối trên Cloudinary
		return rep

class TagSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tag
		fields = ['id', 'name']

class LessonSerializer(ItemSerializer):
	class Meta:
		model = Lesson
		fields = ['id', 'subject', 'image', 'created_date', 'updated_date']

class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = '__all__'

class CourseSerializer(ItemSerializer):
	class Meta:
		model = Course
		fields = ['id', 'subject', 'image', 'created_date', 'updated_date']

class LessonDetailsSerializer(LessonSerializer):
	tags = TagSerializer(many=True)

	class Meta:
		model = LessonSerializer.Meta.model
		fields = LessonSerializer.Meta.fields + ['content', 'tags']

class AuthenticatedLessonDetailsSerializer(LessonDetailsSerializer): #Đối vớiuser đã chứng thực
	liked = serializers.SerializerMethodField()

	def get_like(self, lesson):
		return lesson.like_set.filter(active=True).exists()

	class Meta:
		model = LessonDetailsSerializer.Meta.model
		fields = LessonDetailsSerializer.Meta.fields + ['liked']

class UserSerializer(serializers.ModelSerializer):
	#Ghi đè giai đoạn chèn:
	def create(self, validated_data):
		data = validated_data.copy() #Lúc này nó trở thành đối tượng thì mới set_password được
		user = User(**data)
		user.set_password(data["password"])
		user.save()

		return user

	class Meta:
		model = User
		fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password']

class CommentSerializer(serializers.ModelSerializer):
	user = UserSerializer
	class Meta:
		model = Comment
		fields = ['id','content', 'created_date', 'user']