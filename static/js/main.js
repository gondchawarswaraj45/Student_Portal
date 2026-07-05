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
`;
document.head.appendChild(style);
