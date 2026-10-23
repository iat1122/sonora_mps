import sqlite3
import os
from typing import List, Dict, Any, Optional
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'sonora.db')


def get_db_connection() -> sqlite3.Connection:
    """Create and return a database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Initialize database tables and seed default data if not already present."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            bio TEXT DEFAULT '',
            favorite_genre TEXT DEFAULT 'Lo-Fi',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Songs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            album TEXT DEFAULT '',
            genre TEXT NOT NULL,
            duration INTEGER NOT NULL, -- duration in seconds
            release_year INTEGER DEFAULT 2024,
            audio_url TEXT DEFAULT '',
            cover_color TEXT DEFAULT '#E09F3E',
            play_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Playlists Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # 4. Playlist Songs Table (Ordered list inside playlist)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlist_songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id INTEGER NOT NULL,
            song_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
            FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
            UNIQUE(playlist_id, song_id)
        )
    """)

    # 5. Listening History Table (LIFO Stack persistent tracking)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listening_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            song_id INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
        )
    """)

    conn.commit()

    # Seed Default Static Admin & Demo User
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    if user_count == 0:
        # Static Admin account (also verifiable in code)
        admin_pass_hash = generate_password_hash("sonoraAdmin2024")
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, bio, favorite_genre)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('admin', 'admin@sonora.internal', admin_pass_hash, 'admin', 'Sonora System Administrator', 'All'))

        # Demo regular user for quick testing
        demo_pass_hash = generate_password_hash("user123")
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, bio, favorite_genre)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('melodymaster', 'listener@sonora.com', demo_pass_hash, 'user', 'Music enthusiast and playlist curator.', 'Lo-Fi'))
        conn.commit()

    # Seed Default Music Catalog if empty
    cursor.execute("SELECT COUNT(*) FROM songs")
    song_count = cursor.fetchone()[0]
    if song_count == 0:
        seed_songs = [
            ("Midnight City Reverie", "Neon Echo", "Nocturnal Dreams", "Synthwave", 214, 2023, "", "#E09F3E"),
            ("Amber Sunset Serenade", "Aura Strings", "Golden Horizons", "Acoustic", 185, 2024, "", "#9E2A2B"),
            ("Burgundy Velvet Rain", "Miles Monroe", "Late Night Sessions", "Jazz", 248, 2022, "", "#540B0E"),
            ("Vanilla Cream Chill", "Lo-Fi Odyssey", "Study Beats Vol. 1", "Lo-Fi", 162, 2024, "", "#FFF3B0"),
            ("Electric Solitude", "Cyberpulse", "Digital Heartbeat", "Electronic", 220, 2023, "", "#E09F3E"),
            ("Deep Mahogany Blues", "Sonora Collective", "Soul Reflections", "Blues", 265, 2021, "", "#540B0E"),
            ("Golden Hour Haze", "Solaris Duo", "Sundown Echoes", "Lo-Fi", 175, 2024, "", "#E09F3E"),
            ("Crimson Moon Waltz", "Clara Sterling", "Modern Sonata", "Classical", 230, 2022, "", "#9E2A2B"),
            ("Rustic Highway Breeze", "The Drifters", "Desert Highway", "Indie Rock", 198, 2023, "", "#9E2A2B"),
            ("Champagne Glow", "Silk & Brass", "Cocktail Lounge", "Jazz", 210, 2024, "", "#FFF3B0"),
            ("Echoes of Eternity", "Starlight Ensemble", "Celestial Voyage", "Ambient", 290, 2023, "", "#540B0E"),
            ("Neon Boulevard Drive", "Retro Rider", "Synth Avenue", "Synthwave", 204, 2024, "", "#E09F3E"),
            ("Coffee Shop Morning", "Paperback Sound", "Sunday Pages", "Acoustic", 158, 2022, "", "#9E2A2B"),
            ("Velvet Underground Beat", "DJ Subharmonic", "Urban Pulse", "Electronic", 240, 2024, "", "#540B0E"),
            ("Whispering Willows", "Aria Frost", "Acoustic Journal", "Folk", 192, 2023, "", "#FFF3B0"),
        ]

        cursor.executemany("""
            INSERT INTO songs (title, artist, album, genre, duration, release_year, audio_url, cover_color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_songs)
        conn.commit()

        # Seed sample playlist for demo user
        cursor.execute("SELECT id FROM users WHERE username = 'melodymaster'")
        user_row = cursor.fetchone()
        if user_row:
            user_id = user_row['id']
            cursor.execute("""
                INSERT INTO playlists (user_id, name, description)
                VALUES (?, ?, ?)
            """, (user_id, "Chill Vibes & Study", "Mellow acoustic and lo-fi tracks for deep focus."))
            playlist_id = cursor.lastrowid

            # Add first 4 songs to this playlist
            for pos, s_id in enumerate([1, 2, 4, 7]):
                cursor.execute("""
                    INSERT INTO playlist_songs (playlist_id, song_id, position)
                    VALUES (?, ?, ?)
                """, (playlist_id, s_id, pos))
            conn.commit()

    conn.close()


