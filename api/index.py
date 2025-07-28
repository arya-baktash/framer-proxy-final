# File: /api/index.py
from flask import Flask, jsonify
import myfxbook
import os

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    email = os.environ.get('MYFXBOOK_EMAIL')
    password = os.environ.get('MYFXBOOK_PASSWORD')

    if not email or not password:
        return jsonify({"error": "Email or password not configured in Vercel environment variables."}), 500
    
    try:
        client = myfxbook.Myfxbook(email, password)
        client.login()
        
        accounts = client.get_my_accounts()
        
        if not accounts:
            client.logout()
            return jsonify({"error": "No accounts found on this MyFXBook profile."}), 404

        # --- اصلاح کلیدی: انتخاب خودکار اولین حساب ---
        target_account = accounts[0]
        
        # داده‌های نمودار در این API موجود نیست
        response_data = {
            "gain": target_account.get('gain'),
            "profitability": target_account.get('profitability'),
            "drawdown": target_account.get('drawdown'),
            "chartData": [] 
        }
        
        client.logout()
        return jsonify(response_data)

    except Exception as e:
        # برگرداندن خطای دقیق برای دیباگ کردن
        return jsonify({"error": f"An exception occurred: {str(e)}"}), 500

# این تابع اصلی است که Vercel آن را اجرا می‌کند
def vercel_handler(request):
    return app(request.environ, request.start_response)
