document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('storyForm');
    const storyContainer = document.querySelector('.story-container');
    const storyContent = document.getElementById('story-content');
    const loading = document.querySelector('.loading');
    const newStoryBtn = document.querySelector('.new-story-btn');
    const pdfBtn = document.querySelector('.pdf-btn');
    const shareButtons = document.querySelectorAll('.share-btn');
    const temaSelect = document.getElementById('tema');

    // Lista de temas disponibles
    const temas = [
        { valor: "amistad", emoji: "🤝", nombre: "Amistad" },
        { valor: "valentia", emoji: "🦁", nombre: "Valentía" },
        { valor: "honestidad", emoji: "✨", nombre: "Honestidad" },
        { valor: "perseverancia", emoji: "💪", nombre: "Perseverancia" },
        { valor: "respeto", emoji: "🌟", nombre: "Respeto" },
        { valor: "compartir", emoji: "🎁", nombre: "Compartir" },
        { valor: "medioambiente", emoji: "🌱", nombre: "Cuidado del Medio Ambiente" },
        { valor: "creatividad", emoji: "🎨", nombre: "Creatividad e Imaginación" },
        { valor: "familia", emoji: "❤️", nombre: "Amor Familiar" },
        { valor: "diversidad", emoji: "🌈", nombre: "Celebrando las Diferencias" },
        { valor: "responsabilidad", emoji: "📚", nombre: "Responsabilidad" },
        { valor: "curiosidad", emoji: "🔍", nombre: "Curiosidad y Aprendizaje" },
        { valor: "empatia", emoji: "🤗", nombre: "Empatía" },
        { valor: "autoestima", emoji: "⭐", nombre: "Confianza en Uno Mismo" },
        { valor: "trabajo_equipo", emoji: "🤝", nombre: "Trabajo en Equipo" }
    ];

    function getTemaAleatorio() {
        const temaRandom = temas[Math.floor(Math.random() * temas.length)];
        return `${temaRandom.emoji} ${temaRandom.nombre}`;
    }

    function mostrarCuento(cuento, esError = false) {
        storyContent.innerHTML = cuento;
        storyContent.style.display = 'block';
        loading.style.display = 'none';
        
        // Solo mostrar los botones de acción si no hay error
        document.getElementById('story-actions').style.display = esError ? 'none' : 'flex';
        
        if (esError) {
            storyContent.classList.add('error');
        } else {
            storyContent.classList.remove('error');
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            nombre: document.getElementById('nombre').value.trim(),
            animal: document.getElementById('animal').value.trim(),
            tema: temaSelect.value || getTemaAleatorio(),
            edad: document.getElementById('edad').value,
            longitud: document.getElementById('longitud').value,
            moraleja: document.getElementById('moraleja').value.trim()
        };

        // Validar datos requeridos
        if (!formData.nombre || !formData.animal) {
            mostrarCuento('Por favor completa todos los campos requeridos.', true);
            return;
        }

        // Mostrar contenedor de historia y loading
        storyContainer.style.display = 'block';
        loading.style.display = 'block';
        storyContent.style.display = 'none';
        form.style.display = 'none';

        try {
            const response = await fetch('/generar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Error al generar el cuento');
            }
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Mostrar el cuento
            mostrarCuento(data.cuento);
            
        } catch (error) {
            console.error('Error:', error);
            mostrarCuento(`<p>😔 ${error.message || 'Lo siento, hubo un error generando tu historia. Por favor intenta de nuevo.'}</p>`, true);
        }
    });

    newStoryBtn.addEventListener('click', () => {
        storyContainer.style.display = 'none';
        form.style.display = 'block';
        form.reset();
        storyContent.classList.remove('error');
    });

    // Manejar la descarga de PDF
    pdfBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/descargar-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    contenido: storyContent.innerHTML,
                    titulo: `Cuento de ${document.getElementById('nombre').value}`
                })
            });
            
            if (!response.ok) {
                throw new Error('Error al generar el PDF');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `cuento_${document.getElementById('nombre').value.toLowerCase()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Error al descargar PDF:', error);
            alert('Hubo un error al generar el PDF. Por favor intenta de nuevo.');
        }
    });

    // Manejar compartir en redes sociales
    shareButtons.forEach(button => {
        button.addEventListener('click', () => {
            const platform = button.dataset.platform;
            const text = encodeURIComponent(`¡Mira el cuento que generé para ${document.getElementById('nombre').value}!`);
            const url = encodeURIComponent(window.location.href);
            
            let shareUrl;
            switch(platform) {
                case 'whatsapp':
                    shareUrl = `https://wa.me/?text=${text} ${url}`;
                    break;
                case 'facebook':
                    shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}&quote=${text}`;
                    break;
                case 'twitter':
                    shareUrl = `https://twitter.com/intent/tweet?text=${text}&url=${url}`;
                    break;
            }
            
            window.open(shareUrl, '_blank', 'width=600,height=400');
        });
    });
});
