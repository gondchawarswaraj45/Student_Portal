from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from accounts.models import User, Profile, StudentDetail
from accounts.decorators import student_required, teacher_required, admin_required
from accounts.forms import StudentDetailForm, AdminCreateUserForm, AdminEditUserForm, ProfileUpdateForm
from .models import Announcement, Course, Enrollment


@login_required
def dashboard_redirect(request):
    """Redirect to the appropriate dashboard based on user role."""
    if request.user.is_superuser or request.user.is_admin_user:
        return redirect('dashboard:admin_dashboard')
    elif request.user.is_teacher:
        return redirect('dashboard:teacher_dashboard')
    else:
        return redirect('dashboard:student_dashboard')


@student_required
def student_dashboard(request):
    """Dashboard for students."""
    student_detail = StudentDetail.objects.filter(user=request.user).first()
    profile = Profile.objects.filter(user=request.user).first()
    
    # Query student courses / enrollments
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    
    # Query announcements targeting all or student
    announcements = Announcement.objects.filter(target_audience__in=['all', 'student']).order_by('-created_at')[:5]

    context = {
        'student_detail': student_detail,
        'profile': profile,
        'enrollments': enrollments,
        'announcements': announcements,
    }
    return render(request, 'dashboard/student_dashboard.html', context)


@student_required
def student_detail_edit(request):
    """Edit student academic details."""
    student_detail, created = StudentDetail.objects.get_or_create(
        user=request.user,
        defaults={'roll_number': f'STU{request.user.pk:04d}'}
    )

    if request.method == 'POST':
        form = StudentDetailForm(request.POST, instance=student_detail)
        if form.is_valid():
            form.save()
            messages.success(request, 'Academic details updated successfully!')
            return redirect('dashboard:student_dashboard')
    else:
        form = StudentDetailForm(instance=student_detail)

    return render(request, 'dashboard/student_detail_edit.html', {'form': form})


@teacher_required
def teacher_dashboard(request):
    """Dashboard for teachers."""
    students = User.objects.filter(role='student').select_related('student_detail', 'profile')
    total_students = students.count()

    dept_stats = StudentDetail.objects.values('department').annotate(
        count=Count('id')
    ).order_by('-count')

    year_stats = StudentDetail.objects.values('year').annotate(
        count=Count('id')
    ).order_by('year')

    # Query announcements
    announcements = Announcement.objects.filter(target_audience__in=['all', 'teacher']).order_by('-created_at')[:5]

    context = {
        'students': students,
        'total_students': total_students,
        'dept_stats': dept_stats,
        'year_stats': year_stats,
        'announcements': announcements,
    }
    return render(request, 'dashboard/teacher_dashboard.html', context)


@admin_required
def admin_dashboard(request):
    """Dashboard for administrators."""
    total_users = User.objects.count()
    total_students = User.objects.filter(role='student').count()
    total_teachers = User.objects.filter(role='teacher').count()
    total_admins = User.objects.filter(role='admin').count()
    verified_users = User.objects.filter(is_email_verified=True).count()
    all_users = User.objects.order_by('-date_joined')

    dept_stats = StudentDetail.objects.values('department').annotate(
        count=Count('id')
    ).order_by('-count')

    # Query announcements
    announcements = Announcement.objects.all().order_by('-created_at')[:5]

    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_admins': total_admins,
        'verified_users': verified_users,
        'all_users': all_users,
        'dept_stats': dept_stats,
        'announcements': announcements,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@admin_required
def admin_add_user(request):
    """Admin: create a new student or teacher."""
    if request.method == 'POST':
        form = AdminCreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            role_display = user.get_role_display()
            messages.success(request, f'{role_display} "{user.username}" created successfully!')
            return redirect('dashboard:admin_dashboard')
    else:
        form = AdminCreateUserForm()

    return render(request, 'dashboard/admin_add_user.html', {'form': form})


@admin_required
def admin_edit_user(request, user_id):
    """Admin: edit a user's information."""
    managed_user = get_object_or_404(User, pk=user_id)
    profile, _ = Profile.objects.get_or_create(user=managed_user)
    student_detail = StudentDetail.objects.filter(user=managed_user).first()

    if request.method == 'POST':
        user_form = AdminEditUserForm(request.POST, instance=managed_user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        # Handle student detail form if user is a student
        student_form = None
        if managed_user.is_student:
            if student_detail is None:
                student_detail = StudentDetail(user=managed_user)
            student_form = StudentDetailForm(request.POST, instance=student_detail)

        forms_valid = user_form.is_valid() and profile_form.is_valid()
        if student_form:
            forms_valid = forms_valid and student_form.is_valid()

        if forms_valid:
            user_form.save()
            profile_form.save()
            if student_form:
                student_form.save()
            messages.success(request, f'User "{managed_user.username}" updated successfully!')
            return redirect('dashboard:admin_manage_user', user_id=user_id)
    else:
        user_form = AdminEditUserForm(instance=managed_user)
        profile_form = ProfileUpdateForm(instance=profile)
        student_form = StudentDetailForm(instance=student_detail) if student_detail else None

    context = {
        'managed_user': managed_user,
        'user_form': user_form,
        'profile_form': profile_form,
        'student_form': student_form,
        'student_detail': student_detail,
    }
    return render(request, 'dashboard/admin_edit_user.html', context)


@admin_required
def admin_manage_user(request, user_id):
    """Admin: view/manage a specific user."""
    managed_user = get_object_or_404(User, pk=user_id)
    profile = Profile.objects.filter(user=managed_user).first()
    student_detail = StudentDetail.objects.filter(user=managed_user).first()

    context = {
        'managed_user': managed_user,
        'profile': profile,
        'student_detail': student_detail,
    }
    return render(request, 'dashboard/admin_manage_user.html', context)


@admin_required
def admin_toggle_active(request, user_id):
    """Admin: activate/deactivate a user."""
    managed_user = get_object_or_404(User, pk=user_id)
    managed_user.is_active = not managed_user.is_active
    managed_user.save()
    status = 'activated' if managed_user.is_active else 'deactivated'
    messages.success(request, f'User {managed_user.username} has been {status}.')
    return redirect('dashboard:admin_dashboard')


@admin_required
def admin_delete_user(request, user_id):
    """Admin: delete a user."""
    managed_user = get_object_or_404(User, pk=user_id)
    if managed_user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('dashboard:admin_dashboard')

    username = managed_user.username
    managed_user.delete()
    messages.success(request, f'User {username} has been deleted.')
    return redirect('dashboard:admin_dashboard')
