function saveAuthToken(authData) {
    localStorage.setItem('access_token', authData.access_token);
    localStorage.setItem('token_type', authData.token_type || 'bearer');
}

async function loginUser(formData) {
    const identifier = formData.get('identifier') || formData.get('email') || '';
    const password = formData.get('password') || '';

    const body = new URLSearchParams({
        username: identifier,
        password,
        grant_type: 'password',
    });

    try {
        const response = await fetch('http://127.0.0.1:8000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body,
        });

        const result = await response.json();

        if (!response.ok) {
            alert(result.detail || 'Invalid credentials');
            return;
        }

        saveAuthToken(result);
        window.location.href = './myuser.html';
    } catch (error) {
        console.error('Error:', error);
    }
}

function setupLoginForm() {
    const form = document.querySelector('#login-form');
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        const formData = new FormData(form);
        loginUser(formData);
    });
}

function goToRegisterPage() {
    const button = document.querySelector('#go-to-register');
    button.addEventListener('click', () => {
        window.location.href = './register.html';
    });
}

function goToMyUserPage() {
    const button = document.querySelector('#go-to-my-user');
    button.addEventListener('click', () => {
        window.location.href = './myuser.html';
    });
}

goToMyUserPage();
goToRegisterPage();
setupLoginForm();