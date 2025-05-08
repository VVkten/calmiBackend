from rest_framework import serializers
from .models import User
from .models import Exercise
from .models import User, Category, Article
from .models import Test, Question, Answer, ResultTest, Quotes, ResultTestUser, UserProfile
import os
import random
from django.conf import settings
from django.templatetags.static import static


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'birth_date', 'gender', 'photo']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        gender = validated_data.get('gender', 'O')  # Якщо стать не вказано — вибрати "Інша"

        # Мапа для підстановки шляхів за гендером
        gender_map = {
            'M': 'male',
            'F': 'female',
            'O': 'other',
        }

        gender_folder = gender_map.get(gender, 'other')  # fallback на "other"
        avatar_dir = os.path.join(settings.BASE_DIR, 'static', 'default_avatars', gender_folder)

        try:
            avatar_choices = os.listdir(avatar_dir)
            selected_avatar = random.choice(avatar_choices)
            avatar_path = f'default_avatars/{gender_folder}/{selected_avatar}'  # шлях до фото
            avatar_url = static(avatar_path)  # генеруємо URL для статичного файлу
        except (FileNotFoundError, IndexError):
            avatar_url = None  # Якщо аватарки немає, то ставимо None

        instance = self.Meta.model(**validated_data)

        if avatar_url:
            instance.photo = avatar_url  # тут ми зберігаємо URL, а не шлях до файлу

        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    # author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # category = CategorySerializer(read_only=True)

    class Meta:
        model = Article
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = '__all__'


class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Test
        fields = '__all__'


class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultTest
        fields = '__all__'


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotes
        fields = '__all__'


class TestResultUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultTestUser
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    saved_articles = ArticleSerializer(many=True, read_only=True)
    saved_exercises = ExerciseSerializer(many=True, read_only=True)
    saved_tests = TestSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ['saved_articles', 'saved_exercises', 'saved_tests']