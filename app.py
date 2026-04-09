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

    # הכנת הנתונים למשלוח
    method = request.method
    data = request.get_data()
    headers = {key: value for key, value in request.headers if key.lower() != 'host'}
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
            allow_redirects=False
        )

        # החזרת התשובה המדויקת מהיעד למשתמש
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        resp_headers = [
            (name, value) for name, value in response.raw.headers.items()
            if name.lower() not in excluded_headers
        ]

        return Response(response.content, response.status_code, resp_headers)

    except Exception as e:
        return f"Error connecting to bridge: {str(e)}", 500

if __name__ == '__main__':
    # הרצה מקומית (לצורך בדיקה)
    app.run(port=5000)
