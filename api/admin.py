from django.contrib import admin
from .models import Exercise, Article, Category

class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')

admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)

