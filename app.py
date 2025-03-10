from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
import openai
import os
import pdfkit
from io import BytesIO

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

def generar_cuento(nombre, animal, tema, edad, longitud, moraleja=None):
    # Ajustar la longitud del cuento según la selección
    longitudes = {
        'corto': 500,
        'medio': 1000,
        'largo': 1500
    }
    palabras = longitudes.get(longitud, 1000)
    
    # Ajustar el lenguaje según la edad
    if edad == '3-5':
        nivel = "muy simple y cortas, apropiadas para niños de 3 a 5 años"
    elif edad == '6-8':
        nivel = "sencillas pero más elaboradas, para niños de 6 a 8 años"
    else:
        nivel = "más complejas y descriptivas, para niños de 9 a 12 años"

    prompt = f"""Genera un cuento infantil en español de aproximadamente {palabras} palabras con las siguientes características:
    - El protagonista se llama {nombre}
    - Debe incluir un {animal} como personaje principal
    - El tema o mensaje principal es: {tema}
    - Usa oraciones {nivel}
    - El tono debe ser dulce y amigable
    - Debe tener un inicio, desarrollo y final claro
    - Debe incluir diálogos entre los personajes
    - Debe tener descripciones vívidas y coloridas
    """

    if moraleja:
        prompt += f"- La moraleja debe ser específicamente: {moraleja}"
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un experto escritor de cuentos infantiles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2500
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
    edad = data.get('edad', '6-8')
    longitud = data.get('longitud', 'medio')
    moraleja = data.get('moraleja', '')
    
    cuento = generar_cuento(nombre, animal, tema, edad, longitud, moraleja)
    return jsonify({'cuento': cuento})

@app.route('/descargar-pdf', methods=['POST'])
def descargar_pdf():
    data = request.json
    contenido = data.get('contenido', '')
    titulo = data.get('titulo', 'Mi Cuento')
    
    # Crear HTML con estilos
    html = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 40px;
                    color: #333;
                }}
                h1 {{
                    color: #4a4a4a;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .contenido {{
                    text-align: justify;
                    white-space: pre-wrap;
                }}
                .pie {{
                    margin-top: 30px;
                    text-align: center;
                    font-style: italic;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <h1>{titulo}</h1>
            <div class="contenido">{contenido}</div>
            <div class="pie">Generado con ❤️ por Cuentos Mágicos</div>
        </body>
    </html>
    """
    
    try:
        # Configurar opciones de PDF
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': 'UTF-8'
        }
        
        # Generar PDF
        pdf = pdfkit.from_string(html, False, options=options)
        
        # Crear BytesIO object
        pdf_buffer = BytesIO(pdf)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{titulo.lower().replace(' ', '_')}.pdf"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