# ============================================================================
# HELPER QUERY FUNCTIONS (CRUD)
# ============================================================================

def get_all_songs() -> List[Dict[str, Any]]:
    """Fetch all songs ordered by ID."""
    conn = get_db_connection()
    songs = conn.execute("SELECT * FROM songs ORDER BY id ASC").fetchall()
    conn.close()
    return [dict(s) for s in songs]


def get_song_by_id(song_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single song by ID."""
    conn = get_db_connection()
    song = conn.execute("SELECT * FROM songs WHERE id = ?", (song_id,)).fetchone()
    conn.close()
    return dict(song) if song else None


def add_song(title: str, artist: str, album: str, genre: str, duration: int,
             release_year: int, audio_url: str = '', cover_color: str = '#E09F3E') -> int:
    """Insert a new song into database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO songs (title, artist, album, genre, duration, release_year, audio_url, cover_color)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, artist, album, genre, duration, release_year, audio_url, cover_color))
    conn.commit()
    song_id = cursor.lastrowid
    conn.close()
    return song_id


def update_song(song_id: int, title: str, artist: str, album: str, genre: str,
                duration: int, release_year: int, audio_url: str = '') -> bool:
    """Update song metadata."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE songs
        SET title = ?, artist = ?, album = ?, genre = ?, duration = ?, release_year = ?, audio_url = ?
        WHERE id = ?
    """, (title, artist, album, genre, duration, release_year, audio_url, song_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def delete_song(song_id: int) -> bool:
    """Delete a song by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM songs WHERE id = ?", (song_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def increment_play_count(song_id: int) -> None:
    """Increment song play count and record user listening if applicable."""
    conn = get_db_connection()
    conn.execute("UPDATE songs SET play_count = play_count + 1 WHERE id = ?", (song_id,))
    conn.commit()
    conn.close()


def record_history(user_id: int, song_id: int) -> None:
    """Record listening event for user."""
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO listening_history (user_id, song_id)
        VALUES (?, ?)
    """, (user_id, song_id))
    conn.commit()
    conn.close()


