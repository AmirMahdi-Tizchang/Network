document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#close-alert')?.addEventListener('click', closeAlert);
    document.querySelectorAll('button[name="edit"]').forEach(button => {
        button.addEventListener('click', editPost);
    });

    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', toggleLike);
    });
});

function closeAlert() {
    document.querySelector('#alert').style.display = 'none';
}

function editPost(event) {
    const id = event.target.dataset.id;
    const parent = document.querySelector(`#post-content-${id}`);
    const content = parent.querySelector('p');
    const original = content.textContent;

    const textarea = document.createElement('textarea');
    textarea.className = 'form-control';
    textarea.rows = 10;
    textarea.value = original;

    const save = document.createElement('button');
    save.textContent = 'Save';
    save.classList.add('btn', 'btn-outline-primary', 'btn-sm', 'mt-2');

    // Clear parent content and insert textarea + save
    parent.innerHTML = '';
    parent.appendChild(textarea);
    parent.appendChild(save);

    save.addEventListener('click', function() {
        fetch('/edit', {
                method: 'POST',
                body: JSON.stringify({
                    content: textarea.value,
                    id: id
                })
            })
            .then(response => {
                if (!response.ok) throw new Error('Failed to update!');
                return response.json();
            })
            .then(data => {
                const p = document.createElement('p');
                p.textContent = textarea.value;
                parent.innerHTML = '';
                parent.appendChild(p);
            })
            .catch(error => {
                console.error('Edit failed:', error);
                alert(error);
            });
    });
}

function toggleLike(event) {
    const button = event.currentTarget;
    const id = button.dataset.id;

    fetch('/like', {
            method: 'POST',
            body: JSON.stringify({
                id: id
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Connection got interrupted!');
            }

            return response.json()
        })
        .then(data => {
            if (data.success) {
                const count = button.querySelector('.like-count');
                count.textContent = data.likes;
            } else {
                alert(data.error || 'Could not update like.');
            }
        })
        .catch(error => {
            console.error('Like error:', error);
            alert('Something went wrong.');
        });
}
