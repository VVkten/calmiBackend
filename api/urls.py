from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import RegisterView, LoginView, UserView, LogoutView, ExerciseView, ExerciseDetailView
from .views import TestListView, TestDetailView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('user/', UserView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('exercises/', ExerciseView.as_view()),  # Список вправ та створення
    path('exercises/<int:exercise_id>/', ExerciseDetailView.as_view()),  # Операції з конкретною вправою
    path('tests/', TestListView.as_view(), name='test-list'),
    path('tests/<int:pk>/', TestDetailView.as_view(), name='test-detail'),

    # path('user/update/', UpdateUserView.as_view()),
    # path('user/change-password/', ChangePasswordView.as_view()),
    # path('user/upload-photo/', UploadPhotoView.as_view()),
]

# Додаємо обробку медіафайлів **тільки в режимі розробки**
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
