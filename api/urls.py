from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import RegisterView, LoginView, UserView, LogoutView, ExerciseView, ExerciseDetailView, ArticleView, CategoryView
# from .views import TestListView, TestDetailView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('user/', UserView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('exercises/', ExerciseView.as_view()),
    path('exercises/<int:exercise_id>/', ExerciseDetailView.as_view()),
    path('articles/', ArticleView.as_view(), name='article-list'),
    path('articles/<int:article_id>/', ArticleView.as_view(), name='article-detail'),
    path('categories/', CategoryView.as_view(), name='category-list'),
    path('categories/<int:category_id>/', CategoryView.as_view(), name='category-detail'),

]

# Додаємо обробку медіафайлів **тільки в режимі розробки**
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
