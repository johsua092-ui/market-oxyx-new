/* ============================================================
   NEMESIS-X CORE — main.js (Marketplace BABFT Edition)
============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    // Inisialisasi Seluruh Sistem
    spawnParticles();
    addGlowOrbs();
    initAlerts();
    initRipple();
    initPasswordStrength();
    initScrollReveal();
    initNavbarScroll();
    initTypewriter();
    initCardTilt();
    initStatCounters();
    initParallaxOrbs();
});

/* --- 1. PARTICLE SYSTEM --- */
function spawnParticles() {
    const wrap = document.createElement('div');
    wrap.className = 'particles-container';
    document.body.prepend(wrap);

    const palette = [
        'rgba(102,126,234,0.55)',
        'rgba(240,147,251,0.45)',
        'rgba(118,75,162,0.45)',
        'rgba(255,255,255,0.22)',
        'rgba(79,172,254,0.45)',
    ];

    for (let i = 0; i < 45; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        const sz = Math.random() * 5 + 1.5;
        const col = palette[Math.floor(Math.random() * palette.length)];

        Object.assign(p.style, {
            width: sz + 'px',
            height: sz + 'px',
            left: (Math.random() * 100) + '%',
            background: col,
            position: 'absolute',
            animationDuration: (Math.random() * 18 + 10) + 's',
            animationDelay: (Math.random() * 18) + 's',
            boxShadow: `0 0 ${sz * 2.5}px ${col}`,
        });
        wrap.appendChild(p);
    }
}

/* --- 2. ALERT AUTO-DISMISS --- */
function initAlerts() {
    document.querySelectorAll('.alert').forEach((el, i) => {
        setTimeout(() => {
            el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            el.style.opacity = '0';
            el.style.transform = 'translateX(32px)';
            setTimeout(() => el.remove(), 520);
        }, 3800 + (i * 300));
    });
}

/* --- 3. BUTTON RIPPLE EFFECT --- */
function initRipple() {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn');
        if (!btn) return;

        const r = document.createElement('span');
        r.className = 'ripple-effect';
        const rect = btn.getBoundingClientRect();
        const sz = Math.max(rect.width, rect.height);

        Object.assign(r.style, {
            width: sz + 'px',
            height: sz + 'px',
            left: (e.clientX - rect.left - sz / 2) + 'px',
            top: (e.clientY - rect.top - sz / 2) + 'px',
            position: 'absolute',
            borderRadius: '50%',
            backgroundColor: 'rgba(255, 255, 255, 0.3)',
            transform: 'scale(0)',
            animation: 'ripple 0.6s linear',
            pointerEvents: 'none'
        });

        btn.style.position = 'relative';
        btn.style.overflow = 'hidden';
        btn.appendChild(r);
        setTimeout(() => r.remove(), 680);
    });
}

/* --- 4. PASSWORD STRENGTH --- */
function initPasswordStrength() {
    const passwordInput = document.getElementById('password');
    if (!passwordInput) return;

    const group = passwordInput.closest('.form-group') || passwordInput.parentElement;
    const bar = document.createElement('div');
    bar.className = 'password-strength-bar';
    const fill = document.createElement('div');
    fill.className = 'password-strength-fill';
    
    // Styling dasar via JS jika CSS belum ada
    bar.style.height = '4px';
    bar.style.background = 'rgba(255,255,255,0.1)';
    bar.style.marginTop = '8px';
    bar.style.borderRadius = '2px';
    fill.style.height = '100%';
    fill.style.width = '0%';
    fill.style.transition = 'all 0.3s ease';

    bar.appendChild(fill);
    group.appendChild(bar);

    passwordInput.addEventListener('input', function() {
        let score = 0;
        const val = this.value;
        if (val.length >= 8) score++;
        if (/[A-Z]/.test(val)) score++;
        if (/[0-9]/.test(val)) score++;
        if (/[^A-Za-z0-9]/.test(val)) score++;

        const colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71'];
        fill.style.width = (score * 25) + '%';
        fill.style.backgroundColor = colors[score - 1] || '#e74c3c';
    });
}

/* --- 5. INTERACTIVE EFFECTS --- */
function initCardTilt() {
    document.querySelectorAll('.feature-card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const cx = rect.width / 2;
            const cy = rect.height / 2;
            const rotX = ((y - cy) / cy) * -10;
            const rotY = ((x - cx) / cx) * 10;
            card.style.transform = `perspective(1000px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateY(-5px)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
        });
    });
}

function initNavbarScroll() {
    const nav = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.style.background = 'rgba(10, 10, 26, 0.95)';
            nav.style.padding = '0.7rem 0';
        } else {
            nav.style.background = 'rgba(10, 10, 26, 0.55)';
            nav.style.padding = '0.95rem 0';
        }
    });
}

// Tambahkan fungsi kosong agar tidak error jika dipanggil tapi belum diisi
function addGlowOrbs() {}
function initScrollReveal() {}
function initTypewriter() {}
function initStatCounters() {}
function initParallaxOrbs() {}
