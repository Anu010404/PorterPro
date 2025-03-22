from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False, default='customer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Porter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_number = db.Column(db.String(20), nullable=False)
    station = db.Column(db.String(100), nullable=False)
    photo_path = db.Column(db.String(255))
    available = db.Column(db.Boolean, default=True)
    current_location = db.Column(db.String(100))
    rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Add unique constraint for badge number per station
    __table_args__ = (
        db.UniqueConstraint('badge_number', 'station', name='unique_badge_station'),
    )

    user = db.relationship('User', backref=db.backref('porter', uselist=False))
    bookings = db.relationship('Booking', backref='porter', lazy=True)
    ratings = db.relationship('Rating', backref='porter', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    porter_id = db.Column(db.Integer, db.ForeignKey('porter.id'), nullable=False)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, in_progress, completed, cancelled
    weight = db.Column(db.Float, nullable=False)
    trolley_required = db.Column(db.Boolean, default=False)
    number_of_bags = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='pending')
    stripe_session_id = db.Column(db.String(100))
    otp = db.Column(db.String(6))
    otp_expiry = db.Column(db.DateTime)
    otp_verified = db.Column(db.Boolean, default=False)
    meeting_point = db.Column(db.String(200))  # Where to meet at the station
    meeting_time = db.Column(db.DateTime)  # When to meet

    rating = db.relationship('Rating', backref='booking', lazy=True, uselist=False)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    porter_id = db.Column(db.Integer, db.ForeignKey('porter.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)