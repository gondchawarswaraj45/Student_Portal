from django import forms
from .models import Announcement, Course, Enrollment
from accounts.models import User

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'target_audience']
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
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'department', 'semester']
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
        }

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['attendance_percentage', 'grade', 'marks']
        widgets = {
            'attendance_percentage': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 85.0',
                'min': '0',
                'max': '100',
                'step': '0.1',
            }),
            'grade': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. A+, B, C',
            }),
            'marks': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 75',
                'min': '0',
                'max': '100',
            }),
        }

class TeacherEnrollStudentForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(role='student'),
        widget=forms.Select(attrs={'class': 'form-input'}),
        empty_label="Select Student"
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={'class': 'form-input'}),
        empty_label="Select Course"
    )

    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'attendance_percentage', 'grade', 'marks']
        widgets = {
            'attendance_percentage': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 85.0',
                'min': '0',
                'max': '100',
                'step': '0.1',
            }),
            'grade': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. A+, B, C',
            }),
            'marks': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 75',
                'min': '0',
                'max': '100',
            }),
        }
