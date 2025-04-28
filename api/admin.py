from django.contrib import admin
from .models import (
    Exercise,
    Article,
    Category,
    Test,
    ResultTest,
    Question,
    Answer,
    ResultTestUser,
    Quotes
)


class QuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')


class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user  # Записуємо поточного користувача як автора
        obj.save()


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user  # Записуємо поточного користувача як автора
        obj.save()


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')


class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user  # Записуємо поточного користувача як автора
        obj.save()


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test')


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'score', 'question')


class ResultTestAdmin(admin.ModelAdmin):
    list_display = ('test', 'result_data')


class ResultTestUserAdmin(admin.ModelAdmin):
    list_display = ('test', 'user', 'result_data')


admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(ResultTest, ResultTestAdmin)
admin.site.register(ResultTestUser, ResultTestUserAdmin)
admin.site.register(Quotes, QuoteAdmin)