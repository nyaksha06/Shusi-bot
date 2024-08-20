document.addEventListener('DOMContentLoaded', function () {
    const inputElement = document.getElementById('input');
    const sendButton = document.getElementById('send');
    const outputElement = document.getElementById('output');

    function sendMessage() {
        const message = inputElement.value.trim();
        if (message === '') return;

        outputElement.innerHTML += `<div class="message user-message">${message}</div>`;

        fetch('/send_message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: new URLSearchParams({
                'message': message
            })
        })
            .then(response => response.json())
            .then(data => {
                outputElement.innerHTML += `<div class="message bot-message">${data.response}</div>`;
                inputElement.value = '';
                outputElement.scrollTop = outputElement.scrollHeight;
            })
            .catch(error => console.error('Error:', error));
    }

    sendButton.addEventListener('click', sendMessage);

    inputElement.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });

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
