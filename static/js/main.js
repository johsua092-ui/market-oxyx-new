document.addEventListener('DOMContentLoaded', function () {
    createParticles();
    addGlowOrbs();

    // Auto-hide alerts
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s, transform 0.5s';
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(30px)';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });

    // Ripple on buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
            ripple.style.top  = (e.clientY - rect.top  - size / 2) + 'px';
            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 700);
        });
    });

    // Password strength bar
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        const group = passwordInput.closest('.form-group');
        if (group) {
            const bar = document.createElement('div');
            bar.className = 'password-strength-bar';
            const fill = document.createElement('div');
            fill.className = 'password-strength-fill';
            bar.appendChild(fill);
            const label = document.createElement('div');
            label.className = 'password-strength-label';
            group.appendChild(bar);
            group.appendChild(label);
            passwordInput.addEventListener('input', function () {
                const score = checkPasswordStrength(this.value);
                const pct = Math.min((score / 7) * 100, 100);
                const colors = ['#e74c3c','#e67e22','#f1c40f','#f1c40f','#2ecc71','#27ae60','#1abc9c','#16a085'];
                const texts  = ['','Very Weak','Weak','Fair','Good','Strong','Very Strong','Max'];
                fill.style.width = pct + '%';
                fill.style.background = `linear-gradient(90deg, ${colors[score]}, ${colors[Math.min(score+1,7)]})`;
                label.textContent = score > 0 ? `Strength: ${texts[score]}` : '';
                label.style.color = colors[score];
            });
        }
    }

    // Scroll reveal
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                entry.target.style.transitionDelay = (i * 0.08) + 's';
                entry.target.classList.add('visible');
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });
    document.querySelectorAll('.feature-card, .dashboard-card, .stat-card, .auth-container, .admin-section').forEach(el => {
        el.classList.add('reveal');
        revealObserver.observe(el);
    });

    // Navbar darken on scroll
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            navbar.style.background = window.scrollY > 30
                ? 'rgba(10, 10, 26, 0.85)'
                : 'rgba(255, 255, 255, 0.03)';
        });
    }

    // Typewriter on hero subtitle
    const heroP = document.querySelector('.hero p');
    if (heroP) {
        const text = heroP.textContent.trim();
        heroP.textContent = '';
        const cursor = document.createElement('span');
        cursor.className = 'typing-cursor';
        heroP.appendChild(cursor);
        let i = 0;
        function typeChar() {
            if (i < text.length) {
                heroP.insertBefore(document.createTextNode(text[i++]), cursor);
                setTimeout(typeChar, 45);
            } else { setTimeout(() => cursor.remove(), 1500); }
        }
        setTimeout(typeChar, 600);
    }

    // Card 3D tilt
    document.querySelectorAll('.feature-card').forEach(card => {
        card.addEventListener('mousemove', function (e) {
            const r = this.getBoundingClientRect();
            const rx = ((e.clientY - r.top  - r.height/2) / (r.height/2)) * -8;
            const ry = ((e.clientX - r.left - r.width/2)  / (r.width/2))  *  8;
            this.style.transform = `translateY(-10px) scale(1.02) rotateX(${rx}deg) rotateY(${ry}deg)`;
        });
        card.addEventListener('mouseleave', function () { this.style.transform = ''; });
    });

    // Stat counter
    document.querySelectorAll('.stat-value').forEach(el => {
        const target = parseInt(el.textContent) || 0;
        if (target > 0) {
            el.textContent = '0';
            new IntersectionObserver(([entry], obs) => {
                if (entry.isIntersecting) { animateCount(el, 0, target, 1200); obs.disconnect(); }
            }).observe(el);
        }
    });

    // Mouse parallax on hero orbs
    const hero = document.querySelector('.hero');
    if (hero) {
        document.addEventListener('mousemove', (e) => {
            const mx = (e.clientX / window.innerWidth  - 0.5) * 30;
            const my = (e.clientY / window.innerHeight - 0.5) * 30;
            hero.querySelectorAll('.glow-orb').forEach((orb, i) => {
                const f = (i + 1) * 0.4;
                orb.style.transform = `translate(${mx*f}px, ${my*f}px)`;
            });
        });
    }
});

function checkPasswordStrength(p) {
    let s = 0;
    if (p.length >= 12) s++;
    if (p.length >= 16) s++;
    if (/[A-Z]/.test(p)) s++;
    if (/[a-z]/.test(p)) s++;
    if (/[0-9]/.test(p)) s++;
    if (/[^A-Za-z0-9]/.test(p)) s++;
    if (p.length > 0 && !/(password|123456|qwerty|admin)/i.test(p)) s++;
    return s;
}

function animateCount(el, start, end, duration) {
    const t0 = performance.now();
    (function update(now) {
        const p = Math.min((now - t0) / duration, 1);
        el.textContent = Math.round(start + (end - start) * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(update);
    })(t0);
}

function createParticles() {
    const c = document.createElement('div');
    c.className = 'particles-container';
    document.body.appendChild(c);
    const colors = ['rgba(102,126,234,0.6)','rgba(240,147,251,0.5)','rgba(118,75,162,0.5)','rgba(255,255,255,0.3)','rgba(52,152,219,0.5)'];
    for (let i = 0; i < 40; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        const size = Math.random() * 6 + 2;
        const col  = colors[Math.floor(Math.random() * colors.length)];
        p.style.cssText = `width:${size}px;height:${size}px;left:${Math.random()*100}%;background:${col};animation-duration:${Math.random()*15+10}s;animation-delay:${Math.random()*15}s;box-shadow:0 0 ${size*2}px ${col};`;
        c.appendChild(p);
    }
}

function addGlowOrbs() {
    const hero = document.querySelector('.hero');
    if (!hero) return;
    hero.style.position = 'relative';
    hero.style.overflow = 'hidden';
    ['glow-orb-1','glow-orb-2','glow-orb-3'].forEach(cls => {
        const orb = document.createElement('div');
        orb.className = `glow-orb ${cls}`;
        hero.appendChild(orb);
    });
}
