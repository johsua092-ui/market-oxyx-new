import os
import re
import base64
import secrets
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import render_template, request, redirect, url_for, session, flash, g


class SimpleDB:
    def __init__(self):
        self.users = {}
        self.sessions = {}
        self.login_attempts = {}
        self.password_history = {}
        self.invite_codes = {}
        self.ip_bindings = {}
        self.user_id_counter = 1
        self.session_id_counter = 1
        self._owner_created = False

    def ensure_owner(self):
        if self._owner_created:
            return
        self._owner_created = True
        for user in self.users.values():
            if user['role'] == 'owner':
                return
        password = secrets.token_urlsafe(16)
        password_hash = generate_password_hash(password)
        user_id = self.user_id_counter
        self.user_id_counter += 1
        user = {
            'id': user_id, 'username': 'owner',
            'password': password_hash, 'email': 'owner@oxyx.local',
            'join_date': datetime.now().isoformat(), 'registration_ip': '127.0.0.1',
            'last_ip': None, 'role': 'owner', 'is_banned': False,
            'failed_attempts': 0, 'locked_until': None, 'last_login': None
        }
        self.users[user_id] = user
        self.password_history[user_id] = [password_hash]
        with open('owner_credentials.txt', 'w') as f:
            f.write("OXYX BUILDS - OWNER CREDENTIALS\n")
            f.write("=" * 40 + "\n")
            f.write(f"Username: owner\n")
            f.write(f"Password: {password}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 40 + "\n")
            f.write("DELETE THIS FILE AFTER SAVING!\n")
        print("=" * 60)
        print(f"OWNER CREATED  |  Username: owner  |  Password: {password}")
        print("=" * 60)

    def get_user_by_username(self, username):
        for user in self.users.values():
            if user.get('username') == username:
                return user
        return None

    def get_user_by_id(self, user_id):
        return self.users.get(user_id)

    def create_user(self, username, password_hash, email, ip, role='user'):
        user_id = self.user_id_counter
        self.user_id_counter += 1
        user = {
            'id': user_id, 'username': username, 'password': password_hash,
            'email': email, 'join_date': datetime.now().isoformat(),
            'registration_ip': ip, 'last_ip': None, 'role': role,
            'is_banned': False, 'failed_attempts': 0,
            'locked_until': None, 'last_login': None
        }
        self.users[user_id] = user
        self.password_history[user_id] = [password_hash]
        return user

    def create_session(self, user_id, ip, user_agent):
        session_id = self.session_id_counter
        self.session_id_counter += 1
        fingerprint = hashlib.sha256(
            f"{ip}|{user_agent}|{secrets.token_hex(8)}".encode()).hexdigest()
        session_data = {
            'id': session_id, 'user_id': user_id, 'ip': ip,
            'user_agent': user_agent, 'fingerprint': fingerprint,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(minutes=30)).isoformat()
        }
        self.sessions[session_id] = session_data
        return session_id, fingerprint

    def validate_session(self, session_id, ip, user_agent, fingerprint):
        session_data = self.sessions.get(session_id)
        if not session_data:
            return None
        if datetime.now() > datetime.fromisoformat(session_data['expires_at']):
            self.invalidate_session(session_id)
            return None
        session_data['last_activity'] = datetime.now().isoformat()
        session_data['expires_at'] = (datetime.now() + timedelta(minutes=30)).isoformat()
        return session_data

    def invalidate_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def invalidate_user_sessions(self, user_id, exclude_session=None):
        to_delete = [sid for sid, s in self.sessions.items()
                     if s['user_id'] == user_id and sid != exclude_session]
        for sid in to_delete:
            del self.sessions[sid]

    def record_login_attempt(self, ip, username, success):
        key = f"{ip}:{username}"
        if key not in self.login_attempts:
            self.login_attempts[key] = []
        self.login_attempts[key].append({'timestamp': time.time(), 'success': success})
        self.login_attempts[key] = [
            a for a in self.login_attempts[key] if time.time() - a['timestamp'] < 3600]

    def check_rate_limit(self, ip, username):
        key = f"{ip}:{username}"
        if key not in self.login_attempts:
            return True
        now = time.time()
        recent = [a for a in self.login_attempts[key]
                  if not a['success'] and now - a['timestamp'] < 900]
        return len(recent) < 5

    def generate_invite_code(self, role, created_by_id):
        code = secrets.token_urlsafe(12).upper()
        self.invite_codes[code] = {
            'code': code, 'role': role, 'used': False,
            'used_by': None, 'created_by': created_by_id,
            'created_at': datetime.now().isoformat()
        }
        return code

    def use_invite_code(self, code):
        entry = self.invite_codes.get(code.upper().strip())
        if not entry or entry['used']:
            return None
        return entry

    def mark_code_used(self, code, user_id):
        entry = self.invite_codes.get(code.upper().strip())
        if entry:
            entry['used'] = True
            entry['used_by'] = user_id

    def get_ip_binding(self, user_id):
        return self.ip_bindings.get(user_id)

    def set_ip_binding(self, user_id, ip):
        self.ip_bindings[user_id] = ip

    def reset_ip_binding(self, user_id):
        self.ip_bindings.pop(user_id, None)

    def get_all_users(self):
        return list(self.users.values())

    def get_active_sessions(self):
        now = datetime.now()
        active = []
        for sess in self.sessions.values():
            if now <= datetime.fromisoformat(sess['expires_at']):
                user = self.get_user_by_id(sess['user_id'])
                active.append({**sess,
                    'username': user['username'] if user else '?',
                    'role': user['role'] if user else '?'})
        return active

    def get_invite_codes(self):
        return list(self.invite_codes.values())

    def ban_user(self, user_id):
        user = self.users.get(user_id)
        if user:
            user['is_banned'] = True
            self.invalidate_user_sessions(user_id)

    def unban_user(self, user_id):
        user = self.users.get(user_id)
        if user:
            user['is_banned'] = False


