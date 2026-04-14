from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    # 1. ניסיון שליפת כתובת יעד בסיסית
    target_url = request.args.get('URL_GESHER')
    
    # 2. בדיקה האם מדובר במצב "plus" עם PressKey
    plus_mode = request.args.get('plus') == 'yes'
    press_key_value = request.args.get('PressKey')

    if plus_mode and press_key_value:
        # בניית שם הפרמטר הדינמי (למשל PressKey_9)
        lookup_param = f"PressKey_{press_key_value}"
        new_target = request.args.get(lookup_param)
        
        # אם נמצאה כתובת בפרמטר הדינמי, היא מקבלת עדיפות
        if new_target:
            target_url = new_target

    # 3. בדיקת תקינות - רק עכשיו בודקים אם יש לנו כתובת יעד כלשהי
    if not target_url:
        return "Error: Missing target URL parameter", 400

    # הכנת הנתונים למשלוח
    method = request.method
    data = request.get_data()
    headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}
    
    # סינון פרמטרים פנימיים כדי שלא יעברו לשרת היעד
    exclude_params = {'URL_GESHER', 'plus', 'PressKey'}
    params = {key: value for key, value in request.args.items() 
              if key not in exclude_params and not key.startswith('PressKey_')}

    try:
        # ביצוע הבקשה
        response = requests.request(
            method=method,
            url=target_url,
            headers=headers,
            data=data,
            params=params,
            cookies=request.cookies,
            allow_redirects=False,
            timeout=10
        )

        # הגבלת אורך התשובה והגדרת סוג תוכן כטקסט פשוט
        content_text = response.text[:1000]
        resp_headers = {
            'Content-Type': 'text/plain; charset=utf-8'
        }

        return Response(content_text, response.status_code, resp_headers)

    except Exception as e:
        return f"Error connecting to bridge: {str(e)}"[:1000], 500

if __name__ == '__main__':
    app.run(port=5000)
