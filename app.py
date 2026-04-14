from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    # שליפת כתובת היעד המקורית מהפרמטרים
    target_url = request.args.get('URL_GESHER')
    
    # --- שדרוג הקוד לפי בקשתך ---
    # בדיקה האם מופיע פרמטר plus=yes והאם קיים פרמטר PressKey
    plus_mode = request.args.get('plus') == 'yes'
    press_key_value = request.args.get('PressKey')

    if plus_mode and press_key_value:
        # בניית שם הפרמטר ממנו יש לשלוף את הכתובת החדשה (לדוגמה: PressKey_*-0)
        lookup_param = f"PressKey_{press_key_value}"
        new_target = request.args.get(lookup_param)
        
        # אם נמצאה כתובת בפרמטר הדינמי, נעדכן את כתובת היעד
        if new_target:
            target_url = new_target
    # ---------------------------

    if not target_url:
        return "Error: Missing target URL parameter", 400

    # הכנת הנתונים למשלוח (הסרת Host כדי למנוע שגיאות ניתוב)
    method = request.method
    data = request.get_data()
    headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}
    
    # הסרת פרמטרי השליטה של ה-proxy כדי שלא יעברו לשרת היעד ב-Query String
    exclude_params = {'URL_GESHER', 'plus', 'PressKey'}
    # מסננים גם את כל הפרמטרים שמתחילים ב-PressKey_
    params = {key: value for key, value in request.args.items() 
              if key not in exclude_params and not key.startswith('PressKey_')}

    try:
        # ביצוע הבקשה לכתובת היעד (המקורית או הדינמית מהשדרוג)
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

        # הגבלת אורך התשובה ל-1000 תווים
        content_text = response.text[:1000]

        # כפיית סוג תוכן טקסט פשוט למניעת הרצת HTML
        resp_headers = {
            'Content-Type': 'text/plain; charset=utf-8'
        }

        return Response(content_text, response.status_code, resp_headers)

    except Exception as e:
        return f"Error connecting to bridge: {str(e)}"[:1000], 500

if __name__ == '__main__':
    app.run(port=5000)
