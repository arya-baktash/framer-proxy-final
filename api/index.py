# File: /api/index.py
from flask import Flask, jsonify, request
import myfxbook
import os

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    email = os.environ.get('MYFXBOOK_EMAIL')
    password = os.environ.get('MYFXBOOK_PASSWORD')
    account_id = request.args.get('accountId')

    if not email or not password:
        return jsonify({"error": "Email or password not configured in Vercel environment variables."}), 500
    
    if not account_id:
        return jsonify({"error": "accountId is required as a query parameter."}), 400

    try:
        client = myfxbook.Myfxbook(email, password)
        client.login()
        
        accounts = client.get_my_accounts()
        target_account = next((acc for acc in accounts if str(acc.get('id')) == account_id), None)
        
        client.logout() # Logout after getting data

        if target_account:
            # داده‌های نمودار در این API موجود نیست، یک آرایه خالی برمی‌گردانیم
            response_data = {
                "gain": target_account.get('gain'),
                "profitability": target_account.get('profitability'),
                "drawdown": target_account.get('drawdown'),
                "chartData": [] 
            }
            return jsonify(response_data)
        else:
            return jsonify({"error": f"Account with ID {account_id} not found."}), 404

    except Exception as e:
        # برگرداندن خطای دقیق برای دیباگ کردن
        return jsonify({"error": f"An exception occurred: {str(e)}"}), 500

# این تابع اصلی است که Vercel آن را اجرا می‌کند
def vercel_handler(request):
    return app(request.environ, request.start_response)
