from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile, StudentDetail
from dashboard.models import Course, Enrollment, Announcement

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds initial users, profiles, courses, and announcements for EduPortal.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding EduPortal initial data...')

        # 1. Admin
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@eduportal.com',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_email_verified': True,
                'first_name': 'System',
                'last_name': 'Administrator',
            }
        )
        if created:
            admin.set_password('AdminPass123!')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created admin user (admin / AdminPass123!)'))
        Profile.objects.get_or_create(
            user=admin,
            defaults={'phone': '+91 9999999999', 'bio': 'EduPortal Lead Administrator'}
        )

        # 2. Student 1 (swaraj45)
        student1, created = User.objects.get_or_create(
            username='swaraj45',
            defaults={
                'email': 'swarajgondchawar@gmail.com',
                'role': 'student',
                'is_email_verified': True,
                'first_name': 'Swaraj',
                'last_name': 'Gondchawar',
            }
        )
        if created:
            student1.set_password('SwarajPass123!')
            student1.save()
            self.stdout.write(self.style.SUCCESS('Created student user (swaraj45 / SwarajPass123!)'))
        Profile.objects.get_or_create(
            user=student1,
            defaults={'phone': '+91 9876543211', 'bio': 'Computer Science Student'}
        )
        StudentDetail.objects.get_or_create(
            user=student1,
            defaults={
                'roll_number': 'CS2026001',
                'department': 'Computer Science',
                'year': '2',
                'semester': '3',
            }
        )

        # 3. Student 2 (student2)
        student2, created = User.objects.get_or_create(
            username='student2',
            defaults={
                'email': 'student2@eduportal.com',
                'role': 'student',
                'is_email_verified': True,
                'first_name': 'Rahul',
                'last_name': 'Sharma',
            }
        )
        if created:
            student2.set_password('StudentPass123!')
            student2.save()
            self.stdout.write(self.style.SUCCESS('Created student user (student2 / StudentPass123!)'))
        Profile.objects.get_or_create(
            user=student2,
            defaults={'phone': '+91 9876543212', 'bio': 'Engineering Freshman'}
        )
        StudentDetail.objects.get_or_create(
            user=student2,
            defaults={
                'roll_number': 'CS2026042',
                'department': 'Computer Science',
                'year': '1',
                'semester': '1',
            }
        )

        # 4. Teacher 1 (teacher1)
        teacher1, created = User.objects.get_or_create(
            username='teacher1',
            defaults={
                'email': 'teacher1@eduportal.com',
                'role': 'teacher',
                'is_email_verified': True,
                'first_name': 'Dr. Priya',
                'last_name': 'Kulkarni',
            }
        )
        if created:
            teacher1.set_password('TeacherPass123!')
            teacher1.save()
            self.stdout.write(self.style.SUCCESS('Created teacher user (teacher1 / TeacherPass123!)'))
        Profile.objects.get_or_create(
            user=teacher1,
            defaults={
                'phone': '+91 9876543210',
                'bio': 'Assistant Professor in Computer Science with 8+ years of teaching experience.',
                'address': 'Faculty Block B, Tech Campus',
            }
        )

        # 5. Courses
        courses_data = [
            ('CS101', 'Introduction to Computer Science', 'Computer Science', '1', 3, 60),
            ('CS102', 'Data Structures & Algorithms', 'Computer Science', '2', 3, 60),
            ('CS103', 'Database Management Systems', 'Computer Science', '3', 3, 60),
            ('EE101', 'Basic Electrical Engineering', 'Electrical Engineering', '1', 3, 60),
        ]
        created_courses = {}
        for code, name, dept, sem, cr, max_en in courses_data:
            c, _ = Course.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'department': dept,
                    'semester': sem,
                    'credits': cr,
                    'max_enrollment': max_en,
                    'is_active': True,
                }
            )
            created_courses[code] = c

        # 6. Sample Enrollments
        if 'CS101' in created_courses:
            Enrollment.objects.get_or_create(
                student=student1, course=created_courses['CS101'],
                defaults={'attendance_percentage': 92.5, 'marks': 94, 'status': 'active'}
            )
            Enrollment.objects.get_or_create(
                student=student2, course=created_courses['CS101'],
                defaults={'attendance_percentage': 88.0, 'marks': 82, 'status': 'active'}
            )
        if 'EE101' in created_courses:
            Enrollment.objects.get_or_create(
                student=student2, course=created_courses['EE101'],
                defaults={'attendance_percentage': 68.5, 'marks': 55, 'status': 'active'}
            )
        if 'CS102' in created_courses:
            Enrollment.objects.get_or_create(
                student=student1, course=created_courses['CS102'],
                defaults={'attendance_percentage': 95.0, 'marks': 95, 'status': 'active'}
            )
        if 'CS103' in created_courses:
            Enrollment.objects.get_or_create(
                student=student1, course=created_courses['CS103'],
                defaults={'attendance_percentage': 81.0, 'marks': 78, 'status': 'active'}
            )

        # 7. Sample Announcement
        Announcement.objects.get_or_create(
            title='Mid-Term Examination Schedule Released',
            defaults={
                'content': 'The mid-term examination timetable for Semester 1 to 4 has been published. All students must maintain at least 75% attendance to be eligible.',
                'posted_by': admin,
                'target_audience': 'all',
                'is_pinned': True,
            }
        )

        self.stdout.write(self.style.SUCCESS('Initial data seeding completed!'))
