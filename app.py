from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime
from flask_mail import Mail, Message
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable Flask debugging
app.debug = True

# Email Configuration
try:
    app.config.update(
        MAIL_SERVER='server62.hostingraja.org',
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        MAIL_USE_TLS=False,
        MAIL_USERNAME='sales@astroimpulse.in',
        MAIL_PASSWORD='Astroimpulse@123',
        MAIL_DEFAULT_SENDER=('AstroImpulse', 'sales@astroimpulse.in')
    )
    
    # Initialize mail after configuration
    mail = Mail(app)
    logger.info("Mail configuration successful")
except Exception as e:
    logger.error(f"Error in mail configuration: {str(e)}")

def calculate_bhagyank(dob):
    """Calculate Bhagyank from full date (DD-MM-YYYY)"""
    try:
        # Convert full date to numbers and sum them
        total = sum(int(digit) for digit in dob.replace('-', '') if digit.isdigit())
        # Keep reducing until single digit
        while total > 9:
            total = sum(int(digit) for digit in str(total))
        return total
    except Exception as e:
        logger.error(f"Error in calculate_bhagyank: {str(e)}")
        return None

def calculate_mulank(dob):
    """Calculate Mulank from birth date (DD) only"""
    try:
        date_obj = datetime.strptime(dob, '%Y-%m-%d')
        date_num = date_obj.day  # Get only the day part
        # Keep reducing until single digit
        while date_num > 9:
            date_num = sum(int(digit) for digit in str(date_num))
        return date_num
    except Exception as e:
        logger.error(f"Error in calculate_mulank: {str(e)}")
        return None

def is_lucky_number(number, bhagyank, mulank):
    """Check if number is compatible with Bhagyank or Mulank"""
    try:
        # Sum all digits in the number
        num_sum = sum(int(digit) for digit in str(number))
        while num_sum > 9:
            num_sum = sum(int(digit) for digit in str(num_sum))
        
        # Numerology compatibility combinations
        lucky_combinations = {
            1: [1, 3, 5, 6],
            2: [2, 3, 6, 9],
            3: [1, 2, 3, 9],
            4: [1, 4, 5, 7],
            5: [1, 4, 5, 8],
            6: [1, 2, 6, 9],
            7: [2, 4, 7, 8],
            8: [3, 5, 6, 8],
            9: [2, 3, 6, 9]
        }
        
        # Check compatibility with both numbers
        compatible_with_bhagyank = num_sum in lucky_combinations.get(bhagyank, [])
        compatible_with_mulank = num_sum in lucky_combinations.get(mulank, [])
        
        return {
            'is_lucky': compatible_with_bhagyank or compatible_with_mulank,
            'bhagyank_compatible': compatible_with_bhagyank,
            'mulank_compatible': compatible_with_mulank
        }
    except Exception as e:
        logger.error(f"Error in is_lucky_number: {str(e)}")
        return None

@app.route('/')
def home():
    try:
        return render_template('home.html', active_page='home')
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return "Error loading home page", 500

@app.route('/services')
def services():
    try:
        return render_template('services.html', active_page='services')
    except Exception as e:
        logger.error(f"Error in services route: {str(e)}")
        return "Error loading services page", 500

@app.route('/contact')
def contact():
    try:
        return render_template('contact.html', active_page='contact')
    except Exception as e:
        logger.error(f"Error in contact route: {str(e)}")
        return "Error loading contact page", 500

@app.route('/calculate_number', methods=['POST'])
def calculate_number():
    try:
        dob = request.form.get('dob', '')
        phone = request.form.get('phone', '')
        
        if not dob or not phone:
            return jsonify({'error': 'Please provide both DOB and phone number'})
        
        if not phone.isdigit() or len(phone) != 10:
            return jsonify({'error': 'Please enter a valid 10-digit mobile number'})
        
        bhagyank = calculate_bhagyank(dob)
        mulank = calculate_mulank(dob)
        if mulank is None:
            return jsonify({'error': 'Invalid date format'})
            
        lucky_status = is_lucky_number(phone, bhagyank, mulank)
        
        return jsonify({
            'result': {
                'is_lucky': lucky_status['is_lucky'],
                'bhagyank_compatible': lucky_status['bhagyank_compatible'],
                'mulank_compatible': lucky_status['mulank_compatible']
            }
        })
    except Exception as e:
        logger.error(f"Error in calculate_number: {str(e)}")
        return jsonify({'error': 'An error occurred while calculating. Please try again.'})

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    try:
        name = request.form.get('name')
        dob = request.form.get('dob')
        phone = request.form.get('phone')
        email = request.form.get('email')
        
        if not all([name, dob, phone, email]):
            return jsonify({'error': 'Please fill out all fields'})
        
        # Generate invoice number
        invoice_number = datetime.now().strftime('%Y%m%d%H%M%S')
        
        try:
            # Create email message with proper formatting
            msg = Message(
                subject=f'Invoice for Mobile Numerology Report - {name}',
                sender=('AstroImpulse', 'sales@astroimpulse.in'),
                recipients=[email]  # Send to customer
            )
            msg.body = f'''
            Dear {name},

            Thank you for choosing AstroImpulse Mobile Numerology Services.
            
            Invoice Details:
            ----------------
            Invoice Number: {invoice_number}
            Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Amount: ₹499.00
            
            Client Details:
            --------------
            Name: {name}
            Date of Birth: {dob}
            Phone: {phone}
            Email: {email}
            
            Payment Instructions:
            -------------------
            Please scan the QR code in the invoice to make the payment using any UPI app.
            Your report will be sent to your email address within 24hrs after the payment confirmation.
            
            Best regards,
            AstroImpulse Team
            '''
            
            # Send to customer
            mail.send(msg)
            logger.info(f"Invoice email sent to customer: {email}")
            
            # Create copy for admin
            admin_msg = Message(
                subject=f'New Order: Mobile Numerology Report - {name}',
                sender=('AstroImpulse', 'sales@astroimpulse.in'),
                recipients=['sales@astroimpulse.in']  # Send to admin
            )
            admin_msg.body = f'''
            New order received:
            
            Client Details:
            --------------
            Name: {name}
            Date of Birth: {dob}
            Phone: {phone}
            Email: {email}
            
            Invoice Number: {invoice_number}
            Amount: ₹499.00
            '''
            
            # Send to admin
            mail.send(admin_msg)
            logger.info("Admin notification email sent")
            
            return jsonify({
                'success': True,
                'message': 'Invoice generated successfully!',
                'invoice_number': invoice_number,
                'date': datetime.now().strftime('%Y-%m-%d')
            })
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return jsonify({'error': 'Failed to send email. Please try again.'})
            
    except Exception as e:
        logger.error(f"Error in submit_contact: {str(e)}")
        return jsonify({'error': 'An error occurred. Please try again later.'})

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application...")
        app.run(debug=True, port=8000)
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")