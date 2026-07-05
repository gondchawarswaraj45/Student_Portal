from django.contrib import admin
from .models import Announcement, Course, Enrollment

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_by', 'target_audience', 'created_at')
    list_filter = ('target_audience', 'created_at')
    search_fields = ('title', 'content')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'semester')
    list_filter = ('department', 'semester')
    search_fields = ('code', 'name')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'attendance_percentage', 'grade', 'marks')
    list_filter = ('course__name', 'grade')
    search_fields = ('student__username', 'course__name')
