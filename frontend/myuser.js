function getAccessToken() {
	return localStorage.getItem('access_token');
}

function logout() {
	localStorage.removeItem('access_token');
	localStorage.removeItem('token_type');
	window.location.href = './login.html';
}

function renderProfile(user) {
	const profileCard = document.querySelector('#profile-card');
	profileCard.innerHTML = `
		<h2 class="card-title">${user.username}</h2>
		<p><strong>Email:</strong> ${user.email}</p>
		<p><strong>ID:</strong> ${user.id}</p>
		<p><strong>Created:</strong> ${user.created_at}</p>
	`;
}

async function fetchMyUser() {
	const token = getAccessToken();
	if (!token) {
		alert('Please login first');
		window.location.href = './login.html';
		return;
	}

	try {
		const response = await fetch('http://127.0.0.1:8000/user/me', {
			method: 'GET',
			headers: {
				'Authorization': `Bearer ${token}`,
			},
		});

		if (!response.ok) {
			alert('Session expired, please login again');
			logout();
			return;
		}

		const user = await response.json();
		renderProfile(user);
	} catch (error) {
		console.error('Error:', error);
	}
}

function setupMyUserPage() {
	const logoutButton = document.querySelector('#logout');
	const refreshButton = document.querySelector('#refresh-profile');

	logoutButton.addEventListener('click', logout);
	refreshButton.addEventListener('click', fetchMyUser);

	fetchMyUser();
}

setupMyUserPage();
