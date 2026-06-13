import os
import requests
from flask import Flask, request, jsonify
import json
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
        
        if not DEEPSEEK_API_KEY:
            return jsonify({"fulfillmentText": "Error: API Key no configurada"})
        
   
        system_prompt = """Eres un profesor asistente de matemáticas a nivel universitario. 
        Explica conceptos sobre derivadas de matrices de manera clara, didáctica y completa.
        Incluye ejemplos concretos cuando sea apropiado.
        Usa notación matemática simple como dA/dt o ∂a_ij/∂x.
        Responde en español, con un tono académico pero accesible."""
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
   
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,       
            "max_tokens": 500,        
            "top_p": 0.95
        }
        

        response = requests.post(
            DEEPSEEK_API_URL, 
            headers=headers, 
            json=payload,
            timeout=4.5
        )
        
        elapsed = time.time() - start_time
        print(f"Tiempo de respuesta: {elapsed:.2f} segundos")
        
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
            

            if len(ai_response) > 1000:
                ai_response = ai_response[:1000] + "... [respuesta truncada por longitud]"
            
            return jsonify({"fulfillmentText": ai_response})
        else:
            return jsonify({"fulfillmentText": f"Error {response.status_code}: No se pudo generar respuesta."})
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"TIMEOUT después de {elapsed:.2f} segundos")
        

        respaldo = """La consulta requiere más tiempo de procesamiento para darte una respuesta académica completa. 

Por favor, prueba preguntar algo más específico sobre derivadas de matrices, como:
- "¿Cómo se deriva una matriz respecto a un escalar?"
- "¿Qué es la matriz jacobiana?"
- "¿Cuál es la regla del producto para derivar matrices?"

Te daré una respuesta detallada y sin apuros. 😊"""
        
        return jsonify({"fulfillmentText": respaldo})
        
    except Exception as e:
        print(f"Error general: {str(e)}")
        return jsonify({"fulfillmentText": "Error técnico. Por favor, intenta de nuevo."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
