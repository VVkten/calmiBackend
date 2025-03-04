from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User
import jwt
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# Завантажуємо секретний ключ з файлу .env
secret = os.getenv("SECRET")

# Клас для реєстрації користувача
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# Клас для входу користувача
class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found')

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

# Клас для отримання інформації про користувача
class UserView(APIView):
    def get(self, request):
        # Отримуємо токен з заголовку "Authorization"
        token = request.headers.get('Authorization')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            # Очікуємо, що заголовок виглядатиме як "Bearer <token>"
            token = token.split(' ')[1]
            # Декодуємо токен і перевіряємо його дійсність
            payload = jwt.decode(token, secret, algorithms=['HS256'])
        except (jwt.ExpiredSignatureError, IndexError):
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()

        if not user:
            raise AuthenticationFailed('User not found')

        # Повертаємо серіалізовані дані користувача
        serializer = UserSerializer(user)
        return Response(serializer.data)

# Клас для виходу з системи
class LogoutView(APIView):
    def post(self, request):
        # Оскільки ми не використовуємо cookies, просто повертаємо повідомлення про вихід
        return Response({"message": "Logged out successfully"})
