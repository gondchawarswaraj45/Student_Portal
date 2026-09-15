from django.utils import timezone
from django.conf import settings
from django.contrib.auth import logout
from django.contrib import messages
import datetime


class SessionTimeoutMiddleware:
    """Auto-logout users after inactivity period with warning."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = getattr(settings, 'SESSION_COOKIE_AGE', 1800)  # 30 min default

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            now = timezone.now().isoformat()

            if last_activity:
                try:
                    last = datetime.datetime.fromisoformat(last_activity)
                    if (timezone.now() - last).total_seconds() > self.timeout:
                        logout(request)
                        messages.warning(
                            request,
                            'Your session has expired due to inactivity. Please log in again.'
                        )
                except (ValueError, TypeError):
                    pass

            request.session['last_activity'] = now

        response = self.get_response(request)
        return response
