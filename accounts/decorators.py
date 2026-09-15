from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseNotAllowed
from functools import wraps


def role_required(allowed_roles):
    """Decorator to restrict access based on user role."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard:redirect')
        return wrapper
    return decorator


def student_required(view_func):
    """Restrict access to students only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_student:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'This page is accessible to students only.')
        return redirect('dashboard:redirect')
    return wrapper


def teacher_required(view_func):
    """Restrict access to teachers only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_teacher:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'This page is accessible to teachers only.')
        return redirect('dashboard:redirect')
    return wrapper


def admin_required(view_func):
    """Restrict access to admins only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_admin_user or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'This page is accessible to administrators only.')
        return redirect('dashboard:redirect')
    return wrapper


def email_verified_required(view_func):
    """Restrict access to users with verified email addresses."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_email_verified or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.warning(
            request,
            'Please verify your email address to access this feature. '
            'Check your inbox for the verification link.'
        )
        return redirect('dashboard:redirect')
    return wrapper


def post_required(view_func):
    """Restrict view to POST requests only — prevents destructive actions via GET."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])
        return view_func(request, *args, **kwargs)
    return wrapper
