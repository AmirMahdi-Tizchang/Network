from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "last_login", "date_joined")

class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "get_date")

admin.site.register(User, UserAdmin)
admin.site.register(Post)
admin.site.register(Follow)
