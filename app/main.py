from flask import render_template, redirect, url_for, session
from app.auth import login_required, db

def init_main_routes(app):

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        user = db.get_user_by_id(session['user_id'])
        if not user:
            return redirect(url_for('login'))
        if user['role'] == 'owner': return redirect(url_for('owner_dashboard'))
        if user['role'] == 'staff': return redirect(url_for('staff_dashboard'))
        return render_template('dashboard.html', user=user)
