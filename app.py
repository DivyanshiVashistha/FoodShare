"""
FoodShare - A platform to connect food donors with those in need
Main Flask application file
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///foodshare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Admin password (in production, use environment variables and hashing)
ADMIN_PASSWORD = 'admin123'

# Database Models
class Donor(db.Model):
    """Model for storing donor information"""
    __tablename__ = 'donors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    food_details = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Donor {self.name}>'

class Feedback(db.Model):
    """Model for storing user feedback"""
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Feedback from {self.name}>'

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    """Home page route"""
    return render_template('home.html')

@app.route('/donate', methods=['GET', 'POST'])
def donate():
    """Donation form route - handles both display and submission"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        food_details = request.form.get('food_details')
        
        # Create new donor record
        new_donor = Donor(
            name=name,
            phone=phone,
            address=address,
            food_details=food_details
        )
        
        # Save to database
        try:
            db.session.add(new_donor)
            db.session.commit()
            flash('Thank you for your generous donation! We will contact you soon.', 'success')
            return redirect(url_for('thank_you', type='donation'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('donate'))
    
    return render_template('donate.html')

@app.route('/about')
def about():
    """About page route"""
    return render_template('about.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Feedback form route - handles both display and submission"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Create new feedback record
        new_feedback = Feedback(
            name=name,
            email=email,
            message=message
        )
        
        # Save to database
        try:
            db.session.add(new_feedback)
            db.session.commit()
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('thank_you', type='feedback'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('feedback'))
    
    return render_template('feedback.html')

@app.route('/thank-you/<type>')
def thank_you(type):
    """Thank you page after successful submission"""
    return render_template('thank_you.html', type=type)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Admin dashboard route - password protected"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            return redirect(url_for('admin'))
        else:
            flash('Incorrect password', 'error')
            return redirect(url_for('admin'))
    
    # Check if admin is authenticated
    if not session.get('admin_authenticated'):
        return render_template('admin_login.html')
    
    # Get all donors and feedback
    donors = Donor.query.order_by(Donor.timestamp.desc()).all()
    feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    
    return render_template('admin.html', donors=donors, feedbacks=feedbacks)

@app.route('/admin/logout')
def admin_logout():
    """Logout from admin dashboard"""
    session.pop('admin_authenticated', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))

# Error handlers
@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)