from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from .forms import SignUpForm

class StoreUserAdmin(UserAdmin):
    add_form = SignUpForm
    model = StoreUser
    list_display = 'avatar', 'email', 'username'


admin.site.register(StoreUser, StoreUserAdmin)
admin.site.register(App)
admin.site.register(AppDeveloper)
admin.site.register(AppSubcategory)
admin.site.register(AppCategory)
admin.site.register(AppAgeRating)
admin.site.register(AppEstimation)
admin.site.register(AppPreviewImage)
admin.site.register(Achievement)
