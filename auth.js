document.addEventListener('DOMContentLoaded', () => {

  const tabSignIn = document.getElementById('tabSignIn');
  const tabRegister = document.getElementById('tabRegister');
  const signInForm = document.getElementById('signInForm');
  const registerForm = document.getElementById('registerForm');
  const toastBox = document.getElementById('toastNotification');

  const adminLogoBtn = document.getElementById('adminLogoBtn');
  const adminModal = document.getElementById('adminModal');
  const closeAdminModal = document.getElementById('closeAdminModal');
  const btnAdminDirectAuthorize = document.getElementById('btnAdminDirectAuthorize');

  const fillDemoUser = document.getElementById('fillDemoUser');
  const fillAdmin = document.getElementById('fillAdmin');

  function showToast(message, type = 'success') {
    if (!toastBox) return;
    toastBox.textContent = message;
    toastBox.className = `neu-toast show ${type}`;
    setTimeout(() => {
      toastBox.className = 'neu-toast';
    }, 3800);
  }

  tabSignIn.addEventListener('click', () => {
    tabSignIn.classList.add('active');
    tabRegister.classList.remove('active');
    signInForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
  });

  tabRegister.addEventListener('click', () => {
    tabRegister.classList.add('active');
    tabSignIn.classList.remove('active');
    registerForm.classList.remove('hidden');
    signInForm.classList.add('hidden');
  });

  if (fillDemoUser) {
    fillDemoUser.addEventListener('click', () => {
      document.getElementById('loginUsername').value = 'melodymaster';
      document.getElementById('loginPassword').value = 'user123';
      showToast('Filled Demo User credentials.', 'success');
    });
  }


  if (adminLogoBtn && adminModal) {
    adminLogoBtn.addEventListener('click', () => {
      adminModal.classList.add('open');
    });

    closeAdminModal.addEventListener('click', () => {
      adminModal.classList.remove('open');
    });

    adminModal.addEventListener('click', (e) => {
      if (e.target === adminModal) {
        adminModal.classList.remove('open');
      }
    });

    if (btnAdminDirectAuthorize) {
      btnAdminDirectAuthorize.addEventListener('click', async () => {
        try {
          const res = await fetch('/api/admin-quick-login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key: 'sonoraAdmin2024' })
          });
          const data = await res.json();
          if (data.success) {
            showToast('Administrator session authorized! Redirecting...', 'success');
            setTimeout(() => {
              window.location.href = data.redirect || '/admin';
            }, 800);
          } else {
            showToast(data.message || 'Authorization failed.', 'error');
          }
        } catch (err) {
          showToast('Network error authorizing admin session.', 'error');
        }
      });
    }
  }

  
  // 5. Sign In Form Submission
  signInForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!username || !password) {
      showToast('Please enter both username and password.', 'error');
      return;
    }

    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();

      if (data.success) {
        showToast(data.message || 'Sign in successful!', 'success');
        setTimeout(() => {
          window.location.href = data.redirect || '/dashboard';
        }, 700);
      } else {
        showToast(data.message || 'Invalid credentials.', 'error');
      }
    } catch (err) {
      showToast('Server connection error. Please try again.', 'error');
    }
  });

  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('regUsername').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;
    const genre = document.getElementById('regGenre').value;

    if (username.length < 3) {
      showToast('Username must have at least 3 characters.', 'error');
      return;
    }
    if (!email.includes('@') || !email.includes('.')) {
      showToast('Please provide a valid email address.', 'error');
      return;
    }
    if (password.length < 6) {
      showToast('Password must be at least 6 characters.', 'error');
      return;
    }

    try {
      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password, genre })
      });
      const data = await res.json();

      if (data.success) {
        showToast('Account created successfully! Welcome.', 'success');
        setTimeout(() => {
          window.location.href = data.redirect || '/dashboard';
        }, 800);
      } else {
        showToast(data.message || 'Registration failed.', 'error');
      }
    } catch (err) {
      showToast('Server connection error. Please try again.', 'error');
    }
  });
});

