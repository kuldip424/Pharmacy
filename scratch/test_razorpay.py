import razorpay
import os
from dotenv import load_dotenv

load_dotenv()

key_id = os.getenv('RAZORPAY_KEY_ID')
key_secret = os.getenv('RAZORPAY_KEY_SECRET')

print(f"Testing with Key ID: {key_id}")

client = razorpay.Client(auth=(key_id, key_secret))

try:
    order = client.order.create({
        'amount': 100, # 1 INR
        'currency': 'INR',
        'payment_capture': 1
    })
    print("Order created successfully:", order['id'])
except Exception as e:
    print("Error creating order:", e)
