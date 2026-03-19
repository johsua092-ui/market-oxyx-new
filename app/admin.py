from flask import render_template, request, redirect, url_for, flash, session
from app.auth import login_required, db

def init_admin_routes(app):

    @app.route('/owner/dashboard')
    @login_required
    def owner_dashboard():
        if session.get('role') != 'owner':
            flash('Akses ditolak.', 'error')
            return redirect(url_for('index'))
        users = db.get_all_users()
        stats = {
            'total_users':    len(users),
            'active_sessions': len(db.get_active_sessions()),
            'staff_count':    len([u for u in users if u['role'] == 'staff']),
            'owner_count':    len([u for u in users if u['role'] == 'owner']),
        }
        return render_template('owner_dashboard.html',
            user=session, users=users,
            active_sessions=db.get_active_sessions(),
            invite_codes=db.get_invite_codes(),
            ip_bindings=db.ip_bindings, stats=stats)

    @app.route('/owner/generate-code', methods=['POST'])
    @login_required
    def generate_code():
        if session.get('role') != 'owner':
            flash('Akses ditolak.', 'error')
            return redirect(url_for('index'))
        role = request.form.get('role', 'staff')
        if role not in ('staff', 'owner'):
            flash('Role tidak valid.', 'error')
            return redirect(url_for('owner_dashboard'))
        code = db.generate_invite_code(role, session['user_id'])
        flash(f'Kode {role.upper()} berhasil dibuat: {code}', 'success')
        return redirect(url_for('owner_dashboard'))

    @app.route('/owner/ban/<int:user_id>', methods=['POST'])
    @login_required
    def ban_user(user_id):
        if session.get('role') != 'owner':
            flash('Akses ditolak.', 'error')
            return redirect(url_for('index'))
        target = db.get_user_by_id(user_id)
        if not target or target['role'] == 'owner':
            flash('Tidak bisa ban akun ini.', 'error')
            return redirect(url_for('owner_dashboard'))
        db.ban_user(user_id)
        flash(f'User {target["username"]} dibanned.', 'success')
        return redirect(url_for('owner_dashboard'))

    @app.route('/owner/unban/<int:user_id>', methods=['POST'])
    @login_required
    def unban_user(user_id):
        if session.get('role') != 'owner':
            flash('Akses ditolak.', 'error')
            return redirect(url_for('index'))
        target = db.get_user_by_id(user_id)
        if target:
            db.unban_user(user_id)
            flash(f'User {target["username"]} di-unban.', 'success')
        return redirect(url_for('owner_dashboard'))

    @app.route('/owner/reset-ip/<int:user_id>', methods=['POST'])
    @login_required
    def reset_ip(user_id):
        if session.get('role') != 'owner':
            flash('Akses ditolak.', 'error')
            return redirect(url_for('index'))
        target = db.get_user_by_id(user_id)
        if target:
            db.reset_ip_binding(user_id)
            db.invalidate_user_sessions(user_id)
            flash(f'IP {target["username"]} direset.', 'success')
        return redirect(url_for('owner_dashboard'))

    @app.route('/staff/dashboard')
    @login_required
    def staff_dashboard():
        if session.get('role') not in ('staff', 'owner'):
            flash('Akses ditolak.', 'error')
            return redirect(url_for('index'))
        from app.auth import get_client_ip
        ip = get_client_ip()
        return render_template('staff_dashboard.html',
            user=session, current_ip=ip,
            bound_ip=db.get_ip_binding(session['user_id']),
            users=db.get_all_users())