def get_user_history(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieve user listening history with song details."""
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT h.id as history_id, h.played_at, s.*
        FROM listening_history h
        JOIN songs s ON h.song_id = s.id
        WHERE h.user_id = ?
        ORDER BY h.played_at DESC, h.id DESC
        LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_playlists(user_id: int) -> List[Dict[str, Any]]:
    """Fetch all playlists for a specific user with song count."""
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT p.*, COUNT(ps.id) as song_count
        FROM playlists p
        LEFT JOIN playlist_songs ps ON p.id = ps.playlist_id
        WHERE p.user_id = ?
        GROUP BY p.id
        ORDER BY p.id DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_playlist_details(playlist_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """Get playlist info and all included songs ordered by position."""
    conn = get_db_connection()
    playlist = conn.execute("SELECT * FROM playlists WHERE id = ? AND user_id = ?", (playlist_id, user_id)).fetchone()
    if not playlist:
        conn.close()
        return None

    songs = conn.execute("""
        SELECT s.*, ps.position, ps.added_at, ps.id as playlist_item_id
        FROM playlist_songs ps
        JOIN songs s ON ps.song_id = s.id
        WHERE ps.playlist_id = ?
        ORDER BY ps.position ASC
    """, (playlist_id,)).fetchall()

    conn.close()
    return {
        'playlist': dict(playlist),
        'songs': [dict(s) for s in songs]
    }


def create_playlist(user_id: int, name: str, description: str = '') -> int:
    """Create a new playlist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO playlists (user_id, name, description)
        VALUES (?, ?, ?)
    """, (user_id, name, description))
    conn.commit()
    p_id = cursor.lastrowid
    conn.close()
    return p_id


def delete_playlist(playlist_id: int, user_id: int) -> bool:
    """Delete playlist if owned by user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM playlists WHERE id = ? AND user_id = ?", (playlist_id, user_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def add_song_to_playlist(playlist_id: int, song_id: int) -> bool:
    """Add a song to playlist at the highest position."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check max position
    cursor.execute("SELECT COALESCE(MAX(position), -1) FROM playlist_songs WHERE playlist_id = ?", (playlist_id,))
    max_pos = cursor.fetchone()[0]
    next_pos = max_pos + 1

    try:
        cursor.execute("""
            INSERT INTO playlist_songs (playlist_id, song_id, position)
            VALUES (?, ?, ?)
        """, (playlist_id, song_id, next_pos))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False  # already in playlist
    conn.close()
    return success


def remove_song_from_playlist(playlist_id: int, song_id: int) -> bool:
    """Remove a song from a playlist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM playlist_songs WHERE playlist_id = ? AND song_id = ?", (playlist_id, song_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve user record."""
    conn = get_db_connection()
    user = conn.execute("SELECT id, username, email, role, bio, favorite_genre, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None


def update_user_profile(user_id: int, username: str, email: str, bio: str, favorite_genre: str) -> bool:
    """Update user profile information."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users
            SET username = ?, email = ?, bio = ?, favorite_genre = ?
            WHERE id = ?
        """, (username, email, bio, favorite_genre, user_id))
        conn.commit()
        affected = cursor.rowcount > 0
    except sqlite3.IntegrityError:
        affected = False
    conn.close()
    return affected


def update_user_password(user_id: int, new_password_hash: str) -> bool:
    """Update user password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
    conn.commit()
    affected = cursor.rowcount > 0
    conn.close()
    return affected


def get_admin_metrics() -> Dict[str, Any]:
    """Retrieve system overview metrics for the Admin Dashboard."""
    conn = get_db_connection()
    total_songs = conn.execute("SELECT COUNT(*) FROM songs").fetchone()[0]
    total_users = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'user'").fetchone()[0]
    total_playlists = conn.execute("SELECT COUNT(*) FROM playlists").fetchone()[0]
    total_plays = conn.execute("SELECT COALESCE(SUM(play_count), 0) FROM songs").fetchone()[0]

    # Most played songs
    top_songs = conn.execute("""
        SELECT id, title, artist, play_count, genre
        FROM songs
        ORDER BY play_count DESC, id ASC
        LIMIT 5
    """).fetchall()

    # Genre distribution
    genres = conn.execute("""
        SELECT genre, COUNT(*) as count
        FROM songs
        GROUP BY genre
        ORDER BY count DESC
    """).fetchall()

    conn.close()
    return {
        'total_songs': total_songs,
        'total_users': total_users,
        'total_playlists': total_playlists,
        'total_plays': total_plays,
        'top_songs': [dict(s) for s in top_songs],
        'genres': [dict(g) for g in genres]
    }

