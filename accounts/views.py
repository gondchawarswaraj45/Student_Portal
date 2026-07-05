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

from .models import User, Profile
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm, UserUpdateForm
from .tokens import email_verification_token


def register_view(request):
    """Handle STUDENT-ONLY registration."""
    if request.user.is_authenticated:
        return redirect('dashboard:redirect')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.STUDENT  # Force student role
            user.is_active = True
            user.save()

            # Create profile
            Profile.objects.create(user=user)

            # Send verification email
            current_site = get_current_site(request)
            subject = 'Activate Your Account - Registration Portal'
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': email_verification_token.make_token(user),
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

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
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard:redirect')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('dashboard:redirect')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Handle user logout."""
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
    """View and update user profile."""
    # Ensure profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

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
