from django.utils.html import strip_tags
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import (UserSerializer, ExerciseSerializer, ArticleSerializer, CategorySerializer, TestSerializer,
                          TestResultSerializer, AnswerSerializer, QuestionSerializer, QuoteSerializer,
                          TestResultUserSerializer, UserProfileSerializer)
from .models import (User, Exercise, Article, Category, Test, ResultTest, Question, Quotes, ResultTestUser, UserProfile)
import datetime
from dotenv import load_dotenv
import os
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import jwt
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail, EmailMultiAlternatives
from rest_framework.decorators import api_view
import random
from django.conf import settings

secret = os.getenv("SECRET")
load_dotenv()

verification_codes = {}


class SendCodeView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if not user:
            return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)

        code = random.randint(100000, 999999)
        verification_codes[email] = str(code)

        subject = "Скидання паролю"

        html_content = f"""
          <html>
             <body style="font-family: Segoe UI; font-size: 18px;">
               <p>Шановний користувачу <span style="color: #1386a6;"><strong>CalMi</strong></span>!</p>
               <p><i>Ми отримали запит на відновлення паролю до акаунту: {str(email).lower()}</i></p>
               <p>Ваш код підтвердження:</p>
               <p style="font-size: 28px; font-weight: bold; color: #1386a6;">{code}</p>
               <p>Не передавайте його нікому. Якщо ви не надсилали запит, проігноруйте це повідомлення.</p>
               <p>Бережіть себе та своє ментальне здоров'я!✨<br>З повагою, Команда CalMi </p>
             </body>
           </html>
           """

        text_content = strip_tags(html_content)  # plain text версія

        try:
            email_msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
            email_msg.attach_alternative(html_content, "text/html")  # додаємо HTML
            email_msg.send()
            print(f"Verification code {code} sent to {email}")
            return Response({
                'success': True,
                'message': 'Verification code sent',
            })
        except Exception as e:
            print("SEND MAIL ERROR:", e)
            return Response({'error': 'Failed to send email'}, status=500)


