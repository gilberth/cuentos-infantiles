document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('storyForm');
    const storyContainer = document.querySelector('.story-container');
    const storyContent = document.getElementById('story-content');
    const loading = document.querySelector('.loading');
    const newStoryBtn = document.querySelector('.new-story-btn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            nombre: document.getElementById('nombre').value,
            animal: document.getElementById('animal').value,
            tema: document.getElementById('tema').value
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
});
