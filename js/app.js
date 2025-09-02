// DOM Elements
const userStatusElement = document.getElementById('user-status');
const loginSection = document.getElementById('login-section');
const registerSection = document.getElementById('register-section');
const dashboardSection = document.getElementById('dashboard-section');
const addPlayerSection = document.getElementById('add-player-section');
const contentArea = document.getElementById('content-area');

// Form Elements
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const addPlayerForm = document.getElementById('add-player-form');

// Navigation Elements
const showRegisterLink = document.getElementById('show-register');
const showLoginLink = document.getElementById('show-login');
const viewPlayersButton = document.getElementById('view-players');
const addPlayerButton = document.getElementById('add-player');
const viewStatisticsButton = document.getElementById('view-statistics');

// Firebase References
const auth = firebase.auth();
const db = firebase.firestore();

// Show/Hide Sections
function showSection(section) {
  // Hide all sections
  loginSection.classList.remove('active');
  registerSection.classList.remove('active');
  dashboardSection.classList.remove('active');
  addPlayerSection.classList.remove('active');
  
  // Show the requested section
  section.classList.add('active');
}

// Authentication State Observer
auth.onAuthStateChanged(user => {
  if (user) {
    // User is signed in
    userStatusElement.innerHTML = `
      <span>Welcome, ${user.email}</span>
      <button id="logout-button">Logout</button>
    `;
    document.getElementById('logout-button').addEventListener('click', () => {
      auth.signOut();
    });
    
    showSection(dashboardSection);
    loadPlayers();
  } else {
    // User is signed out
    userStatusElement.innerHTML = '';
    showSection(loginSection);
  }
});

// Navigation Event Listeners
showRegisterLink.addEventListener('click', (e) => {
  e.preventDefault();
  showSection(registerSection);
});

showLoginLink.addEventListener('click', (e) => {
  e.preventDefault();
  showSection(loginSection);
});

viewPlayersButton.addEventListener('click', () => {
  loadPlayers();
});

addPlayerButton.addEventListener('click', () => {
  showSection(addPlayerSection);
  setupAddPlayerForm();
});

viewStatisticsButton.addEventListener('click', () => {
  loadStatistics();
});

// Authentication Functions
loginForm.addEventListener('submit', (e) => {
  e.preventDefault();
  
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  
  auth.signInWithEmailAndPassword(email, password)
    .catch(error => {
      alert(`Login Error: ${error.message}`);
    });
});

registerForm.addEventListener('submit', (e) => {
  e.preventDefault();
  
  const email = document.getElementById('reg-email').value;
  const password = document.getElementById('reg-password').value;
  const confirmPassword = document.getElementById('reg-confirm-password').value;
  
  if (password !== confirmPassword) {
    alert("Passwords don't match!");
    return;
  }
  
  auth.createUserWithEmailAndPassword(email, password)
    .catch(error => {
      alert(`Registration Error: ${error.message}`);
    });
});

// Database Functions
function loadPlayers() {
  showSection(dashboardSection);
  contentArea.innerHTML = '<h3>Loading players...</h3>';
  
  db.collection('players').get()
    .then(snapshot => {
      if (snapshot.empty) {
        contentArea.innerHTML = '<h3>No players found</h3>';
        return;
      }
      
      let tableHTML = `
        <h3>All Players</h3>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Age Group</th>
              <th>Jersey #</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
      `;
      
      snapshot.forEach(doc => {
        const player = doc.data();
        tableHTML += `
          <tr>
            <td>${player.fullName}</td>
            <td>${player.playerType}</td>
            <td>${player.ageGroup}</td>
            <td>${player.jerseyNumber || ''}</td>
            <td>
              <button onclick="editPlayer('${doc.id}')">Edit</button>
              <button onclick="deletePlayer('${doc.id}')">Delete</button>
            </td>
          </tr>
        `;
      });
      
      tableHTML += `
          </tbody>
        </table>
      `;
      
      contentArea.innerHTML = tableHTML;
    })
    .catch(error => {
      contentArea.innerHTML = `<h3>Error loading players: ${error.message}</h3>`;
    });
}