db = SimpleDB()


def generate_password_hash(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=64)
    return base64.b64encode(salt + key).decode('ascii')


def verify_password(password, hashed):
    try:
        decoded = base64.b64decode(hashed.encode('ascii'))
        salt, key = decoded[:32], decoded[32:]
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=64)
        return hmac.compare_digest(key, new_key)
    except Exception:
        return False


def validate_password_strength(password):
    errors = []
    if len(password) < 12:         errors.append("Password minimal 12 karakter")
    if not re.search(r'[A-Z]', password): errors.append("Harus ada huruf kapital")
    if not re.search(r'[a-z]', password): errors.append("Harus ada huruf kecil")
    if not re.search(r'\d', password):    errors.append("Harus ada angka")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password): errors.append("Harus ada karakter spesial")
    if any(p in password.lower() for p in ['password','123456','qwerty','admin']):
        errors.append("Password mengandung pola umum")
    return errors


def get_client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'error')
            return redirect(url_for('login'))
        session_id = session.get('_session_id')
        if not session_id:
            session.clear()
            flash('Sesi tidak valid.', 'error')
            return redirect(url_for('login'))
        sess = db.validate_session(session_id, get_client_ip(),
                                   request.headers.get('User-Agent',''),
                                   session.get('_fingerprint'))
        if not sess:
            session.clear()
            flash('Sesi berakhir.', 'error')
            return redirect(url_for('login'))
        user = db.get_user_by_id(session['user_id'])
        if not user or user.get('is_banned'):
            session.clear()
            flash('Akun tidak ditemukan atau dibanned.', 'error')
            return redirect(url_for('login'))
        g.user = user
        return f(*args, **kwargs)
    return decorated


