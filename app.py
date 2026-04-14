from flask import Flask, request, Response
import requests
import time

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    # --- 1. מנגנון אבטחת זמן (ApiTime) ---
    api_time_str = request.args.get('ApiTime')
    try:
        if not api_time_str:
            raise ValueError()
        
        api_time = float(api_time_str)
        current_time = time.time()
        
        # אם ההפרש גדול מ-20 שניות - שגיאה 909
        if abs(current_time - api_time) > 20:
            return "Error 909", 403
    except:
        return "Error 909", 403

    # --- 2. איתור כתובת היעד ---
    target_url = request.args.get('URL_GESHER')
    plus_mode = request.args.get('plus') == 'yes'
    press_key_value = request.args.get('PressKey')

    if plus_mode and press_key_value:
        lookup_param = f"PressKey_{press_key_value}"
        new_target = request.args.get(lookup_param)
        if new_target:
            target_url = new_target

    if not target_url:
        return "Error: Missing target URL", 400

    # --- 3. הכנת הבקשה ליעד ---
    method = request.method
    data = request.get_data()
    # העברת כותרות מהלקוח (למעט Host)
    headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}
    
    # סינון פרמטרים פנימיים (ApiTime נשלח ליעד כפי שביקשת)
    exclude_params = {'URL_GESHER', 'plus', 'PressKey'}
    params = {k: v for k, v in request.args.items() 
              if k not in exclude_params and not k.startswith('PressKey_')}

    try:
        # ביצוע הבקשה עם מעקב אחרי הפניות
        response = requests.request(
            method=method,
            url=target_url,
            headers=headers,
            data=data,
            params=params,
            cookies=request.cookies,
            allow_redirects=True, # גשר מלא עוקב אחרי הפניות
            timeout=15
        )

        # --- 4. החזרת תשובה מלאה (Transparent Proxy) ---
        # מוציאים את הכותרות החשובות משרת היעד (סוג תוכן וכו')
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        resp_headers = {k: v for k, v in response.headers.items() if k.lower() not in excluded_headers}

        return Response(response.content, response.status_code, resp_headers)

    except Exception as e:
        return f"Proxy Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(port=5000)
