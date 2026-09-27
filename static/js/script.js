const btn = document.getElementById('send_message');

    function esc(s) {
        const div = document.createElement('div');
        div.textContent = String(s ?? '');
        return div.innerHTML;
    }

    document.getElementById('send_message').addEventListener('click', async function () {
        btn.disabled = true;
        btn.textContent = 'загрузка';

        try {
            let prompt = document.getElementById('prompt').value;

            const response = await fetch('/products/ai/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.detail || `HTTP ${response.status}`);
            }

            const data = await response.json();

            let ingredients = data.ingredients;
            let html = '';
            for (let i = 0; i < ingredients.length; i++) {
                html += `<li>${esc(ingredients[i].name)} — ${esc(ingredients[i].quantity)}</li>`;
            }

            document.getElementById('recipe-ingredients').innerHTML = html;

            const el = {
                title: document.getElementById('recipe-title'),
                description: document.getElementById('recipe-description'),
                time: document.getElementById('recipe-time'),
                servings: document.getElementById('recipe-servings'),
                difficulty: document.getElementById('recipe-difficulty'),
                tips: document.getElementById('recipe-tips'),
                ingredients: document.getElementById('recipe-ingredients'),
                steps: document.getElementById('recipe-steps'),
            };

            el.title.textContent = data.title;
            el.description.textContent = data.description;
            el.time.textContent = data.time_minutes + ' мин';
            el.servings.textContent = data.servings;
            el.difficulty.textContent = data.difficulty;
            el.tips.textContent = data.tips;
            el.ingredients.innerHTML = html;

            const steps = data.steps;
            const ol = document.getElementById('recipe-steps');

            let html_steps = '';
            for (let i = 0; i < steps.length; i++) {
                html_steps += `<li>${esc(steps[i])}</li>`;
            }
            ol.innerHTML = html_steps;

        } catch (e) {
            alert('Ошибка: ' + e.message);
        } finally {
            btn.disabled = false;
            btn.textContent = 'send';
        }
    });