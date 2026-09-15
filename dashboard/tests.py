from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from dashboard.models import Course, Enrollment, Announcement, calculate_grade, get_grade_points
from dashboard.views import calculate_gpa, calculate_total_credits, MAX_COURSES_PER_STUDENT

User = get_user_model()


class DashboardBusinessLogicTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='teststudent',
            email='teststudent@eduportal.com',
            password='Password123!',
            role='student',
            is_email_verified=True,
        )
        self.admin = User.objects.create_user(
            username='testadmin',
            email='testadmin@eduportal.com',
            password='AdminPassword123!',
            role='admin',
            is_email_verified=True,
        )
        self.course1 = Course.objects.create(
            code='CS101',
            name='Computer Science I',
            department='Computer Science',
            semester='1',
            credits=3,
            max_enrollment=2,
            is_active=True,
        )
        self.course2 = Course.objects.create(
            code='CS102',
            name='Data Structures',
            department='Computer Science',
            semester='1',
            credits=4,
            max_enrollment=50,
            is_active=True,
        )

    def test_grade_calculation_scale(self):
        """Verify standard scale mapping."""
        self.assertEqual(calculate_grade(95), 'A+')
        self.assertEqual(calculate_grade(85), 'A')
        self.assertEqual(calculate_grade(75), 'B+')
        self.assertEqual(calculate_grade(65), 'B')
        self.assertEqual(calculate_grade(55), 'C')
        self.assertEqual(calculate_grade(45), 'D')
        self.assertEqual(calculate_grade(30), 'F')
        self.assertEqual(calculate_grade(None), 'N/A')

    def test_enrollment_auto_grade_on_save(self):
        """Enrollment should automatically assign grade based on marks."""
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course1,
            attendance_percentage=90.0,
            marks=88,
        )
        self.assertEqual(enrollment.grade, 'A')

    def test_gpa_and_credits_calculation(self):
        """Verify weighted GPA and credit sum."""
        e1 = Enrollment.objects.create(
            student=self.student, course=self.course1,
            marks=92, attendance_percentage=95.0
        )  # A+ -> 10.0 pts * 3 cr = 30
        e2 = Enrollment.objects.create(
            student=self.student, course=self.course2,
            marks=82, attendance_percentage=90.0
        )  # A -> 9.0 pts * 4 cr = 36
        enrollments = [e1, e2]
        # Total pts = 66, Total credits = 7 -> GPA = 66 / 7 = 9.43
        gpa = calculate_gpa(enrollments)
        credits = calculate_total_credits(enrollments)
        self.assertEqual(gpa, 9.43)
        self.assertEqual(credits, 7)

    def test_course_capacity_and_availability(self):
        """Course seats available and is_full logic."""
        self.assertEqual(self.course1.seats_available, 2)
        self.assertFalse(self.course1.is_full)

        # Enroll student 1
        Enrollment.objects.create(student=self.student, course=self.course1, marks=50)
        self.assertEqual(self.course1.seats_available, 1)

        # Enroll student 2
        student2 = User.objects.create_user(
            username='student2', email='stu2@test.com', password='Pass!', role='student'
        )
        Enrollment.objects.create(student=student2, course=self.course1, marks=50)
        self.assertEqual(self.course1.seats_available, 0)
        self.assertTrue(self.course1.is_full)

    def test_admin_destructive_actions_require_post(self):
        """Admin delete user and toggle active should reject GET (405)."""
        self.client.login(username='testadmin', password='AdminPassword123!')

        # GET request to delete user should fail
        response = self.client.get(reverse('dashboard:admin_delete_user', args=[self.student.pk]))
        self.assertEqual(response.status_code, 405)

        # GET request to toggle active should fail
        response = self.client.get(reverse('dashboard:admin_toggle_active', args=[self.student.pk]))
        self.assertEqual(response.status_code, 405)

        # GET request to delete course should fail
        response = self.client.get(reverse('dashboard:admin_delete_course', args=[self.course1.pk]))
        self.assertEqual(response.status_code, 405)

    def test_admin_cannot_delete_self(self):
        """Admin should not be able to delete their own account."""
        self.client.login(username='testadmin', password='AdminPassword123!')
        response = self.client.post(reverse('dashboard:admin_delete_user', args=[self.admin.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())
