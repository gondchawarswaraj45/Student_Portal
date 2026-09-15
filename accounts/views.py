from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST

from .models import User, Profile
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm, UserUpdateForm
from .tokens import email_verification_token


def register_view(request):
    """Handle STUDENT-ONLY registration with honeypot anti-bot protection."""
    if request.user.is_authenticated:
        return redirect('dashboard:redirect')

    if request.method == 'POST':
        # Honeypot check — bots fill hidden fields, humans don't
        honeypot = request.POST.get('website', '')
        if honeypot:
            # Silent rejection for bots
            messages.error(request, 'Registration failed. Please try again.')
            return redirect('accounts:register')

        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.STUDENT  # Force student role
            user.is_active = True
            user.save()

            # Create profile
            Profile.objects.create(user=user)

            # Send verification email
            try:
                current_site = get_current_site(request)
                subject = 'Activate Your Account - Registration Portal'
                message = render_to_string('accounts/activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': email_verification_token.make_token(user),
                })
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            except Exception:
                pass  # Don't block registration if email fails

            messages.success(
                request,
                'Student account created successfully! A verification email has been sent. '
                'You can log in now.'
            )
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Handle user login with brute-force protection."""
    if request.user.is_authenticated:
        return redirect('dashboard:redirect')

    if request.method == 'POST':
        username_input = request.POST.get('username', '').strip()

        # Check if account is locked
        try:
            if '@' in username_input:
                target_user = User.objects.get(email__iexact=username_input)
            else:
                target_user = User.objects.get(username=username_input)

            if target_user.is_locked_out:
                remaining = target_user.lockout_until
                messages.error(
                    request,
                    f'Account temporarily locked due to too many failed attempts. '
                    f'Try again after {remaining.strftime("%I:%M %p")}.'
                )
                return render(request, 'accounts/login.html', {'form': UserLoginForm()})
        except User.DoesNotExist:
            target_user = None

        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                user.reset_login_attempts()
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('dashboard:redirect')
        else:
            # Record failed attempt
            if target_user:
                target_user.record_failed_login()
                remaining_attempts = max(0, getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5) - target_user.failed_login_attempts)
                if remaining_attempts > 0:
                    messages.error(
                        request,
                        f'Invalid username or password. {remaining_attempts} attempts remaining.'
                    )
                else:
                    messages.error(
                        request,
                        'Account locked due to too many failed attempts. Please try again later.'
                    )
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@require_POST
def logout_view(request):
    """Handle user logout — POST only to prevent CSRF logout attacks."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def activate_view(request, uidb64, token):
    """Handle email verification."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        user.is_email_verified = True
        user.save()
        messages.success(request, 'Email verified successfully! You can now log in.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return redirect('home')


@login_required
def profile_view(request):
    """View and update user profile with upload validation."""
    # Ensure profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        # Validate uploaded image
        if 'profile_picture' in request.FILES:
            uploaded = request.FILES['profile_picture']
            max_size = getattr(settings, 'MAX_UPLOAD_SIZE_MB', 2) * 1024 * 1024
            allowed_types = getattr(settings, 'ALLOWED_IMAGE_TYPES',
                                    ['image/jpeg', 'image/png', 'image/gif', 'image/webp'])

            if uploaded.size > max_size:
                messages.error(request, f'Image too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB.')
                return redirect('accounts:profile')

            if uploaded.content_type not in allowed_types:
                messages.error(request, 'Invalid image format. Use JPEG, PNG, GIF, or WebP.')
                return redirect('accounts:profile')

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile.html', context)