class VerifyCodeView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if str(verification_codes.get(email)) != str(code):
            return Response({'error': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)

        payload = {
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, secret, algorithm='HS256')
        return Response({'success': True, 'token': token})


class ResetPasswordView(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')

        if not token:
            return Response({'error': 'Token required'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = token.split(' ')[1]
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            email = payload.get('email')
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        new_password = request.data.get('new_password')
        if not new_password:
            return Response({'error': 'New password required'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        verification_codes.pop(email, None)

        return Response({'success': True, 'message': 'Password successfully reset'})


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


class VerifyPasswordView(APIView):
    def post(self, request):
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

        password = request.data.get('password')
        if not password or not user.check_password(password):
            raise AuthenticationFailed('Invalid password')

        return Response({'detail': 'Password is valid'}, status=200)


class UserView(APIView):
    def get_user_from_token(self, request):
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
        return user
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

    def delete(self, request):
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

        user.delete()
        return Response(status=204)

    def patch(self, request):
        user = self.get_user_from_token(request)
        data = request.data

        name = data.get('name')
        email = data.get('email')

        if name:
            user.name = name
        if email:
            user.email = email

        user.save()
        return Response({'message': 'User updated'})


class LogoutView(APIView):
    def post(self, request):
        return Response({"message": "Logged out successfully"})


class ExerciseView(APIView):
    def get(self, request, exercise_id=None):
        payload = check_token(request)
        category_id = request.query_params.get('category_id')

        if exercise_id:
            try:
                exercise = Exercise.objects.get(id=exercise_id)
                serializer = ExerciseSerializer(exercise)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exercise.DoesNotExist:
                return Response({"error": "Exercise not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            exercises = Exercise.objects.all()

            if category_id:
                exercises = exercises.filter(category_id=category_id)

            serializer = ExerciseSerializer(exercises, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class ArticleView(APIView):
    def get(self, request, article_id=None):
        payload = check_token(request)
        category_id = request.query_params.get('category_id')

        if article_id:
            article = get_object_or_404(Article, id=article_id)
            serializer = ArticleSerializer(article)
        else:
            articles = Article.objects.all()

            if category_id:
                articles = articles.filter(category_id=category_id)  # Фільтруємо по категорії, якщо параметр є

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


class QuestionListView(APIView):
    def get(self, request, test_id):
        payload = check_token(request)
        test = get_object_or_404(Test, id=test_id)
        questions = test.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)


class AnswerListView(APIView):
    def get(self, request, question_id):
        payload = check_token(request)
        question = get_object_or_404(Question, id=question_id)
        answers = question.answers.all()
        serializer = AnswerSerializer(answers, many=True)
        return Response(serializer.data)


class TestQuestionsWithAnswersView(APIView):
    def get(self, request, test_id):
        payload = check_token(request)
        test = get_object_or_404(Test, id=test_id)
        questions = test.questions.all()

        data = []
        for question in questions:
            answers = question.answers.all()
            question_data = {
                "id": question.id,
                "text": question.text,
                "answers": [
                    {
                        "id": answer.id,
                        "text": answer.text,
                        "score": answer.score,  # можеш прибрати, якщо не треба показувати
                    }
                    for answer in answers
                ]
            }
            data.append(question_data)

        return Response(data)


class RandomQuoteView(APIView):
    def get(self, request):
        payload = check_token(request)
        quotes = Quotes.objects.all()
        if not quotes:
            return Response({"detail": "No quotes available."}, status=404)
        random_quote = random.choice(quotes)
        serializer = QuoteSerializer(random_quote)
        return Response(serializer.data)


class SaveResultTestUserView(APIView):
    def get(self, request, test_id):
        # Перевірка токена
        payload = check_token(request)
        user = get_object_or_404(User, id=payload['id'])
        test = get_object_or_404(Test, id=test_id)

        # Отримати ВСІ результати юзера для цього тесту
        results = ResultTestUser.objects.filter(user=user, test=test)

        # Підготувати дані для відповіді
        results_data = [
            {
                'result_data': result.result_data,
                'passed_at': result.passed_at.isoformat(),  # Формат ISO 8601
            }
            for result in results
        ]

        return Response(results_data, status=status.HTTP_200_OK)

    def post(self, request, test_id):
        # Перевірка токена
        payload = check_token(request)
        user = get_object_or_404(User, id=payload['id'])
        test = get_object_or_404(Test, id=test_id)

        # Отримати дані з тіла запиту
        result_data = request.data.get('result_data')

        if not result_data:
            return Response({'error': 'Result data is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Створити новий результат
        ResultTestUser.objects.create(
            user=user,
            test=test,
            result_data=result_data
        )

        return Response({'message': 'Result saved successfully!'}, status=status.HTTP_201_CREATED)


class LastTestResultView(APIView):
    def get(self, request):
        # Перевірка токена
        payload = check_token(request)
        user = get_object_or_404(User, id=payload['id'])  # Отримуємо користувача за ID з токена

        # Отримуємо останній результат тесту для цього користувача
        last_test_result = ResultTestUser.objects.filter(user=user).order_by('-passed_at').first()

        if last_test_result is None:
            return Response({"message": "No tests found for this user."}, status=404)

        # Серіалізація результату
        serializer = TestResultUserSerializer(last_test_result)
        return Response(serializer.data)


class UserProfileView(APIView):
    def get(self, request):
        payload = check_token(request)
        if not payload:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        user =  get_object_or_404(User, id=payload['id'])

        profile, created = UserProfile.objects.get_or_create(user=user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

class SaveContentView(APIView):
    def post(self, request):
        payload = check_token(request)
        if not payload:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        user =  get_object_or_404(User, id=payload['id'])
        profile, created = UserProfile.objects.get_or_create(user=user)

        content_type = request.data.get('type')
        content_id = request.data.get('id')

        try:
            if content_type == 'article':
                content = Article.objects.get(id=content_id)
                profile.saved_articles.add(content)
            elif content_type == 'exercise':
                content = Exercise.objects.get(id=content_id)
                profile.saved_exercises.add(content)
            elif content_type == 'test':
                content = Test.objects.get(id=content_id)
                profile.saved_tests.add(content)
            else:
                return Response({'error': 'Invalid content type'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({'status': 'saved'})


class SaveOrRemoveContentView(APIView):
    def post(self, request):
        payload = check_token(request)
        if not payload:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        user = get_object_or_404(User, id=payload['id'])
        profile, created = UserProfile.objects.get_or_create(user=user)

        content_type = request.data.get('type')
        content_id = request.data.get('id')

        try:
            if content_type == 'article':
                content = Article.objects.get(id=content_id)
                if content in profile.saved_articles.all():
                    profile.saved_articles.remove(content)
                    return Response({'status': 'removed'})
                else:
                    profile.saved_articles.add(content)
                    return Response({'status': 'saved'})

            elif content_type == 'exercise':
                content = Exercise.objects.get(id=content_id)
                if content in profile.saved_exercises.all():
                    profile.saved_exercises.remove(content)
                    return Response({'status': 'removed'})
                else:
                    profile.saved_exercises.add(content)
                    return Response({'status': 'saved'})

            elif content_type == 'test':
                content = Test.objects.get(id=content_id)
                if content in profile.saved_tests.all():
                    profile.saved_tests.remove(content)
                    return Response({'status': 'removed'})
                else:
                    profile.saved_tests.add(content)
                    return Response({'status': 'saved'})
            else:
                return Response({'error': 'Invalid content type'}, status=400)

        except Exception as e:
            return Response({'error': str(e)}, status=400)


class SavedContentView(APIView):
    def get(self, request):
        payload = check_token(request)
        if not payload:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        user = get_object_or_404(User, id=payload['id'])
        profile = get_object_or_404(UserProfile, user=user)

        # Отримуємо збережені статті, вправи та тести
        saved_articles = profile.saved_articles.all()
        saved_exercises = profile.saved_exercises.all()
        saved_tests = profile.saved_tests.all()

        # Сериалізація даних
        article_serializer = ArticleSerializer(saved_articles, many=True)
        exercise_serializer = ExerciseSerializer(saved_exercises, many=True)
        test_serializer = TestSerializer(saved_tests, many=True)

        return Response({
            'saved_articles': article_serializer.data,
            'saved_exercises': exercise_serializer.data,
            'saved_tests': test_serializer.data
        })


class SavedArticlesView(APIView):
    def get(self, request):
        payload = check_token(request)
        if not payload:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        user = get_object_or_404(User, id=payload['id'])
        profile = get_object_or_404(UserProfile, user=user)

        # Fetch saved articles
        saved_articles = profile.saved_articles.all()
        serializer = ArticleSerializer(saved_articles, many=True)
        return Response(serializer.data)


class SavedExercisesView(APIView):
    def get(self, request):
        payload = check_token(request)
        if not payload:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        user = get_object_or_404(User, id=payload['id'])
        profile = get_object_or_404(UserProfile, user=user)

        # Fetch saved exercises
        saved_exercises = profile.saved_exercises.all()
        serializer = ExerciseSerializer(saved_exercises, many=True)
        return Response(serializer.data)


class SavedTestsView(APIView):
    def get(self, request):
        payload = check_token(request)
        if not payload:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        user = get_object_or_404(User, id=payload['id'])
        profile = get_object_or_404(UserProfile, user=user)

        # Fetch saved tests
        saved_tests = profile.saved_tests.all()
        serializer = TestSerializer(saved_tests, many=True)
        return Response(serializer.data)
