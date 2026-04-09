from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    # שליפת כתובת היעד מהפרמטרים
    target_url = request.args.get('URL_GESHER')
    
    if not target_url:
        return "Error: Missing URL_GESHER parameter", 400

    # הכנת הנתונים למשלוח (הסרת Host כדי למנוע שגיאות ניתוב)
    method = request.method
    data = request.get_data()
    headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}
    params = {key: value for key, value in request.args.items() if key != 'URL_GESHER'}

    try:
        # ביצוע הבקשה לכתובת היעד
        response = requests.request(
            method=method,
            url=target_url,
            headers=headers,
            data=data,
            params=params,
            cookies=request.cookies,
            allow_redirects=False,
            timeout=10 # מומלץ להוסיף timeout
        )

        # --- התיקונים לבקשתך ---
        
        # 1. הגבלת אורך התשובה ל-1000 תווים
        # אנחנו משתמשים ב-response.text כדי לעבוד עם מחרוזת
        content_text = response.text[:1000]

        # 2. כפיית סוג תוכן טקסט פשוט (Plain Text) למניעת הרצת HTML
        resp_headers = {
            'Content-Type': 'text/plain; charset=utf-8'
        }

        # החזרת התשובה המוגבלת
        return Response(content_text, response.status_code, resp_headers)

    except Exception as e:
        # גם הודעת השגיאה מוגבלת באורך
        return f"Error connecting to bridge: {str(e)}"[:1000], 500

if __name__ == '__main__':
    app.run(port=5000)
