// Register logic POST /user
async function registerUser(formData) {
    const data = Object.fromEntries(formData.entries());
    const dataJson = JSON.stringify(data);
    try {
        const send = await fetch('http://127.0.0.1:8000/user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body : dataJson
        })
        const response = await send.json();
        console.log(response)
    }
    catch(error){
        console.log(error)
    }
}


async function getFormData() {
    const form = document.querySelector('.register-form')
    form.addEventListener('submit' , (event) => {
        event.preventDefault();
        const formData = new FormData(form);
        registerUser(formData);
    });
}

function goToUsersPage() {
    const button = document.querySelector('.go-to-users');
    button.addEventListener('click', () => {
        window.location.href = './users.html';
    });
}

goToUsersPage();
getFormData();