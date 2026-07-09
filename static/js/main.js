/* =============================================
   EduPortal — JavaScript
   ============================================= */

document.addEventListener('DOMContentLoaded', function() {

    // --- Mobile Navigation Toggle ---
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            this.classList.toggle('active');
        });

        // Close menu on link click
        navMenu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });
    }

    // --- Navbar Scroll Effect ---
    const navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // --- Auto-dismiss alerts ---
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach((alert, index) => {
        setTimeout(() => {
            alert.style.animation = 'slideOutRight 0.3s ease forwards';
            setTimeout(() => alert.remove(), 300);
        }, 4000 + (index * 500));
    });

    // --- Fade In on Scroll ---
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animateElements = document.querySelectorAll(
        '.feature-card, .role-card, .stat-card, .dashboard-card'
    );
    animateElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = `all 0.6s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1}s`;
        observer.observe(el);
    });

    // --- Password Visibility Toggle ---
    document.querySelectorAll('.form-input[type="password"]').forEach(input => {
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        const toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.innerHTML = '<i class="fas fa-eye"></i>';
        toggle.style.cssText = `
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 0.9rem;
            padding: 4px;
        `;

        toggle.addEventListener('click', function() {
            if (input.type === 'password') {
                input.type = 'text';
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                input.type = 'password';
                this.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });

        wrapper.appendChild(toggle);
    });

    // --- Light/Dark Theme Toggle ---
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');

    if (themeToggle && themeIcon) {
        // Retrieve stored theme
        const currentTheme = localStorage.getItem('theme') || 'dark';

        if (currentTheme === 'light') {
            document.body.classList.add('light-theme');
            themeIcon.className = 'fas fa-moon';
        } else {
            document.body.classList.remove('light-theme');
            themeIcon.className = 'fas fa-sun';
        }

        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('light-theme');
            
            let theme = 'dark';
            if (document.body.classList.contains('light-theme')) {
                theme = 'light';
                themeIcon.className = 'fas fa-moon';
            } else {
                themeIcon.className = 'fas fa-sun';
            }
            
            localStorage.setItem('theme', theme);
        });
    }

});

