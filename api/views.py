from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User
import datetime
from dotenv import load_dotenv
import os
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Exercise
from .serializers import ExerciseSerializer
import jwt
from django.shortcuts import get_object_or_404
from .models import Test, TestResult
from .serializers import TestSerializer


secret = os.getenv("SECRET")

load_dotenv()

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

        # Генерація JWT токену з ідентифікатором користувача та терміном дії
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
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        exercises = Exercise.objects.all()
        serializer = ExerciseSerializer(exercises, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ExerciseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExerciseDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, exercise_id):
        try:
            exercise = Exercise.objects.get(id=exercise_id)
            serializer = ExerciseSerializer(exercise)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exercise.DoesNotExist:
            return Response({"error": "Exercise not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, exercise_id):
        try:
            exercise = Exercise.objects.get(id=exercise_id)
            serializer = ExerciseSerializer(exercise, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exercise.DoesNotExist:
            return Response({"error": "Exercise not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, exercise_id):
        try:
            exercise = Exercise.objects.get(id=exercise_id)
            exercise.delete()
            return Response({"message": "Exercise deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Exercise.DoesNotExist:
            return Response({"error": "Exercise not found"}, status=status.HTTP_404_NOT_FOUND)

class TestListView(APIView):
    """Список всіх тестів"""

    def get(self, request):
        tests = Test.objects.all()
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)  # Призначаємо автора
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TestDetailView(APIView):
    """Деталі конкретного тесту"""

    def get(self, request, test_id):
        test = get_object_or_404(Test, id=test_id)
        serializer = TestSerializer(test)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TestResultView(APIView):
    """Обчислення результату тесту"""

    def post(self, request, test_id):
        test = get_object_or_404(Test, id=test_id)
        user_answers = request.data.get("answers", [])  # Список відповідей

        total_score = sum(answer["points"] for answer in user_answers)

        # Шукаємо відповідний результат
        result = TestResult.objects.filter(
            test=test,
            min_score__lte=total_score,
            max_score__gte=total_score
        ).first()

        if result:
            return Response({"result": result.result_text}, status=status.HTTP_200_OK)
        return Response({"error": "Результат не знайдено"}, status=status.HTTP_404_NOT_FOUND)