function setupAddPlayerForm() {
  // First, get age groups from the database
  db.collection('ageGroups').get()
    .then(snapshot => {
      let ageGroupOptions = '';
      snapshot.forEach(doc => {
        const ageGroup = doc.data();
        ageGroupOptions += `<option value="${doc.id}">${ageGroup.name}</option>`;
      });
      
      addPlayerForm.innerHTML = `
        <div class="form-group">
          <label for="player-name">Full Name:</label>
          <input type="text" id="player-name" required>
        </div>
        <div class="form-group">
          <label for="player-type">Player Type:</label>
          <select id="player-type" required>
            <option value="FT">Full Time (FT)</option>
            <option value="SC">Scholarship (SC)</option>
            <option value="PT">Part Time (PT)</option>
            <option value="T">Trial (T)</option>
          </select>
        </div>
        <div class="form-group">
          <label for="age-group">Age Group:</label>
          <select id="age-group" required>
            ${ageGroupOptions}
          </select>
        </div>
        <div class="form-group">
          <label for="birth-day">Birth Day:</label>
          <input type="number" id="birth-day" min="1" max="31" required>
        </div>
        <div class="form-group">
          <label for="birth-month">Birth Month:</label>
          <input type="number" id="birth-month" min="1" max="12" required>
        </div>
        <div class="form-group">
          <label for="birth-year">Birth Year:</label>
          <input type="number" id="birth-year" min="2000" max="2020" required>
        </div>
        <div class="form-group">
          <label for="jersey-number">Jersey Number:</label>
          <input type="text" id="jersey-number">
        </div>
        <button type="submit">Add Player</button>
      `;
      
      // Add event listener to the form
      addPlayerForm.addEventListener('submit', submitNewPlayer);
    })
    .catch(error => {
      addPlayerForm.innerHTML = `<p>Error loading form: ${error.message}</p>`;
    });
}

function submitNewPlayer(e) {
  e.preventDefault();
  
  const playerData = {
    fullName: document.getElementById('player-name').value,
    playerType: document.getElementById('player-type').value,
    ageGroupId: document.getElementById('age-group').value,
    birthDay: parseInt(document.getElementById('birth-day').value),
    birthMonth: parseInt(document.getElementById('birth-month').value),
    birthYear: parseInt(document.getElementById('birth-year').value),
    jerseyNumber: document.getElementById('jersey-number').value,
    veoMember: false,
    photos: false,
    idpMeetingSep: false,
    idpMeetingApr: false,
    chat: false,
    files: false,
    createdAt: firebase.firestore.FieldValue.serverTimestamp(),
    updatedAt: firebase.firestore.FieldValue.serverTimestamp()
  };
  
  db.collection('players').add(playerData)
    .then(() => {
      alert('Player added successfully!');
      addPlayerForm.reset();
      loadPlayers();
    })
    .catch(error => {
      alert(`Error adding player: ${error.message}`);
    });
}

function loadStatistics() {
  showSection(dashboardSection);
  contentArea.innerHTML = '<h3>Loading statistics...</h3>';
  
  db.collection('ageGroups').get()
    .then(snapshot => {
      if (snapshot.empty) {
        contentArea.innerHTML = '<h3>No statistics found</h3>';
        return;
      }
      
      let tableHTML = `
        <h3>Academy Statistics</h3>
        <table>
          <thead>
            <tr>
              <th>Age Group</th>
              <th>Total Players</th>
              <th>Budget</th>
              <th>Net</th>
              <th>FT Players</th>
              <th>PT Players</th>
              <th>SC Players</th>
              <th>Trial Players</th>
            </tr>
          </thead>
          <tbody>
      `;
      
      snapshot.forEach(doc => {
        const ageGroup = doc.data();
        tableHTML += `
          <tr>
            <td>${ageGroup.name}</td>
            <td>${ageGroup.total || 0}</td>
            <td>${ageGroup.budget || 0}</td>
            <td>${(ageGroup.budget || 0) - (ageGroup.total || 0)}</td>
            <td>${ageGroup.ftPlayers || 0}</td>
            <td>${ageGroup.ptPlayers || 0}</td>
            <td>${ageGroup.scPlayers || 0}</td>
            <td>${ageGroup.trialPlayers || 0}</td>
          </tr>
        `;
      });
      
      tableHTML += `
          </tbody>
        </table>
      `;
      
      contentArea.innerHTML = tableHTML;
    })
    .catch(error => {
      contentArea.innerHTML = `<h3>Error loading statistics: ${error.message}</h3>`;
    });
}

// Global functions for table actions
window.editPlayer = function(playerId) {
  // Implementation for editing a player
  alert(`Edit player with ID: ${playerId}`);
};

window.deletePlayer = function(playerId) {
  if (confirm('Are you sure you want to delete this player?')) {
    db.collection('players').doc(playerId).delete()
      .then(() => {
        alert('Player deleted successfully!');
        loadPlayers();
      })
      .catch(error => {
        alert(`Error deleting player: ${error.message}`);
      });
  }
};
