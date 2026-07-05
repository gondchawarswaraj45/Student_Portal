from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_redirect, name='redirect'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/edit-details/', views.student_detail_edit, name='student_detail_edit'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/add-user/', views.admin_add_user, name='admin_add_user'),
    path('admin-panel/user/<int:user_id>/', views.admin_manage_user, name='admin_manage_user'),
    path('admin-panel/user/<int:user_id>/edit/', views.admin_edit_user, name='admin_edit_user'),
    path('admin-panel/user/<int:user_id>/toggle/', views.admin_toggle_active, name='admin_toggle_active'),
    path('admin-panel/user/<int:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
]
