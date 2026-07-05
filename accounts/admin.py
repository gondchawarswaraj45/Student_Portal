from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, StudentDetail


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


class StudentDetailInline(admin.StackedInline):
    model = StudentDetail
    can_delete = False
    verbose_name_plural = 'Student Details'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_email_verified', 'is_active')
    list_filter = ('role', 'is_email_verified', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Verification', {'fields': ('role', 'is_email_verified')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role & Verification', {'fields': ('role', 'is_email_verified')}),
    )
    inlines = [ProfileInline, StudentDetailInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_of_birth', 'created_at')
    search_fields = ('user__username', 'phone')


@admin.register(StudentDetail)
class StudentDetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll_number', 'department', 'year', 'semester')
    list_filter = ('department', 'year', 'semester')
    search_fields = ('user__username', 'roll_number', 'department')
