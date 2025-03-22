# PorterPro

A web application for booking porter services at railway stations.

## Features

- User registration and authentication
- Porter service booking
- OTP verification for service confirmation
- Real-time booking tracking
- Rating system
- Admin dashboard

## Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your environment variables
5. Run the application:
   ```bash
   flask run
   ```

## Deployment to Render

1. Create a Render account at https://render.com
2. Create a new Web Service
3. Connect your GitHub repository
4. Configure the service:
   - Name: porterpro (or your preferred name)
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Plan: Free

5. Add the following environment variables in Render:
   ```
   FLASK_APP=app.py
   FLASK_ENV=production
   SECRET_KEY=<generate-a-secure-secret-key>
   DATABASE_URL=<your-postgresql-database-url>
   STRIPE_SECRET_KEY=<your-stripe-secret-key>
   STRIPE_PUBLISHABLE_KEY=<your-stripe-publishable-key>
   TWILIO_ACCOUNT_SID=<your-twilio-account-sid>
   TWILIO_AUTH_TOKEN=<your-twilio-auth-token>
   TWILIO_PHONE_NUMBER=<your-twilio-phone-number>
   ```

6. Create a PostgreSQL database in Render and use its connection string as your DATABASE_URL

## Environment Variables

- `FLASK_APP`: The Flask application entry point
- `FLASK_ENV`: The environment (development/production)
- `SECRET_KEY`: Flask secret key for session management
- `DATABASE_URL`: PostgreSQL database connection string
- `STRIPE_SECRET_KEY`: Stripe API secret key
- `STRIPE_PUBLISHABLE_KEY`: Stripe API publishable key
- `TWILIO_ACCOUNT_SID`: Twilio account SID
- `TWILIO_AUTH_TOKEN`: Twilio authentication token
- `TWILIO_PHONE_NUMBER`: Twilio phone number for SMS

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 