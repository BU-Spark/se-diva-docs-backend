from flask import Flask, request, jsonify
import stripe

# Set your Stripe API key and webhook signing secret
stripe.api_key = "sk_test_51MbreiIOQGSqv0xRllrwIKir09GURs4U3QYiLXSyKTiWqBBAoyx21Jum6e20GJpVgTg2B8f8zPz0w2D4ewIdUAWf00EUNTiFyg"
webhook_secret = "whsec_34d1b16bc211ba244123bf9fccebf7e286632563298ca36bc186df76d5bf09b6"

app = Flask(__name__)

# Define a route for the webhook endpoint
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': str(e)}), 401

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        return jsonify({'received': True})
        # Do something with the payment_intent object, e.g. mark the order as paid

    # Return a 200 response to acknowledge receipt of the event
    return jsonify({'test': True})

if __name__ == '__main__':
    app.run()