from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with role-based access."""

    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN


class Profile(models.Model):
    """Extended user profile with additional details."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(max_length=300, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    avatar_ratio = models.CharField(
        max_length=10,
        choices=[
            ('1-1', '1:1 (Square)'),
            ('4-5', '4:5 (Portrait)'),
            ('16-9', '16:9 (Landscape)'),
            ('auto', 'Auto / Original')
        ],
        default='auto'
    )
    avatar_position = models.CharField(
        max_length=10,
        choices=[
            ('center', 'Center'),
            ('top', 'Top'),
            ('bottom', 'Bottom')
        ],
        default='center'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class StudentDetail(models.Model):
    """Academic details for students."""

    YEAR_CHOICES = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
    ]

    SEMESTER_CHOICES = [
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
        ('3', 'Semester 3'),
        ('4', 'Semester 4'),
        ('5', 'Semester 5'),
        ('6', 'Semester 6'),
        ('7', 'Semester 7'),
        ('8', 'Semester 8'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_detail')
    roll_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    year = models.CharField(max_length=1, choices=YEAR_CHOICES, default='1')
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, default='1')
    admission_date = models.DateField(null=True, blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.roll_number}"

    class Meta:
        verbose_name = 'Student Detail'
        verbose_name_plural = 'Student Details'
