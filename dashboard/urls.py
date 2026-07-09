from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Core Dashboards
    path('', views.dashboard_redirect, name='redirect'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/edit-details/', views.student_detail_edit, name='student_detail_edit'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    
    # Admin User Management
    path('admin-panel/add-user/', views.admin_add_user, name='admin_add_user'),
    path('admin-panel/user/<int:user_id>/', views.admin_manage_user, name='admin_manage_user'),
    path('admin-panel/user/<int:user_id>/edit/', views.admin_edit_user, name='admin_edit_user'),
    path('admin-panel/user/<int:user_id>/toggle/', views.admin_toggle_active, name='admin_toggle_active'),
    path('admin-panel/user/<int:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
    
    # Notice Board / Announcements
    path('announcement/create/', views.create_announcement, name='create_announcement'),
    path('announcement/<int:pk>/delete/', views.delete_announcement, name='delete_announcement'),
    
    # Student Course Registration (AJAX)
    path('course/register/', views.student_course_register, name='student_course_register'),
    path('course/<int:course_id>/drop/', views.student_course_drop, name='student_course_drop'),
    
    # Teacher Student Management
    path('student-performance/<int:enrollment_id>/edit/', views.edit_student_performance, name='edit_student_performance'),
    path('student/enroll/', views.teacher_enroll_student, name='teacher_enroll_student'),
    
    # Admin Course Management
    path('courses/', views.admin_manage_courses, name='admin_manage_courses'),
    path('courses/<int:course_id>/delete/', views.admin_delete_course, name='admin_delete_course'),
]
