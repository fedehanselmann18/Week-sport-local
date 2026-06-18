async function fetchUsers() {
    const response = await fetch('http://localhost:8000/user/');
    const data = await response.json();
    return data
}


async function displayAllUsers(){
    const usersGrid = document.querySelector('#users-grid');
    const allData = await fetchUsers()
    allData.forEach(user => {
        const userDiv = document.createElement('div')
        userDiv.className = 'user-card';
        userDiv.innerHTML += '<h2 class="card-title">' + user.username + '</h2><p><strong>Email:</strong> ' + user.email + '</p><p><strong>ID:</strong> ' + user.id + '</p><p><strong>Created:</strong> ' + user.created_at + '</p>';
        usersGrid.appendChild(userDiv)
    });
}

displayAllUsers()

function goToRegisterPage() {
    const button = document.querySelector('.go-to-register');
    button.addEventListener('click', () => {
        window.location.href = './register.html';
    });
}
goToRegisterPage();

// Delete user

async function deleteUser(userId) {
    try {
        const response = await fetch(`http://localhost:8000/user/${userId}`, {
            method: 'DELETE'
        });
        if (response.ok) {
            alert('User deleted successfully');
            location.reload();
        } else {
            alert('Failed to delete user');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}