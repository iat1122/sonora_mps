document.addEventListener('DOMContentLoaded', () => {
  const profileForm = document.getElementById('profileForm');
  const passwordForm = document.getElementById('passwordForm');
  const toastBox = document.getElementById('toastNotification');
  const displayUsername = document.getElementById('displayUsername');

  function showToast(message, type = 'success') {
    if (!toastBox) return;
    toastBox.textContent = message;
    toastBox.className = `neu-toast show ${type}`;
    setTimeout(() => {
      toastBox.className = 'neu-toast';
    }, 3500);
  }

  if (profileForm) {
    profileForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const username = document.getElementById('settingUsername').value.trim();
      const email = document.getElementById('settingEmail').value.trim();
      const bio = document.getElementById('settingBio').value.trim();
      const favorite_genre = document.getElementById('settingGenre').value;

      if (username.length < 3) {
        showToast('Username must be at least 3 characters.', 'error');
        return;
      }
      if (!email.includes('@') || !email.includes('.')) {
        showToast('Please provide a valid email.', 'error');
        return;
      }

      try {
        const res = await fetch('/api/user/profile', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, email, bio, favorite_genre })
        });
        const data = await res.json();

        if (data.success) {
          showToast(data.message || 'Profile updated successfully!', 'success');
          if (displayUsername) displayUsername.textContent = username;
        } else {
          showToast(data.message || 'Update failed.', 'error');
        }
      } catch (err) {
        showToast('Network error while saving profile.', 'error');
      }
    });
  }

  if (passwordForm) {
    passwordForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const old_password = document.getElementById('currentPassword').value;
      const new_password = document.getElementById('newPassword').value;
      const confirm_password = document.getElementById('confirmPassword').value;

      if (!old_password) {
        showToast('Please enter your current password.', 'error');
        return;
      }
      if (new_password.length < 6) {
        showToast('New password must be at least 6 characters.', 'error');
        return;
      }
      if (new_password !== confirm_password) {
        showToast('New passwords do not match. Please re-enter.', 'error');
        return;
      }

      try {
        const res = await fetch('/api/user/password', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ old_password, new_password })
        });
        const data = await res.json();

        if (data.success) {
          showToast(data.message || 'Password changed successfully!', 'success');
          passwordForm.reset();
        } else {
          showToast(data.message || 'Could not change password.', 'error');
        }
      } catch (err) {
        showToast('Network error changing password.', 'error');
      }
    });
  }
});

