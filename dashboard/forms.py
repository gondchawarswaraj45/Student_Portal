from django import forms
from django.core.exceptions import ValidationError
from .models import Announcement, Course, Enrollment
from accounts.models import User


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'target_audience', 'is_pinned', 'expires_at']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter announcement title...',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Type your announcement here...',
                'rows': 4,
            }),
            'target_audience': forms.Select(attrs={
                'class': 'form-input',
            }),
            'is_pinned': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local',
                'placeholder': 'Leave blank for no expiry',
            }),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'department', 'semester', 'credits', 'max_enrollment', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. CS101',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Intro to Computer Science',
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Computer Science',
            }),
            'semester': forms.Select(choices=[(str(i), f"Semester {i}") for i in range(1, 9)], attrs={
                'class': 'form-input',
            }),
            'credits': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '1',
                'max': '6',
                'placeholder': 'e.g. 3',
            }),
            'max_enrollment': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '1',
                'placeholder': 'e.g. 60',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['attendance_percentage', 'marks']
        widgets = {
            'attendance_percentage': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 85.0',
                'min': '0',
                'max': '100',
                'step': '0.1',
            }),
            'marks': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 75',
                'min': '0',
                'max': '100',
            }),
        }

    def clean_marks(self):
        marks = self.cleaned_data.get('marks')
        if marks is not None and (marks < 0 or marks > 100):
            raise ValidationError('Marks must be between 0 and 100.')
        return marks

    def clean_attendance_percentage(self):
        att = self.cleaned_data.get('attendance_percentage')
        if att is not None and (att < 0 or att > 100):
            raise ValidationError('Attendance must be between 0% and 100%.')
        return att


class TeacherEnrollStudentForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(role='student', is_active=True),
        widget=forms.Select(attrs={'class': 'form-input'}),
        empty_label="Select Student"
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-input'}),
        empty_label="Select Course"
    )

    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'attendance_percentage', 'marks']
        widgets = {
            'attendance_percentage': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 85.0',
                'min': '0',
                'max': '100',
                'step': '0.1',
            }),
            'marks': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 75',
                'min': '0',
                'max': '100',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        course = cleaned_data.get('course')
        if student and course:
            if Enrollment.objects.filter(student=student, course=course, status='active').exists():
                raise ValidationError(f'{student.username} is already enrolled in {course.code}.')
            if course.is_full:
                raise ValidationError(f'Course {course.code} is at full capacity.')
        return cleaned_data
