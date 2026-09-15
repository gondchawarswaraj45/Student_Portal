from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from accounts.models import User, Profile, StudentDetail
from accounts.decorators import student_required, teacher_required, admin_required, post_required
from accounts.forms import StudentDetailForm, AdminCreateUserForm, AdminEditUserForm, ProfileUpdateForm
from .models import Announcement, Course, Enrollment, GRADE_SCALE, get_grade_points
from .forms import AnnouncementForm, CourseForm, EnrollmentForm, TeacherEnrollStudentForm


# Maximum courses a student can enroll in per semester
MAX_COURSES_PER_STUDENT = 6


def calculate_gpa(enrollments):
    """Calculate GPA from active enrollments with marks > 0."""
    graded = [e for e in enrollments if e.marks > 0 and e.status == 'active']
    if not graded:
        return 0.0
    total_points = sum(e.grade_points * e.course.credits for e in graded)
    total_credits = sum(e.course.credits for e in graded)
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0


def calculate_total_credits(enrollments):
    """Calculate total credits from active enrollments."""
    return sum(e.course.credits for e in enrollments if e.status == 'active')


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
    """Dashboard for students with GPA, attendance warnings, and credit tracking."""
    student_detail = StudentDetail.objects.filter(user=request.user).first()
    profile = Profile.objects.filter(user=request.user).first()
    
    # Query student courses / enrollments
    enrollments = list(
        Enrollment.objects.filter(student=request.user, status='active')
        .select_related('course')
    )
    
    # Calculate GPA and credits
    gpa = calculate_gpa(enrollments)
    total_credits = calculate_total_credits(enrollments)
    
    # Attendance warnings
    low_attendance_courses = [e for e in enrollments if e.is_low_attendance]
    
    # Query announcements targeting all or student (exclude expired)
    from django.utils import timezone
    announcements = Announcement.objects.filter(
        target_audience__in=['all', 'student']
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    ).order_by('-is_pinned', '-created_at')[:5]

    # Available courses (exclude already enrolled, only active courses)
    enrolled_course_ids = Enrollment.objects.filter(
        student=request.user, status='active'
    ).values_list('course_id', flat=True)
    
    available_courses = Course.objects.filter(is_active=True).exclude(id__in=enrolled_course_ids)
    if student_detail and student_detail.semester:
        available_courses = available_courses.filter(semester=student_detail.semester)

    # Check enrollment limits
    can_enroll = len(enrollments) < MAX_COURSES_PER_STUDENT

    context = {
        'student_detail': student_detail,
        'profile': profile,
        'enrollments': enrollments,
        'gpa': gpa,
        'total_credits': total_credits,
        'low_attendance_courses': low_attendance_courses,
        'announcements': announcements,
        'available_courses': available_courses,
        'can_enroll': can_enroll,
        'max_courses': MAX_COURSES_PER_STUDENT,
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
    """Dashboard for teachers with performance analytics."""
    students = User.objects.filter(role='student').select_related('profile')
    total_students = students.count()

    dept_stats = StudentDetail.objects.values('department').annotate(
        count=Count('id')
    ).order_by('-count')

    year_stats = StudentDetail.objects.values('year').annotate(
        count=Count('id')
    ).order_by('year')

    # Query announcements
    from django.utils import timezone
    announcements = Announcement.objects.filter(
        target_audience__in=['all', 'teacher']
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    ).order_by('-is_pinned', '-created_at')[:5]
    
    # Query all active enrollments
    enrollments = Enrollment.objects.filter(status='active').select_related('student', 'course').order_by('student__username')
    courses = Course.objects.all()

    # Performance analytics
    avg_marks = enrollments.aggregate(avg=Avg('marks'))['avg'] or 0
    pass_count = enrollments.filter(marks__gte=40).count()
    fail_count = enrollments.filter(marks__lt=40, marks__gt=0).count()
    total_graded = pass_count + fail_count
    pass_rate = round((pass_count / total_graded) * 100, 1) if total_graded > 0 else 0

    # Attendance defaulters (below 75%)
    defaulters = enrollments.filter(attendance_percentage__lt=75).select_related('student', 'course')

    # Forms
    announcement_form = AnnouncementForm()
    enroll_student_form = TeacherEnrollStudentForm()
    performance_form = EnrollmentForm()

    context = {
        'students': students,
        'total_students': total_students,
        'dept_stats': dept_stats,
        'year_stats': year_stats,
        'announcements': announcements,
        'enrollments': enrollments,
        'courses': courses,
        'announcement_form': announcement_form,
        'enroll_student_form': enroll_student_form,
        'performance_form': performance_form,
        'avg_marks': round(avg_marks, 1),
        'pass_rate': pass_rate,
        'pass_count': pass_count,
        'fail_count': fail_count,
        'defaulters': defaulters,
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
    announcements = Announcement.objects.all().order_by('-is_pinned', '-created_at')[:5]
    courses = Course.objects.all()

    # Active enrollments stats
    total_enrollments = Enrollment.objects.filter(status='active').count()
    total_courses = courses.count()

    # Forms
    announcement_form = AnnouncementForm()
    course_form = CourseForm()

    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_admins': total_admins,
        'verified_users': verified_users,
        'all_users': all_users,
        'dept_stats': dept_stats,
        'announcements': announcements,
        'courses': courses,
        'announcement_form': announcement_form,
        'course_form': course_form,
        'total_enrollments': total_enrollments,
        'total_courses': total_courses,
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
@post_required
def admin_toggle_active(request, user_id):
    """Admin: activate/deactivate a user (POST only)."""
    managed_user = get_object_or_404(User, pk=user_id)

    # Prevent admin from deactivating themselves
    if managed_user == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('dashboard:admin_dashboard')

    managed_user.is_active = not managed_user.is_active
    managed_user.save()
    status = 'activated' if managed_user.is_active else 'deactivated'
    messages.success(request, f'User {managed_user.username} has been {status}.')
    return redirect('dashboard:admin_dashboard')


@admin_required
@post_required
def admin_delete_user(request, user_id):
    """Admin: delete a user (POST only with self-protection)."""
    managed_user = get_object_or_404(User, pk=user_id)
    if managed_user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('dashboard:admin_dashboard')

    # Prevent deleting other admins unless superuser
    if managed_user.is_admin_user and not request.user.is_superuser:
        messages.error(request, 'Only superusers can delete admin accounts.')
        return redirect('dashboard:admin_dashboard')

    username = managed_user.username
    managed_user.delete()
    messages.success(request, f'User {username} has been deleted.')
    return redirect('dashboard:admin_dashboard')


# --- Upgraded Features View Functions ---

@login_required
def create_announcement(request):
    """Post a new notice/announcement."""
    if not (request.user.is_superuser or request.user.is_admin_user or request.user.is_teacher):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard:redirect')

    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            ann = form.save(commit=False)
            ann.posted_by = request.user
            ann.save()
            messages.success(request, 'Announcement posted successfully!')
        else:
            messages.error(request, 'Failed to post announcement. Please check your inputs.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:redirect'))


@login_required
@post_required
def delete_announcement(request, pk):
    """Delete a notice/announcement (POST only)."""
    ann = get_object_or_404(Announcement, pk=pk)
    if not (request.user.is_superuser or request.user.is_admin_user or request.user == ann.posted_by):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Permission denied.'}, status=403)
        messages.error(request, 'Permission denied.')
        return redirect('dashboard:redirect')

    ann.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Announcement deleted successfully.'})
    messages.success(request, 'Announcement deleted successfully.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:redirect'))


