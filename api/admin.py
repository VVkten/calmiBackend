from django.contrib import admin
from .models import Exercise

class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')  # Відображаємо назву та категорію

admin.site.register(Exercise, ExerciseAdmin)