// Add slideOutRight animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        to {
            opacity: 0;
            transform: translateX(40px);
        }
    }
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(40px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    .animated-slide-in {
        animation: fadeInSlideUp 0.4s ease forwards;
    }
`;
document.head.appendChild(style);


/* =============================================
   UPGRADED FEATURES INTERACTIVE LOGIC (AJAX & UI)
   ============================================= */

document.addEventListener('DOMContentLoaded', function() {
    
    // CSRF Token Helper
    function getCSRFToken() {
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        if (input) return input.value;
        
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === ('csrftoken=')) {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // --- Modal Handler ---
    const modalOpenBtns = document.querySelectorAll('[data-modal-target]');
    const modalCloseBtns = document.querySelectorAll('.edu-modal-close, [data-modal-close]');
    const modals = document.querySelectorAll('.edu-modal');

    modalOpenBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('data-modal-target');
            const targetModal = document.getElementById(targetId);
            if (targetModal) {
                targetModal.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        });
    });

    modalCloseBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.edu-modal');
            if (modal) {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });

    // Close on click outside modal content
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });

    // --- Tab Switcher ---
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetPanelId = this.getAttribute('data-tab-target');
            const container = this.closest('.dashboard-container') || document.body;
            
            // Deactivate all sibling buttons
            const tabList = this.closest('.tab-controls');
            if (tabList) {
                tabList.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            }
            
            // Deactivate all panels in this container
            const panels = container.querySelectorAll('.tab-panel');
            panels.forEach(p => p.classList.remove('active'));
            
            // Activate current
            this.classList.add('active');
            const targetPanel = document.getElementById(targetPanelId);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });

    // --- AJAX Course Registration (Student) ---
    const registerBtns = document.querySelectorAll('.btn-register-course');
    const enrollmentContainer = document.getElementById('enrollmentsContainer');
    const emptyEnrollmentState = document.getElementById('emptyEnrollmentState');

    registerBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const courseId = this.getAttribute('data-course-id');
            const card = this.closest('.course-card-premium') || this.closest('.stat-card');
            
            // Visual loading state
            this.disabled = true;
            const originalHtml = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enrolling...';

            const formData = new FormData();
            formData.append('course_id', courseId);

            fetch('/dashboard/course/register/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    
                    // Animate out card from directory
                    if (card) {
                        card.style.transform = 'scale(0.9) translateY(20px)';
                        card.style.opacity = '0';
                        setTimeout(() => {
                            card.remove();
                            // If no more courses in directory, show empty state
                            const directoryGrid = document.querySelector('.courses-grid-directory');
                            if (directoryGrid && directoryGrid.children.length === 0) {
                                const container = directoryGrid.closest('.dashboard-card');
                                if (container) {
                                    container.innerHTML = `
                                        <div class="empty-state">
                                            <i class="fas fa-book-open"></i>
                                            <p>No available courses left to register.</p>
                                        </div>
                                    `;
                                }
                            }
                        }, 300);
                    }

                    // Remove empty enrollments placeholder if it exists
                    if (emptyEnrollmentState) {
                        emptyEnrollmentState.remove();
                    }

                    // Dynamically append new course to enrollments list
                    if (enrollmentContainer) {
                        const courseInfo = data.course;
                        const newCourseHtml = `
                            <div class="course-item animated-slide-in" id="course-enrollment-${courseInfo.id}">
                                <div class="course-info">
                                    <span class="course-code">${courseInfo.code}</span>
                                    <span class="course-name">${courseInfo.name}</span>
                                </div>
                                <div class="course-metrics">
                                    <div class="metric-progress">
                                        <div class="progress-info">
                                            <span>Attendance</span>
                                            <strong>100.0%</strong>
                                        </div>
                                        <div class="progress-bar-track">
                                            <div class="progress-bar-fill" style="width: 100%"></div>
                                        </div>
                                    </div>
                                    <div class="metric-score">
                                        <div class="score-badge">
                                            <span>Grade</span>
                                            <strong>N/A</strong>
                                        </div>
                                        <div class="score-badge">
                                            <span>Marks</span>
                                            <strong>0/100</strong>
                                        </div>
                                    </div>
                                    <div class="course-actions-cell" style="margin-left: 12px; display: flex; align-items: center;">
                                        <button class="btn btn-outline btn-sm btn-drop-course" data-course-id="${courseInfo.id}" style="color: var(--accent-red); border-color: rgba(239, 68, 68, 0.3); padding: 4px 8px;">
                                            <i class="fas fa-trash"></i> Drop
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `;
                        enrollmentContainer.insertAdjacentHTML('beforeend', newCourseHtml);
                        
                        // Bind drop event to the new button
                        const newDropBtn = document.querySelector(`#course-enrollment-${courseInfo.id} .btn-drop-course`);
                        if (newDropBtn) {
                            bindDropEvent(newDropBtn);
                        }
                    }
                } else {
                    showNotification(data.message, 'danger');
                    this.disabled = false;
                    this.innerHTML = originalHtml;
                }
            })
            .catch(err => {
                console.error(err);
                showNotification('An error occurred during enrollment.', 'danger');
                this.disabled = false;
                this.innerHTML = originalHtml;
            });
        });
    });

    // --- AJAX Course Drop ---
    function bindDropEvent(btn) {
        btn.addEventListener('click', function() {
            if (!confirm('Are you sure you want to drop this course? All attendance and grades will be deleted.')) {
                return;
            }

            const courseId = this.getAttribute('data-course-id');
            const row = this.closest('.course-item') || this.closest('tr');
            
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

            fetch(`/dashboard/course/${courseId}/drop/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    
                    if (row) {
                        row.style.transform = 'translateX(-30px)';
                        row.style.opacity = '0';
                        setTimeout(() => {
                            row.remove();
                            // If no courses left, reload to show empty state
                            if (enrollmentContainer && enrollmentContainer.children.length === 0) {
                                location.reload();
                            }
                        }, 300);
                    }
                } else {
                    showNotification(data.message, 'danger');
                    this.disabled = false;
                    this.innerHTML = '<i class="fas fa-trash"></i> Drop';
                }
            })
            .catch(err => {
                console.error(err);
                showNotification('An error occurred.', 'danger');
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-trash"></i> Drop';
            });
        });
    }

    // Bind initial drop buttons
    document.querySelectorAll('.btn-drop-course').forEach(btn => bindDropEvent(btn));

    // --- AJAX Notice Deletion ---
    const deleteNoticeBtns = document.querySelectorAll('.feed-item-delete');
    deleteNoticeBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            if (!confirm('Are you sure you want to delete this announcement?')) return;

            const noticeId = this.getAttribute('data-notice-id');
            const feedItem = this.closest('.feed-item-premium') || this.closest('.feed-item');

            fetch(`/dashboard/announcement/${noticeId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    if (feedItem) {
                        feedItem.style.transform = 'scale(0.9)';
                        feedItem.style.opacity = '0';
                        setTimeout(() => {
                            feedItem.remove();
                            // Check if feed is empty
                            const feed = document.querySelector('.announcements-feed');
                            if (feed && feed.children.length === 0) {
                                const cardBody = feed.closest('.card-body');
                                if (cardBody) {
                                    cardBody.innerHTML = `
                                        <div class="empty-state">
                                            <i class="fas fa-bell-slash"></i>
                                            <p>No new announcements at this time.</p>
                                        </div>
                                    `;
                                }
                            }
                        }, 300);
                    }
                } else {
                    showNotification(data.message, 'danger');
                }
            })
            .catch(err => {
                console.error(err);
                showNotification('Error deleting announcement.', 'danger');
            });
        });
    });

    // --- AJAX Teacher Student Performance Update ---
    const performanceForms = document.querySelectorAll('.form-performance-edit');
    performanceForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const submitBtn = this.querySelector('[type=submit]');
            const originalBtnText = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';

            const actionUrl = this.getAttribute('action');
            const formData = new FormData(this);

            fetch(actionUrl, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken()
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    
                    // Close the modal
                    const modal = this.closest('.edu-modal');
                    if (modal) {
                        modal.classList.remove('active');
                        document.body.style.overflow = '';
                    }

                    // Update values on the table/UI dynamically
                    const perf = data.performance;
                    const row = document.getElementById(`enrollment-row-${perf.id}`);
                    if (row) {
                        const attCell = row.querySelector('.perf-attendance');
                        const marksCell = row.querySelector('.perf-marks');
                        const gradeCell = row.querySelector('.perf-grade');
                        
                        if (attCell) attCell.innerText = perf.attendance + '%';
                        if (marksCell) marksCell.innerText = perf.marks + '/100';
                        if (gradeCell) gradeCell.innerText = perf.grade;
                    }
                } else {
                    let errMsg = 'Update failed: ';
                    if (data.errors) {
                        for (const key in data.errors) {
                            errMsg += `${key}: ${data.errors[key].join(', ')} `;
                        }
                    }
                    showNotification(errMsg, 'danger');
                }
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            })
            .catch(err => {
                console.error(err);
                showNotification('An error occurred while updating performance.', 'danger');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            });
        });
    });

    // Helper Notification function
    function showNotification(message, type = 'success') {
        const container = document.querySelector('.messages-container');
        if (!container) {
            const main = document.body;
            const newContainer = document.createElement('div');
            newContainer.className = 'messages-container';
            main.appendChild(newContainer);
        }
        
        const messageContainer = document.querySelector('.messages-container');
        const alertId = 'alert-dynamic-' + Date.now();
        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
        
        const alertHtml = `
            <div class="alert alert-${type}" id="${alertId}" style="animation: slideInRight 0.3s ease forwards;">
                <div class="alert-content">
                    <i class="fas ${icon}"></i>
                    <span>${message}</span>
                </div>
                <button class="alert-close" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        messageContainer.insertAdjacentHTML('beforeend', alertHtml);
        
        setTimeout(() => {
            const alertEl = document.getElementById(alertId);
            if (alertEl) {
                alertEl.style.animation = 'slideOutRight 0.3s ease forwards';
                setTimeout(() => alertEl.remove(), 300);
            }
        }, 4000);
    }
});

