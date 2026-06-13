import os
import requests
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        req = request.get_json()
        user_message = req.get('queryResult', {}).get('queryText', '')
        
        if not DEEPSEEK_API_KEY:
            return jsonify({"fulfillmentText": "Error: API Key no configurada"})
        
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",  # Este es el más rápido
            "messages": [
                {"role": "system", "content": "Responde en español de forma EXTREMADAMENTE CONCISA. Máximo 20 palabras o 2 líneas."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.3,
            "max_tokens": 100, 
            "top_p": 0.9
        }
        

        response = requests.post(
            DEEPSEEK_API_URL, 
            headers=headers, 
            json=payload,
            timeout=4.5
        )
        
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
            return jsonify({"fulfillmentText": ai_response})
        else:
            return jsonify({"fulfillmentText": "Error temporal. Por favor, repite la pregunta."})
            
    except requests.exceptions.Timeout:

        return jsonify({
            "fulfillmentText": "Estoy pensando... ¿Puedes reformular tu pregunta sobre matrices?"
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"fulfillmentText": "Hubo un problema técnico. Intenta de nuevo."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
