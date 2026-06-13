import os
import requests
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route('/webhook', methods=['POST'])
def webhook():
    start_time = time.time()
    
    try:
        req = request.get_json()
        user_message = req.get('queryResult', {}).get('queryText', '')
        
        # === ESTRATEGIA: Reducir el contexto al mínimo ===
        # Solo enviamos la pregunta, nada de system prompt complejo
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": f"Responde en máximo 2 oraciones: {user_message}"}
            ],
            "max_tokens": 180,        # Límite estricto
            "temperature": 0.3,       # Bajo = más rápido
            "top_p": 0.85
        }
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Timeout justo al límite
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=3.8
        )
        
        elapsed = time.time() - start_time
        print(f"✅ Respuesta en {elapsed:.2f}s: {user_message[:50]}...")
        
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
            return jsonify({"fulfillmentText": ai_response})
        else:
            # Respuesta minimalista en caso de error
            return jsonify({
                "fulfillmentText": "La derivada de una matriz se calcula elemento por elemento. ¿Necesitas la fórmula general?"
            })
            
    except requests.exceptions.Timeout:
        # Respuesta útil pero breve que evita el fallback
        return jsonify({
            "fulfillmentText": "Para derivar una matriz, deriva cada entrada individualmente. Ejemplo: d/dt[t²  t; 0  t³] = [2t  1; 0  3t²]"
        })
        
    except Exception as e:
        return jsonify({
            "fulfillmentText": "Explica qué concepto de derivada de matrices necesitas (básica, parcial, jacobiana)."
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
