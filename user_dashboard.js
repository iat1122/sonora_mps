class SonoraUserDashboard {
  constructor() {
    this.allSongs = [];
    this.currentDisplayedSongs = [];
    this.userPlaylists = [];
    this.activeGenre = 'all';

    this.songsContainer = document.getElementById('songsListContainer');
    this.playlistsContainer = document.getElementById('playlistsContainer');
    this.queueContainer = document.getElementById('queueContainer');
    this.historyContainer = document.getElementById('historyContainer');
    this.searchInput = document.getElementById('searchInput');
    this.sortKeySelect = document.getElementById('sortKeySelect');
    this.toastBox = document.getElementById('toastNotification');

    // Modals
    this.createPlaylistModal = document.getElementById('createPlaylistModal');
    this.closePlaylistModal = document.getElementById('closePlaylistModal');
    this.btnOpenCreatePlaylistModal = document.getElementById('btnOpenCreatePlaylistModal');
    this.createPlaylistForm = document.getElementById('createPlaylistForm');
    this.addToPlaylistModal = document.getElementById('addToPlaylistModal');
    this.closeAddToPlaylistModal = document.getElementById('closeAddToPlaylistModal');
    this.modalPlaylistOptions = document.getElementById('modalPlaylistOptions');
    this.targetSongIdInput = document.getElementById('targetSongId');

    // Admin Logo Modal References
    this.navLogoBtn = document.getElementById('navLogoBtn');
    this.adminModal = document.getElementById('adminModal');
    this.closeAdminModal = document.getElementById('closeAdminModal');
    this.btnAdminAuthorize = document.getElementById('btnAdminAuthorize');

    // Queue buttons
    this.btnClearQueue = document.getElementById('btnClearQueue');
    this.btnUndoStack = document.getElementById('btnUndoStack');

    this.init();
  }

  async init() {
    this.setupEventListeners();
    await this.loadCatalog();
    await this.loadPlaylists();
    await this.refreshQueue();
    await this.refreshHistory();
  }

  setupEventListeners() {
    // Search input typing
    let searchTimeout = null;
    this.searchInput.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => this.executeSearch(), 250);
    });

    // Sort key — re-sorts automatically when changed
    this.sortKeySelect.addEventListener('change', () => this.executeSort());

    // Genre pills
    const genreBar = document.getElementById('genreBar');
    if (genreBar) {
      genreBar.addEventListener('click', (e) => {
        const pill = e.target.closest('.genre-pill');
        if (pill) {
          genreBar.querySelectorAll('.genre-pill').forEach(p => p.classList.remove('active'));
          pill.classList.add('active');
          this.activeGenre = pill.dataset.genre;
          this.filterByGenre(this.activeGenre);
        }
      });
    }


    // Create Playlist Modal
    if (this.btnOpenCreatePlaylistModal) {
      this.btnOpenCreatePlaylistModal.addEventListener('click', () => {
        this.createPlaylistModal.classList.add('open');
      });
      this.closePlaylistModal.addEventListener('click', () => {
        this.createPlaylistModal.classList.remove('open');
      });
      this.createPlaylistForm.addEventListener('submit', (e) => this.handleCreatePlaylist(e));
    }

    // Add to Playlist Modal
    if (this.closeAddToPlaylistModal) {
      this.closeAddToPlaylistModal.addEventListener('click', () => {
        this.addToPlaylistModal.classList.remove('open');
      });
    }

    // Queue & Stack Actions
    if (this.btnClearQueue) {
      this.btnClearQueue.addEventListener('click', async () => {
        await fetch('/api/queue', { method: 'DELETE' });
        this.refreshQueue();
        this.showToast('Up Next list cleared.', 'success');
      });
    }

    if (this.btnUndoStack) {
      this.btnUndoStack.addEventListener('click', async () => {
        const res = await fetch('/api/history', { method: 'DELETE' });
        const data = await res.json();
        if (data.success && data.popped) {
          this.showToast(`Removed "${data.popped.title}" from your listening history`, 'success');
          this.refreshHistory();
        } else {
          this.showToast('Your listening history is empty.', 'error');
        }
      });
    }

    // Nav link buttons
    const btnNavCatalog = document.getElementById('btnNavCatalog');
    const btnNavPlaylists = document.getElementById('btnNavPlaylists');
    if (btnNavCatalog && btnNavPlaylists) {
      btnNavCatalog.addEventListener('click', () => {
        document.querySelectorAll('.nav-link-btn').forEach(b => b.classList.remove('active'));
        btnNavCatalog.classList.add('active');
        this.loadCatalog();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
      btnNavPlaylists.addEventListener('click', () => {
        document.querySelectorAll('.nav-link-btn').forEach(b => b.classList.remove('active'));
        btnNavPlaylists.classList.add('active');
        this.loadPlaylists();
        const sidebar = document.querySelector('.sidebar-section');
        if (sidebar) sidebar.scrollIntoView({ behavior: 'smooth' });
      });
    }
    if (this.navLogoBtn && this.adminModal) {
      this.navLogoBtn.addEventListener('click', () => {
        this.adminModal.classList.add('open');
      });
      this.closeAdminModal.addEventListener('click', () => {
        this.adminModal.classList.remove('open');
      });
      this.btnAdminAuthorize.addEventListener('click', async () => {
        try {
          const res = await fetch('/api/admin-quick-login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key: 'sonoraAdmin2024' })
          });
          const data = await res.json();
          if (data.success) {
            this.showToast('Admin session authorized! Switching...', 'success');
            setTimeout(() => {
              window.location.href = data.redirect || '/admin';
            }, 600);
          }
        } catch (e) {
          this.showToast('Failed to authorize admin session', 'error');
        }
      });
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
        this.allSongs = data.songs;
        this.currentDisplayedSongs = data.songs;
        if (window.sonoraPlayer) {
          window.sonoraPlayer.currentPlaylist = data.songs;
        }
        this.renderSongsTable(this.currentDisplayedSongs);
      }
    } catch (e) {
      this.songsContainer.innerHTML = '<div class="empty-note">Failed to load songs catalog.</div>';
    }
  }

  renderSongsTable(songs) {
    if (!songs || songs.length === 0) {
      this.songsContainer.innerHTML = '<div class="empty-note">No tracks match your query.</div>';
      return;
    }

    this.songsContainer.innerHTML = songs.map((s, idx) => {
      const durationFormatted = this.formatDuration(s.duration);
      return `
        <div class="song-row" id="songRow-${s.id}" data-id="${s.id}">
          <span class="col-index">${idx + 1}</span>
          <div class="col-title-artist" onclick="window.userDashboard.playSong(${s.id})">
            <span class="row-title">${this.escapeHtml(s.title)}</span>
            <span class="row-artist">${this.escapeHtml(s.artist)} &bull; ${this.escapeHtml(s.album || 'Single')}</span>
          </div>
          <span class="col-genre">
            <span class="neu-badge neu-badge-burgundy">${this.escapeHtml(s.genre)}</span>
          </span>
          <span class="col-duration">${durationFormatted}</span>
          <div class="col-actions">
            <!-- Play Now Button -->
            <button class="neu-btn neu-btn-primary btn-action-icon" title="Play Now" onclick="window.userDashboard.playSong(${s.id})">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
            </button>
            <!-- Add to Up Next -->
            <button class="neu-btn btn-action-icon" title="Add to Up Next" onclick="window.userDashboard.addToQueue(${s.id})">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
            </button>
            <!-- Add to Playlist -->
            <button class="neu-btn btn-action-icon" title="Add to Playlist" onclick="window.userDashboard.openAddToPlaylistModal(${s.id}, '${this.escapeHtml(s.title)}')">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M14 10H2v2h12v-2zm0-4H2v2h12V6zm4 8v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zM2 16h8v-2H2v2z"/></svg>
            </button>
          </div>
        </div>
      `;
    }).join('');
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

  highlightPlayingRow(songId) {
    document.querySelectorAll('.song-row').forEach(r => r.classList.remove('playing'));
    const activeRow = document.getElementById(`songRow-${songId}`);
    if (activeRow) activeRow.classList.add('playing');
  }

  playSong(songId) {
    const song = this.allSongs.find(s => s.id === songId);
    if (song && window.sonoraPlayer) {
      window.sonoraPlayer.playSong(song);
    }
  }

  filterByGenre(genre) {
    if (genre === 'all') {
      this.currentDisplayedSongs = this.allSongs;
    } else {
      this.currentDisplayedSongs = this.allSongs.filter(s => (s.genre || '').toLowerCase() === genre.toLowerCase());
    }
    this.renderSongsTable(this.currentDisplayedSongs);
  }

  async executeSearch() {
    const query = this.searchInput.value.trim();

    try {
      const res = await fetch(`/api/dsa/search?q=${encodeURIComponent(query)}`);
      const data = await res.json();

      if (data.success) {
        this.currentDisplayedSongs = data.results || [];
        this.renderSongsTable(this.currentDisplayedSongs);
      }
    } catch (e) {
      console.error('Search error', e);
    }
  }

  
  async executeSort() {
    const key = this.sortKeySelect.value;

    try {
      const res = await fetch(`/api/dsa/sort?key=${key}&order=asc`);
      const data = await res.json();

      if (data.success) {
        this.currentDisplayedSongs = data.results || [];
        this.renderSongsTable(this.currentDisplayedSongs);
      }
    } catch (e) {
      console.error('Sort error', e);
    }
  }

  updateMetrics(algoName, stats) {
    if (this.metricAlgoName) this.metricAlgoName.textContent = algoName;
    if (this.metricStats) this.metricStats.textContent = stats;
  }


  async addToQueue(songId) {
    try {
      const res = await fetch('/api/queue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ song_id: songId })
      });
      const data = await res.json();
      if (data.success) {
        this.showToast(data.message, 'success');
        this.renderQueue(data.queue);
      }
    } catch (e) {
      this.showToast('Could not add to queue.', 'error');
    }
  }

  async refreshQueue() {
    try {
      const res = await fetch('/api/queue');
      const data = await res.json();
      if (data.success) {
        this.renderQueue(data.queue);
      }
    } catch (e) {
      console.warn('Queue refresh failed', e);
    }
  }

  renderQueue(items) {
    if (!this.queueContainer) return;
    if (!items || items.length === 0) {
      this.queueContainer.innerHTML = '<div class="empty-note">Your Up Next is empty. Tap "Up Next" on any song to add it!</div>';
      return;
    }

    this.queueContainer.innerHTML = items.map((s, idx) => `
      <div class="queue-item">
        <div class="item-left">
          <span class="item-title">${idx + 1}. ${this.escapeHtml(s.title)}</span>
          <span class="item-artist">${this.escapeHtml(s.artist)}</span>
        </div>
        <button class="neu-btn btn-sm" onclick="window.userDashboard.removeFromQueue(${s.id})">&times;</button>
      </div>
    `).join('');
  }

  async removeFromQueue(songId) {
    const res = await fetch(`/api/queue?song_id=${songId}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      this.renderQueue(data.queue);
    }
  }

  
  async refreshHistory() {
    try {
      const res = await fetch('/api/history');
      const data = await res.json();
      if (data.success) {
        this.renderHistory(data.history);
      }
    } catch (e) {
      console.warn('History refresh failed', e);
    }
  }

  renderHistory(items) {
    if (!this.historyContainer) return;
    if (!items || items.length === 0) {
      this.historyContainer.innerHTML = '<div class="empty-note">No tracks played yet.</div>';
      return;
    }

    this.historyContainer.innerHTML = items.slice(0, 10).map((s, idx) => `
      <div class="history-item">
        <div class="item-left">
          <span class="item-title">${idx === 0 ? 'Now playing: ' : ''}${this.escapeHtml(s.title)}</span>
          <span class="item-artist">${this.escapeHtml(s.artist)}</span>
        </div>
      </div>
    `).join('');
  }

 

  async loadPlaylists() {
    try {
      const res = await fetch('/api/playlists');
      const data = await res.json();
      if (data.success) {
        this.userPlaylists = data.playlists;
        this.renderPlaylists(data.playlists);
      }
    } catch (e) {
      this.playlistsContainer.innerHTML = '<div class="empty-note">Failed to load playlists.</div>';
    }
  }

  renderPlaylists(playlists) {
    if (!this.playlistsContainer) return;
    if (!playlists || playlists.length === 0) {
      this.playlistsContainer.innerHTML = '<div class="empty-note">No playlists created yet. Click "+ New".</div>';
      return;
    }

    this.playlistsContainer.innerHTML = playlists.map(p => `
      <div class="playlist-item" onclick="window.userDashboard.loadPlaylistTracks(${p.id})">
        <div class="item-left">
          <span class="playlist-name">${this.escapeHtml(p.name)}</span>
          <span class="playlist-count">${p.song_count || 0} songs</span>
        </div>
        <button class="neu-btn btn-sm" title="Delete playlist" onclick="event.stopPropagation(); window.userDashboard.deletePlaylist(${p.id})">&times;</button>
      </div>
    `).join('');
  }

  async handleCreatePlaylist(e) {
    e.preventDefault();
    const name = document.getElementById('playlistNameInput').value.trim();
    const desc = document.getElementById('playlistDescInput').value.trim();

    if (!name) return;

    try {
      const res = await fetch('/api/playlists', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description: desc })
      });
      const data = await res.json();
      if (data.success) {
        this.createPlaylistModal.classList.remove('open');
        this.createPlaylistForm.reset();
        this.showToast(data.message, 'success');
        this.loadPlaylists();
      }
    } catch (err) {
      this.showToast('Failed to create playlist', 'error');
    }
  }

  async loadPlaylistTracks(playlistId) {
    try {
      const res = await fetch(`/api/playlists/${playlistId}`);
      const data = await res.json();
      if (data.success) {
        this.currentDisplayedSongs = data.songs;
        this.renderSongsTable(data.songs);
        this.updateMetrics(`Playlist: ${data.playlist.name}`, `${data.songs.length} songs ready to play`);
        this.showToast(`Now viewing playlist: "${data.playlist.name}"`, 'success');
      }
    } catch (e) {
      this.showToast('Could not load playlist tracks', 'error');
    }
  }

  async deletePlaylist(playlistId) {
    if (!confirm('Are you sure you want to delete this playlist?')) return;
    try {
      const res = await fetch(`/api/playlists/${playlistId}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        this.showToast('Playlist deleted.', 'success');
        this.loadPlaylists();
      }
    } catch (e) {
      this.showToast('Could not delete playlist.', 'error');
    }
  }

  openAddToPlaylistModal(songId, songTitle) {
    this.targetSongIdInput.value = songId;
    document.getElementById('addToPlaylistSongTitle').textContent = `Add "${songTitle}" to Playlist:`;

    if (this.userPlaylists.length === 0) {
      this.modalPlaylistOptions.innerHTML = '<div class="empty-note">No playlists found. Create one first!</div>';
    } else {
      this.modalPlaylistOptions.innerHTML = this.userPlaylists.map(p => `
        <div class="playlist-item" onclick="window.userDashboard.confirmAddToPlaylist(${p.id})">
          <span class="playlist-name">${this.escapeHtml(p.name)}</span>
          <span class="neu-badge neu-badge-amber">+ Add</span>
        </div>
      `).join('');
    }

    this.addToPlaylistModal.classList.add('open');
  }

  async confirmAddToPlaylist(playlistId) {
    const songId = this.targetSongIdInput.value;
    try {
      const res = await fetch(`/api/playlists/${playlistId}/songs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ song_id: parseInt(songId) })
      });
      const data = await res.json();
      if (data.success) {
        this.showToast('Song added to playlist!', 'success');
        this.addToPlaylistModal.classList.remove('open');
        this.loadPlaylists();
      } else {
        this.showToast(data.message || 'Already in playlist', 'error');
      }
    } catch (e) {
      this.showToast('Could not add to playlist', 'error');
    }
  }

}

document.addEventListener('DOMContentLoaded', () => {
  window.userDashboard = new SonoraUserDashboard();
});

