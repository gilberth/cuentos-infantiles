document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('storyForm');
    const storyContainer = document.querySelector('.story-container');
    const storyContent = document.getElementById('story-content');
    const loading = document.querySelector('.loading');
    const newStoryBtn = document.querySelector('.new-story-btn');
    const pdfBtn = document.querySelector('.pdf-btn');
    const shareButtons = document.querySelectorAll('.share-btn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            nombre: document.getElementById('nombre').value,
            animal: document.getElementById('animal').value,
            tema: document.getElementById('tema').value,
            edad: document.getElementById('edad').value,
            longitud: document.getElementById('longitud').value,
            moraleja: document.getElementById('moraleja').value
        };

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
            
            // Ocultar loading y mostrar historia
            loading.style.display = 'none';
            storyContent.style.display = 'block';
            storyContent.textContent = data.cuento;
            
        } catch (error) {
            console.error('Error:', error);
            storyContent.textContent = 'Lo siento, hubo un error generando tu historia. Por favor intenta de nuevo.';
        }
    });

    newStoryBtn.addEventListener('click', () => {
        storyContainer.style.display = 'none';
        form.style.display = 'block';
        form.reset();
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
                    contenido: storyContent.textContent,
                    titulo: `Cuento de ${document.getElementById('nombre').value}`
                })
            });
            
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
