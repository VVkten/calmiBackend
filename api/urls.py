from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('user/', views.UserView.as_view(), name='user'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Exercise URLs
    path('exercises/', views.ExerciseView.as_view(), name='exercises'),  # для всіх вправ
    path('exercise/<int:exercise_id>/', views.ExerciseView.as_view(), name='exercise_detail'),  # для конкретної вправи

    # Article URLs
    path('articles/', views.ArticleView.as_view(), name='articles'),  # для всіх статей
    path('article/<int:article_id>/', views.ArticleView.as_view(), name='article_detail'),  # для конкретної статті

    # Category URLs
    path('categories/', views.CategoryView.as_view(), name='categories'),  # для всіх категорій
    path('category/<int:category_id>/', views.CategoryView.as_view(), name='category_detail'),  # для конкретної категорії

    # Test URLs
    path('tests/', views.TestListView.as_view(), name='tests'),  # для всіх тестів
    path('test/<int:test_id>/', views.TestListView.as_view(), name='test_detail'),  # для конкретного тесту

    # Result Test URLs
    path('result-test/<int:test_id>/', views.ResultTestView.as_view(), name='result_test'),  # для результату тесту
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
