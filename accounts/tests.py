from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()


class SecurityAndAccountTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='TestPass123!',
            role='student',
            is_email_verified=True,
        )
        self.admin = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='AdminPass123!',
            role='admin',
            is_email_verified=True,
        )

    def test_failed_login_attempts_and_lockout(self):
        """Account should lock out after threshold failed attempts."""
        self.assertEqual(self.student.failed_login_attempts, 0)
        self.assertFalse(self.student.is_locked_out)

        # 5 failed attempts
        for _ in range(5):
            self.student.record_failed_login()

        self.student.refresh_from_db()
        self.assertEqual(self.student.failed_login_attempts, 5)
        self.assertTrue(self.student.is_locked_out)

    def test_reset_login_attempts(self):
        """Successful login should reset failed attempts."""
        self.student.record_failed_login()
        self.student.record_failed_login()
        self.student.refresh_from_db()
        self.assertEqual(self.student.failed_login_attempts, 2)

        self.student.reset_login_attempts()
        self.student.refresh_from_db()
        self.assertEqual(self.student.failed_login_attempts, 0)
        self.assertIsNone(self.student.lockout_until)

    def test_logout_post_only(self):
        """GET request to logout should be rejected (405)."""
        self.client.login(username='teststudent', password='TestPass123!')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 405)

        # POST should succeed
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
