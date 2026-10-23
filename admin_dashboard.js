class SonoraAdminDashboard {
  constructor() {
    this.catalogSongs = [];
    this.toastBox = document.getElementById('toastNotification');

    this.tableBody = document.getElementById('adminSongsTableBody');
    this.searchInput = document.getElementById('adminCatalogSearch');
    this.btnOpenPublishModal = document.getElementById('btnOpenPublishModal');
    this.publishModal = document.getElementById('publishModal');
    this.closePublishModal = document.getElementById('closePublishModal');
    this.publishForm = document.getElementById('publishSongForm');

    this.editModal = document.getElementById('editSongModal');
    this.closeEditModal = document.getElementById('closeEditModal');
    this.editForm = document.getElementById('editSongForm');
    this.editSongIdInput = document.getElementById('editSongId');

    this.kpiTotalSongs = document.getElementById('kpiTotalSongs');

    this.init();
  }

  async init() {
    this.setupEventListeners();
    await this.loadCatalog();
  }

  setupEventListeners() {
    if (this.searchInput) {
      this.searchInput.addEventListener('input', () => {
        const query = this.searchInput.value.toLowerCase().trim();
        this.filterTable(query);
      });
    }

    if (this.btnOpenPublishModal) {
      this.btnOpenPublishModal.addEventListener('click', () => {
        this.publishModal.classList.add('open');
      });
      this.closePublishModal.addEventListener('click', () => {
        this.publishModal.classList.remove('open');
      });
      this.publishForm.addEventListener('submit', (e) => this.handlePublishSong(e));
    }

    if (this.closeEditModal) {
      this.closeEditModal.addEventListener('click', () => {
        this.editModal.classList.remove('open');
      });
      this.editForm.addEventListener('submit', (e) => this.handleUpdateSong(e));
    }
  }

  showToast(message, type = 'success') {
    if (!this.toastBox) return;
    this.toastBox.textContent = message;
    this.toastBox.className = `neu-toast show ${type}`;
    setTimeout(() => {
      this.toastBox.className = 'neu-toast';
    }, 3500);
  }

  async loadCatalog() {
    try {
      const res = await fetch('/api/songs');
      const data = await res.json();
      if (data.success) {
        this.catalogSongs = data.songs;
        this.renderTable(this.catalogSongs);
        if (this.kpiTotalSongs) {
          this.kpiTotalSongs.textContent = data.songs.length;
        }
      }
    } catch (e) {
      this.tableBody.innerHTML = '<tr><td colspan="9" class="empty-note">Failed to load catalog.</td></tr>';
    }
  }

  renderTable(songs) {
    if (!songs || songs.length === 0) {
      this.tableBody.innerHTML = '<tr><td colspan="9" class="empty-note">No tracks found.</td></tr>';
      return;
    }

    this.tableBody.innerHTML = songs.map(s => {
      const durationFormatted = this.formatDuration(s.duration);
      return `
        <tr id="adminRow-${s.id}">
          <td style="font-family:var(--font-mono); color:var(--c-amber);">${s.id}</td>
          <td><strong>${this.escapeHtml(s.title)}</strong></td>
          <td>${this.escapeHtml(s.artist)}</td>
          <td>${this.escapeHtml(s.album || '-')}</td>
          <td><span class="neu-badge neu-badge-burgundy">${this.escapeHtml(s.genre)}</span></td>
          <td style="font-family:var(--font-mono);">${durationFormatted}</td>
          <td>${s.release_year || 2024}</td>
          <td style="font-weight:700; color:var(--c-amber);">${s.play_count || 0}</td>
          <td>
            <div class="table-actions">
              <button class="neu-btn btn-sm" onclick="window.adminDashboard.openEditModal(${s.id})">Edit</button>
              <button class="neu-btn btn-sm btn-delete-song" onclick="window.adminDashboard.deleteSong(${s.id}, '${this.escapeHtml(s.title)}')">Delete</button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  }

  filterTable(query) {
    if (!query) {
      this.renderTable(this.catalogSongs);
      return;
    }
    const filtered = this.catalogSongs.filter(s =>
      s.title.toLowerCase().includes(query) ||
      s.artist.toLowerCase().includes(query) ||
      s.genre.toLowerCase().includes(query) ||
      (s.album && s.album.toLowerCase().includes(query))
    );
    this.renderTable(filtered);
  }

  formatDuration(seconds) {
    const s = Math.floor(seconds || 0);
    const mins = Math.floor(s / 60);
    const secs = s % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  }

  escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/[&<>'"]/g, tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag));
  }

  async handlePublishSong(e) {
    e.preventDefault();
    const title = document.getElementById('pubTitle').value.trim();
    const artist = document.getElementById('pubArtist').value.trim();
    const album = document.getElementById('pubAlbum').value.trim();
    const genre = document.getElementById('pubGenre').value;
    const duration = parseInt(document.getElementById('pubDuration').value);
    const year = parseInt(document.getElementById('pubYear').value) || 2024;
    const audioUrl = document.getElementById('pubAudioUrl').value.trim();

    if (!title || !artist || !genre || !duration) {
      this.showToast('Please fill out all required fields.', 'error');
      return;
    }

    try {
      const res = await fetch('/api/admin/songs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title, artist, album, genre, duration, release_year: year, audio_url: audioUrl
        })
      });
      const data = await res.json();
      if (data.success) {
        this.showToast(data.message, 'success');
        this.publishModal.classList.remove('open');
        this.publishForm.reset();
        await this.loadCatalog();
      } else {
        this.showToast(data.message || 'Publishing failed.', 'error');
      }
    } catch (err) {
      this.showToast('Server error while publishing track.', 'error');
    }
  }

  openEditModal(songId) {
    const song = this.catalogSongs.find(s => s.id === songId);
    if (!song) return;

    this.editSongIdInput.value = song.id;
    document.getElementById('editTitle').value = song.title;
    document.getElementById('editArtist').value = song.artist;
    document.getElementById('editAlbum').value = song.album || '';
    document.getElementById('editGenre').value = song.genre;
    document.getElementById('editDuration').value = song.duration;
    document.getElementById('editYear').value = song.release_year || 2024;
    document.getElementById('editAudioUrl').value = song.audio_url || '';

    this.editModal.classList.add('open');
  }

  async handleUpdateSong(e) {
    e.preventDefault();
    const songId = this.editSongIdInput.value;
    const title = document.getElementById('editTitle').value.trim();
    const artist = document.getElementById('editArtist').value.trim();
    const album = document.getElementById('editAlbum').value.trim();
    const genre = document.getElementById('editGenre').value;
    const duration = parseInt(document.getElementById('editDuration').value);
    const year = parseInt(document.getElementById('editYear').value) || 2024;
    const audioUrl = document.getElementById('editAudioUrl').value.trim();

    try {
      const res = await fetch(`/api/admin/songs/${songId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title, artist, album, genre, duration, release_year: year, audio_url: audioUrl
        })
      });
      const data = await res.json();
      if (data.success) {
        this.showToast(data.message, 'success');
        this.editModal.classList.remove('open');
        await this.loadCatalog();
      } else {
        this.showToast(data.message || 'Update failed', 'error');
      }
    } catch (err) {
      this.showToast('Server error updating track', 'error');
    }
  }

  
  async deleteSong(songId, songTitle) {
    if (!confirm(`Are you sure you want to delete "${songTitle}" from the catalog? This cannot be undone.`)) {
      return;
    }

    try {
      const res = await fetch(`/api/admin/songs/${songId}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        this.showToast(`"${songTitle}" removed from catalog.`, 'success');
        await this.loadCatalog();
      } else {
        this.showToast(data.message || 'Deletion failed', 'error');
      }
    } catch (err) {
      this.showToast('Network error while deleting track', 'error');
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.adminDashboard = new SonoraAdminDashboard();
});

