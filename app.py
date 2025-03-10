from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
import openai
import os
import pdfkit
from io import BytesIO
import random
import re

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

def format_story_with_emojis(story):
    # Emojis para diferentes elementos del cuento
    character_emojis = ["👦", "👧", "👨", "👩", "🧔", "👵", "👴", "🐱", "🐶", "🐰", "🦁", "🐯", "🐼"]
    place_emojis = ["🏠", "🌳", "🌲", "🏞️", "🌅", "🏰", "🌆", "🎪", "🎡", "🎢"]
    emotion_emojis = ["😊", "😃", "🥰", "😍", "🤗", "😮", "😢", "😌", "🥳", "😎"]
    action_emojis = ["🏃", "💫", "✨", "🌟", "💝", "🎈", "🎁", "🎨", "🎭", "🎪"]
    
    # Dividir el cuento en párrafos
    paragraphs = story.split('\n\n')
    formatted_paragraphs = []
    
    for i, paragraph in enumerate(paragraphs):
        # Agregar emoji al inicio de cada párrafo
        if i == 0:  # Primer párrafo
            emoji = random.choice(["📖", "🌟", "✨", "🎈"])
            paragraph = f"{emoji} {paragraph}"
        else:
            emoji = random.choice(character_emojis + place_emojis + emotion_emojis + action_emojis)
            paragraph = f"{emoji} {paragraph}"
        
        # Envolver el párrafo en una etiqueta p con clases específicas
        formatted_paragraphs.append(f"<p>{paragraph}</p>")
    
    # Unir los párrafos formateados
    formatted_story = "\n".join(formatted_paragraphs)
    
    # Resaltar palabras clave con clases CSS
    keywords = {
        'character': ['niño', 'niña', 'mamá', 'papá', 'abuelo', 'abuela', 'gato', 'perro', 'conejo'],
        'place': ['casa', 'jardín', 'bosque', 'parque', 'escuela', 'pueblo', 'ciudad', 'montaña', 'playa'],
        'emotion': ['feliz', 'triste', 'emocionado', 'asustado', 'sorprendido', 'alegre', 'contento'],
        'action': ['jugar', 'correr', 'saltar', 'bailar', 'cantar', 'reír', 'compartir', 'ayudar']
    }
    
    for category, words in keywords.items():
        for word in words:
            # Buscar la palabra y sus variaciones (mayúsculas/minúsculas)
            pattern = re.compile(f'\\b{word}\\w*\\b', re.IGNORECASE)
            formatted_story = pattern.sub(lambda m: f'<span class="{category}">{m.group()}</span>', formatted_story)
    
    return formatted_story

def generar_cuento(nombre, animal, tema, edad, longitud, moraleja=None):
    # Configurar el cliente de OpenAI con la API key
    client = openai.OpenAI(
        api_key=os.getenv('OPENAI_API_KEY')
    )

    # Ajustar la longitud del cuento según la selección
    longitudes = {
        "corto": 500,
        "medio": 1000,
        "largo": 1500
    }
    palabras = longitudes.get(longitud, 1000)
    
    # Construir el prompt para OpenAI
    prompt = f"""Escribe un cuento infantil en español con las siguientes características:
    - Protagonista: Un niño/a llamado {nombre}
    - Animal especial: Un {animal}
    - Tema principal: {tema}
    - Edad recomendada: {edad} años
    - Longitud aproximada: {palabras} palabras
    {'- Moraleja específica: ' + moraleja if moraleja else ''}
    
    El cuento debe ser muy infantil, divertido y educativo, con:
    - Descripciones coloridas y vívidas
    - Diálogos amigables y expresivos
    - Situaciones mágicas y sorprendentes
    - Momentos de emoción y alegría
    - Un final feliz y memorable
    
    Formato:
    - Divide el cuento en párrafos cortos
    - Usa un lenguaje simple y claro
    - Incluye elementos de sorpresa
    """
    
    try:
        # Generar el cuento con OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un experto escritor de cuentos infantiles en español."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Obtener el cuento generado
        cuento = response.choices[0].message.content.strip()
        
        # Formatear el cuento con emojis y HTML
        cuento_formateado = format_story_with_emojis(cuento)
        
        return cuento_formateado
        
    except Exception as e:
        print(f"Error al generar el cuento: {str(e)}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generar', methods=['POST'])
def generar():
    try:
        data = request.get_json()
        nombre = data.get('nombre', '')
        animal = data.get('animal', '')
        tema = data.get('tema', '')
        edad = data.get('edad', '')
        longitud = data.get('longitud', '')
        moraleja = data.get('moraleja', None)
        
        if not all([nombre, animal, tema, edad, longitud]):
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        
        cuento = generar_cuento(nombre, animal, tema, edad, longitud, moraleja)
        
        if not cuento:
            return jsonify({'error': 'Error al generar el cuento'}), 500
            
        # Marcar el contenido como HTML seguro
        from markupsafe import Markup
        cuento = Markup(cuento)
        
        return jsonify({'cuento': cuento})
    except Exception as e:
        print(f"Error en /generar: {str(e)}")
        return jsonify({'error': 'Error al generar el cuento'}), 500

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
