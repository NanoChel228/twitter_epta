document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    searchInput.addEventListener('input', function () {
        const query = searchInput.value;
        if (query.length > 2) {  // Поиск начинает работать после ввода 3 символов
            fetch(`/search/?q=${query}`)
                .then(response => response.json())
                .then(data => {
                    searchResults.innerHTML = '';
                    data.forEach(user => {
                        const resultItem = document.createElement('div');
                        resultItem.textContent = user.username;
                        resultItem.dataset.userId = user.id;
                        resultItem.addEventListener('click', function () {
                            createChat(user.id);
                        });
                        searchResults.appendChild(resultItem);
                    });
                })
                .catch(error => console.error('Error:', error));
        } else {
            searchResults.innerHTML = '';
        }
    });
    
    function createChat(userId) {
        fetch(`/chats/create/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Для обработки CSRF
            },
            body: JSON.stringify({ profiles: [userId] })
        })
        .then(response => response.json())
        .then(data => {
            if (data.chat_id) {
                window.location.href = `/chats/?chat_id=${data.chat_id}`;
            } else {
                console.error('Failed to create chat');
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});