from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, stripe
import os
from models import User, Porter, Booking, Rating
from forms import LoginForm, RegistrationForm, BookingForm, RatingForm, OTPVerificationForm
from utils import calculate_price, generate_pdf_pass, generate_otp, send_otp_sms, verify_otp
from datetime import datetime, timedelta

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid email or password')
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        
        if form.role.data == 'porter':
            porter = Porter(
                user_id=user.id,
                badge_number=f"P{user.id:05d}"
            )
            db.session.add(porter)
            
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)

@app.route('/booking/new', methods=['GET', 'POST'])
@login_required
def new_booking():
    form = BookingForm()
    if form.validate_on_submit():
        # Calculate price
        total_amount = calculate_price(
            form.weight.data,
            form.number_of_bags.data,
            form.trolley_required.data
        )
        
        # Create Stripe checkout session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'unit_amount': int(total_amount * 100),
                        'product_data': {
                            'name': 'Porter Service',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.host_url + 'booking/success',
                cancel_url=request.host_url + 'booking/cancel',
            )
            
            # Generate OTP
            otp = generate_otp()
            
            # Create booking
            booking = Booking(
                user_id=current_user.id,
                porter_id=Porter.query.filter_by(available=True).first().id,
                weight=form.weight.data,
                trolley_required=form.trolley_required.data,
                number_of_bags=form.number_of_bags.data,
                price=total_amount,
                stripe_session_id=checkout_session.id,
                otp=otp,
                otp_expiry=form.meeting_time.data + timedelta(minutes=30),  # OTP valid for 30 minutes after meeting time
                meeting_point=form.meeting_point.data,
                meeting_time=form.meeting_time.data
            )
            db.session.add(booking)
            db.session.commit()
            
            # Send OTP via SMS
            if send_otp_sms(current_user.phone, otp):
                flash('Booking confirmed! Please check your SMS for the OTP to share with the porter.')
                return redirect(url_for('track_booking', booking_id=booking.id))
            else:
                flash('Failed to send OTP. Please try again.')
                return redirect(url_for('new_booking'))
            
        except Exception as e:
            flash('Payment processing failed. Please try again.')
            return redirect(url_for('new_booking'))
            
    return render_template('booking/new.html', form=form)

@app.route('/booking/<int:booking_id>/track')
@login_required
def track_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('booking/tracking.html', booking=booking)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    bookings = Booking.query.all()
    porters = Porter.query.all()
    return render_template('admin/dashboard.html', bookings=bookings, porters=porters)

@app.route('/booking/<int:booking_id>/rate', methods=['POST'])
@login_required
def rate_booking(booking_id):
    form = RatingForm()
    if form.validate_on_submit():
        booking = Booking.query.get_or_404(booking_id)
        rating = Rating(
            booking_id=booking.id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(rating)
        
        # Update porter rating
        porter = Porter.query.get(booking.porter_id)
        porter.total_ratings += 1
        porter.rating = ((porter.rating * (porter.total_ratings - 1)) + form.rating.data) / porter.total_ratings
        
        db.session.commit()
        flash('Thank you for your rating')
    return redirect(url_for('index'))

@app.route('/booking/<int:booking_id>/verify-otp', methods=['POST'])
@login_required
def verify_booking_otp(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if booking belongs to current user
    if booking.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if OTP has expired
    if datetime.utcnow() > booking.otp_expiry:
        return jsonify({'error': 'OTP has expired'}), 400
    
    otp = request.json.get('otp')
    if not otp:
        return jsonify({'error': 'OTP is required'}), 400
    
    if verify_otp(booking, otp):
        booking.otp_verified = True
        booking.status = 'in_progress'
        db.session.commit()
        return jsonify({'message': 'OTP verified successfully'})
    else:
        return jsonify({'error': 'Invalid OTP'}), 400

@app.route('/booking/<int:booking_id>/resend-otp')
@login_required
def resend_booking_otp(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if booking belongs to current user
    if booking.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Generate new OTP
    otp = generate_otp()
    booking.otp = otp
    booking.otp_expiry = booking.meeting_time + timedelta(minutes=30)
    db.session.commit()
    
    # Send new OTP
    if send_otp_sms(current_user.phone, otp):
        return jsonify({'message': 'OTP sent successfully'})
    else:
        return jsonify({'error': 'Failed to send OTP'}), 500

@app.route('/porter/verify-otp', methods=['POST'])
@login_required
@porter_required
def porter_verify_otp():
    otp = request.json.get('otp')
    if not otp:
        return jsonify({'error': 'OTP is required'}), 400
    
    # Find the booking with this OTP
    booking = Booking.query.filter_by(
        otp=otp,
        status='pending',
        otp_verified=False
    ).first()
    
    if not booking:
        return jsonify({'error': 'Invalid or expired OTP'}), 400
    
    # Check if OTP has expired
    if datetime.utcnow() > booking.otp_expiry:
        return jsonify({'error': 'OTP has expired'}), 400
    
    # Verify the OTP
    booking.otp_verified = True
    booking.status = 'in_progress'
    booking.porter.available = False
    db.session.commit()
    
    return jsonify({
        'message': 'OTP verified successfully',
        'booking_id': booking.id,
        'customer_name': booking.user.username,
        'meeting_point': booking.meeting_point,
        'weight': booking.weight,
        'trolley_required': booking.trolley_required,
        'number_of_bags': booking.number_of_bags
    })

@app.route('/porter/complete-booking/<int:booking_id>', methods=['POST'])
@login_required
@porter_required
def porter_complete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the porter owns this booking
    if booking.porter_id != current_user.porter.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if the booking is in progress
    if booking.status != 'in_progress':
        return jsonify({'error': 'Invalid booking status'}), 400
    
    # Complete the booking
    booking.status = 'completed'
    booking.porter.available = True
    db.session.commit()
    
    return jsonify({'message': 'Booking completed successfully'})