@student_required
@require_POST
def student_course_register(request):
    """Enroll a student in a course via AJAX with capacity and limit checks."""
    course_id = request.POST.get('course_id')
    course = get_object_or_404(Course, id=course_id)

    # Check if course is active
    if not course.is_active:
        return JsonResponse({'success': False, 'message': 'This course is not available for registration.'})

    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course, status='active').exists():
        return JsonResponse({'success': False, 'message': 'You are already registered for this course.'})

    # Check enrollment limit
    active_count = Enrollment.objects.filter(student=request.user, status='active').count()
    if active_count >= MAX_COURSES_PER_STUDENT:
        return JsonResponse({
            'success': False,
            'message': f'You have reached the maximum of {MAX_COURSES_PER_STUDENT} courses per semester.'
        })

    # Check course capacity
    if course.is_full:
        return JsonResponse({
            'success': False,
            'message': f'Course {course.code} is full ({course.max_enrollment} students enrolled).'
        })

    enrollment = Enrollment.objects.create(
        student=request.user,
        course=course,
        attendance_percentage=100.0,
        marks=0,
        grade='N/A',
        status='active',
    )
    return JsonResponse({
        'success': True,
        'message': f'Successfully registered for {course.code} — {course.name}!',
        'course': {
            'id': course.id,
            'code': course.code,
            'name': course.name,
            'credits': course.credits,
            'attendance': float(enrollment.attendance_percentage),
            'marks': enrollment.marks,
            'grade': enrollment.grade,
        }
    })


