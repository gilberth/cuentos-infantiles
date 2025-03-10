from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import openai
import os

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

def generar_cuento(nombre, animal, tema):
    prompt = f"""Genera un cuento infantil en español de al menos 1000 palabras con las siguientes características:
    - El protagonista se llama {nombre}
    - Debe incluir un {animal} como personaje principal
    - El tema o mensaje principal es: {tema}
    - El tono debe ser dulce y amigable
    - Debe tener un inicio, desarrollo y final claro
    - Debe incluir diálogos entre los personajes
    - Debe tener descripciones vívidas y coloridas
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un experto escritor de cuentos infantiles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generar', methods=['POST'])
def generar():
    data = request.json
    nombre = data.get('nombre', '')
    animal = data.get('animal', '')
    tema = data.get('tema', '')
    
    cuento = generar_cuento(nombre, animal, tema)
    return jsonify({'cuento': cuento})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
