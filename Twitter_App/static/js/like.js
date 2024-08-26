document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.likes').forEach(function(likeDiv) {
        likeDiv.addEventListener('click', function() {
            const postSlug = this.dataset.postSlug;
            fetch(`/post/${postSlug}/like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ post_slug: postSlug })
            })
            .then(response => response.json())
            .then(data => {
                const likeIcon = document.getElementById(`like-icon-${postSlug}`);
                const likeCount = document.getElementById(`likes-count-${postSlug}`);
                if (data.liked) {
                    likeIcon.classList.add('liked');
                } else {
                    likeIcon.classList.remove('liked');
                }
                likeCount.textContent = data.likes_count;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
});