@student_required
@require_POST
def student_course_drop(request, course_id):
    """Drop a course enrollment via AJAX."""
    course = get_object_or_404(Course, id=course_id)
    enrollment = Enrollment.objects.filter(student=request.user, course=course, status='active').first()
    if enrollment:
        enrollment.status = 'dropped'
        enrollment.save()
        return JsonResponse({'success': True, 'message': f'Dropped course {course.code} successfully.'})
    return JsonResponse({'success': False, 'message': 'Enrollment not found.'}, status=404)


@teacher_required
def edit_student_performance(request, enrollment_id):
    """Update grade, marks, and attendance with auto-grade calculation."""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    if request.method == 'POST':
        form = EnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()  # Grade auto-calculated in model save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Student performance updated successfully!',
                    'performance': {
                        'id': enrollment.id,
                        'attendance': float(enrollment.attendance_percentage),
                        'marks': enrollment.marks,
                        'grade': enrollment.grade,
                    }
                })
            messages.success(request, 'Student performance updated successfully!')
            return redirect('dashboard:teacher_dashboard')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            messages.error(request, 'Failed to update performance. Please check input values.')
    return redirect('dashboard:teacher_dashboard')


@teacher_required
def teacher_enroll_student(request):
    """Enroll a student in a course by a teacher."""
    if request.method == 'POST':
        form = TeacherEnrollStudentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.status = 'active'

            # Check capacity
            if enrollment.course.is_full:
                messages.error(request, f'Course {enrollment.course.code} is at full capacity.')
                return redirect('dashboard:teacher_dashboard')

            form.save()
            messages.success(request, 'Student enrolled successfully!')
        else:
            messages.error(request, 'Failed to enroll student. (Check if they are already enrolled in this course).')
    return redirect('dashboard:teacher_dashboard')


@admin_required
def admin_manage_courses(request):
    """Admin view to manage and add courses."""
    courses = Course.objects.all()
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course added successfully!')
            return redirect('dashboard:admin_manage_courses')
        else:
            messages.error(request, 'Failed to add course. Make sure course code is unique.')
    else:
        form = CourseForm()
    return render(request, 'dashboard/admin_manage_courses.html', {'courses': courses, 'form': form})


@admin_required
@post_required
def admin_delete_course(request, course_id):
    """Admin view to delete a course (POST only)."""
    course = get_object_or_404(Course, id=course_id)
    code = course.code
    course.delete()
    messages.success(request, f'Course {code} deleted successfully.')
    return redirect('dashboard:admin_manage_courses')
