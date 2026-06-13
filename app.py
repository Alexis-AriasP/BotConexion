import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    
    user_message = req.get('queryResult', {}).get('queryText', '')
    
    if not DEEPSEEK_API_KEY:
        return jsonify({"fulfillmentText": "El servicio no está configurado correctamente."})

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Eres un asistente académico útil y conciso."},
            {"role": "user", "content": user_message}
        ]
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        ai_response = response.json()['choices'][0]['message']['content']
        
        return jsonify({"fulfillmentText": ai_response})
        
    except Exception as e:
        print(f"Error al llamar a DeepSeek: {e}")
        return jsonify({"fulfillmentText": "Lo siento, hubo un error procesando tu solicitud."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))