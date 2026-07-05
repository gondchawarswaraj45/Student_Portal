from django.db import models
from django.conf import settings

class Announcement(models.Model):
    """System-wide announcements posted by Admin or Teachers."""
    
    TARGET_CHOICES = [
        ('all', 'All Users'),
        ('student', 'Students Only'),
        ('teacher', 'Teachers Only'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='announcements')
    target_audience = models.CharField(max_length=10, choices=TARGET_CHOICES, default='all')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Course(models.Model):
    """Courses offered by the department."""
    
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    semester = models.CharField(max_length=1)  # 1 to 8

    def __str__(self):
        return f"{self.code} - {self.name}"


class Enrollment(models.Model):
    """Student enrollment in courses with grades and attendance."""
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=85.0)
    grade = models.CharField(max_length=2, blank=True, null=True) # e.g. A+, A, B, etc.
    marks = models.IntegerField(default=75) # Out of 100

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.name}"

    class Meta:
        unique_together = ('student', 'course')