def init_auth_routes(app):
    db.ensure_owner()

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if 'user_id' in session:
            return redirect(url_for('index'))
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            ip = get_client_ip()

            if not db.check_rate_limit(ip, username):
                flash('Terlalu banyak percobaan. Coba lagi nanti.', 'error')
                return render_template('login.html')

            user = db.get_user_by_username(username)
            password_valid = user and verify_password(password, user['password'])
            db.record_login_attempt(ip, username, password_valid)

            if user and password_valid:
                if user.get('is_banned'):
                    flash('Akun kamu telah dibanned.', 'error')
                    return render_template('login.html')
                if user.get('locked_until'):
                    if datetime.now() < datetime.fromisoformat(user['locked_until']):
                        flash('Akun terkunci. Coba lagi nanti.', 'error')
                        return render_template('login.html')

                if user['role'] in ('staff', 'owner'):
                    bound_ip = db.get_ip_binding(user['id'])
                    if bound_ip is None:
                        db.set_ip_binding(user['id'], ip)
                    elif bound_ip != ip:
                        flash(f'Akses ditolak. IP {ip} tidak diizinkan untuk akun ini.', 'error')
                        return render_template('login.html')

                user['failed_attempts'] = 0
                user['locked_until'] = None
                db.invalidate_user_sessions(user['id'])

                session_id, fingerprint = db.create_session(
                    user['id'], ip, request.headers.get('User-Agent', ''))
                session.permanent = True
                session['user_id']      = user['id']
                session['username']     = user['username']
                session['role']         = user['role']
                session['_session_id']  = session_id
                session['_fingerprint'] = fingerprint
                user['last_login'] = datetime.now().isoformat()
                user['last_ip']    = ip

                flash(f'Selamat datang, {user["username"]}!', 'success')
                if user['role'] == 'owner': return redirect(url_for('owner_dashboard'))
                if user['role'] == 'staff': return redirect(url_for('staff_dashboard'))
                return redirect(url_for('index'))
            else:
                if user:
                    user['failed_attempts'] = user.get('failed_attempts', 0) + 1
                    if user['failed_attempts'] >= 5:
                        user['locked_until'] = (datetime.now() + timedelta(minutes=30)).isoformat()
                        flash('Akun terkunci 30 menit.', 'error')
                        return render_template('login.html')
                flash('Username atau password salah!', 'error')
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if 'user_id' in session:
            return redirect(url_for('index'))
        if request.method == 'POST':
            username     = request.form.get('username', '').strip()
            password     = request.form.get('password', '')
            confirm      = request.form.get('confirm_password', '')
            email        = request.form.get('email', '').strip()
            invite_code  = request.form.get('invite_code', '').strip()
            ip = get_client_ip()

            if not username or len(username) < 3:
                flash('Username minimal 3 karakter.', 'error')
                return render_template('register.html')
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                flash('Username hanya huruf, angka, underscore.', 'error')
                return render_template('register.html')
            if db.get_user_by_username(username):
                flash('Username sudah dipakai!', 'error')
                return render_template('register.html')

            for err in validate_password_strength(password):
                flash(err, 'error')
            if validate_password_strength(password):
                return render_template('register.html')

            if password != confirm:
                flash('Password tidak sama!', 'error')
                return render_template('register.html')

            role = 'user'
            code_entry = None
            if invite_code:
                code_entry = db.use_invite_code(invite_code)
                if not code_entry:
                    flash('Kode undangan tidak valid atau sudah dipakai!', 'error')
                    return render_template('register.html')
                role = code_entry['role']

            user = db.create_user(username, generate_password_hash(password), email, ip, role)
            if code_entry:
                db.mark_code_used(invite_code.upper().strip(), user['id'])

            flash(f'Registrasi berhasil sebagai {role}! Silakan login.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/logout')
    def logout():
        session_id = session.get('_session_id')
        if session_id:
            db.invalidate_session(session_id)
        session.clear()
        flash('Kamu telah logout.', 'info')
        return redirect(url_for('index'))
