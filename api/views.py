from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer, ExerciseSerializer, ArticleSerializer, CategorySerializer, TestSerializer, TestResultSerializer
from .models import User, Exercise, Article, Category, Test, ResultTest
import datetime
from dotenv import load_dotenv
import os
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import jwt
from django.shortcuts import get_object_or_404

secret = os.getenv("SECRET")
load_dotenv()


def check_token(request):
    token = request.headers.get('Authorization')

    if not token:
        raise AuthenticationFailed('Unauthenticated!')

    try:
        token = token.split(' ')[1]
        payload = jwt.decode(token, secret, algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, IndexError):
        raise AuthenticationFailed('Unauthenticated!')

    return payload


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        # Перевірка, чи є користувач з таким імейлом
        if not user:
            return Response({"error": "Email not found"}, status=status.HTTP_404_NOT_FOUND)

        # Перевірка пароля
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')

        # Генерація JWT токену
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, secret, algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {'jwt': token}
        return response


class UserView(APIView):
    def get(self, request):
        token = request.headers.get('Authorization')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            token = token.split(' ')[1]
            payload = jwt.decode(token, secret, algorithms=['HS256'])
        except (jwt.ExpiredSignatureError, IndexError):
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()

        if not user:
            raise AuthenticationFailed('User not found')

        serializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        return Response({"message": "Logged out successfully"})


class ExerciseView(APIView):
    def get(self, request, exercise_id=None):
        payload = check_token(request)
        if exercise_id:
            try:
                exercise = Exercise.objects.get(id=exercise_id)
                serializer = ExerciseSerializer(exercise)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exercise.DoesNotExist:
                return Response({"error": "Exercise not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            exercises = Exercise.objects.all()
            serializer = ExerciseSerializer(exercises, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class ArticleView(APIView):
    def get(self, request, article_id=None):
        payload = check_token(request)
        if article_id:
            article = get_object_or_404(Article, id=article_id)
            serializer = ArticleSerializer(article)
        else:
            articles = Article.objects.all()
            serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryView(APIView):
    def get(self, request, category_id=None):
        payload = check_token(request)
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            serializer = CategorySerializer(category)
        else:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TestListView(APIView):
    def get(self, request, test_id=None):
        payload = check_token(request)
        if test_id:
            test = get_object_or_404(Test, id=test_id)
            serializer = TestSerializer(test)
            return Response(serializer.data)
        else:
            tests = Test.objects.all()
            serializer = TestSerializer(tests, many=True)
            return Response(serializer.data)


class ResultTestView(APIView):
    def get(self, request, test_id):
        payload = check_token(request)
        result_test = get_object_or_404(ResultTest, test_id=test_id)
        serializer = TestResultSerializer(result_test)
        return Response(serializer.data)
