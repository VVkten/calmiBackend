from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('user/', views.UserView.as_view(), name='user'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('user/verify-password/', views.VerifyPasswordView.as_view()),
    # Password reset (2FA-like)
    path('send-code/', views.SendCodeView.as_view(), name='send_code'),
    path('verify-code/', views.VerifyCodeView.as_view(), name='verify_code'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),

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
    path('tests/', views.TestListView.as_view(), name='test-list'),
    path('tests/<int:test_id>/', views.TestListView.as_view(), name='test-detail'),
    path('tests/<int:test_id>/questions/', views.QuestionListView.as_view(), name='test-questions'),
    path('questions/<int:question_id>/answers/', views.AnswerListView.as_view(), name='question-answers'),
    path('tests/<int:test_id>/result/', views.ResultTestView.as_view(), name='test-result'),
    path('tests/<int:test_id>/questions_with_answers/', views.TestQuestionsWithAnswersView.as_view(), name='questions-with-answers'),

    path('quotes/', views.RandomQuoteView.as_view(), name='quote'),

    path('save-result/<int:test_id>/', views.SaveResultTestUserView.as_view(), name='save_result'),
    path('last_test_result/', views.LastTestResultView.as_view(), name='last_test_result'),

    path('profile/', views.UserProfileView.as_view()),
    path('save/', views.SaveContentView.as_view()),
    path('save-content/', views.SaveOrRemoveContentView.as_view()),

    path('save-articles/', views.SavedArticlesView.as_view()),
    path('save-tests/', views.SavedTestsView.as_view()),
    path('save-exercises/', views.SavedExercisesView.as_view()),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
