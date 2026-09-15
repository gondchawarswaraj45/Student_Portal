from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


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
    is_pinned = models.BooleanField(default=False, help_text='Pinned announcements appear at the top.')
    expires_at = models.DateTimeField(null=True, blank=True, help_text='Leave blank for no expiry.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        """Check if announcement has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def is_visible(self):
        """Check if announcement should be displayed."""
        return not self.is_expired

    class Meta:
        ordering = ['-is_pinned', '-created_at']


class Course(models.Model):
    """Courses offered by the department."""
    
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    semester = models.CharField(max_length=1)  # 1 to 8
    credits = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(6)])
    max_enrollment = models.IntegerField(default=60, validators=[MinValueValidator(1)],
                                          help_text='Maximum number of students allowed.')
    is_active = models.BooleanField(default=True, help_text='Inactive courses are hidden from registration.')

    @property
    def enrolled_count(self):
        """Number of currently enrolled (active) students."""
        return self.enrollments.filter(status='active').count()

    @property
    def seats_available(self):
        """Number of remaining seats."""
        return max(0, self.max_enrollment - self.enrolled_count)

    @property
    def is_full(self):
        """Check if course is at capacity."""
        return self.enrolled_count >= self.max_enrollment

    def __str__(self):
        return f"{self.code} - {self.name} ({self.credits} cr)"


# Grade scale for auto-calculation
GRADE_SCALE = {
    'A+': (90, 100, 10.0),
    'A':  (80, 89, 9.0),
    'B+': (70, 79, 8.0),
    'B':  (60, 69, 7.0),
    'C':  (50, 59, 6.0),
    'D':  (40, 49, 5.0),
    'F':  (0, 39, 0.0),
}


def calculate_grade(marks):
    """Auto-calculate grade from marks using standard grading scale."""
    if marks is None:
        return 'N/A'
    marks = int(marks)
    for grade, (low, high, _) in GRADE_SCALE.items():
        if low <= marks <= high:
            return grade
    return 'F'


def get_grade_points(grade):
    """Get grade points for GPA calculation."""
    for g, (_, _, points) in GRADE_SCALE.items():
        if g == grade:
            return points
    return 0.0


class Enrollment(models.Model):
    """Student enrollment in courses with grades and attendance."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('dropped', 'Dropped'),
        ('completed', 'Completed'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}, related_name='enrollments'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    attendance_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=100.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    grade = models.CharField(max_length=2, blank=True, default='N/A')
    marks = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    enrolled_at = models.DateTimeField(default=timezone.now)

    def clean(self):
        """Validate marks range and auto-calculate grade."""
        super().clean()
        if self.marks is not None:
            if self.marks < 0 or self.marks > 100:
                raise ValidationError({'marks': 'Marks must be between 0 and 100.'})
            # Auto-calculate grade from marks
            self.grade = calculate_grade(self.marks)

    def save(self, *args, **kwargs):
        """Auto-calculate grade before saving."""
        if self.marks is not None and self.marks > 0:
            self.grade = calculate_grade(self.marks)
        super().save(*args, **kwargs)

    @property
    def is_low_attendance(self):
        """Flag if attendance is below 75% (warning threshold)."""
        return self.attendance_percentage < 75

    @property
    def grade_points(self):
        """Get grade points for this enrollment."""
        return get_grade_points(self.grade)

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.name}"

    class Meta:
        unique_together = ('student', 'course')
