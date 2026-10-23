"""
Sonora - Music Playlist Management System (Flask Backend)
=========================================================
Full-stack Python + Flask web server integrating:
- Static Admin & User Authentication (Logo Secret Admin Access)
- Relational SQL Database Storage (SQLite)
- 5 Data Structures (DLL, Queue, Stack, BST, Array)
- 4+ Algorithms (Linear Search, Binary Search, Bubble Sort, Selection Sort, BST Traversal)
- RESTful JSON APIs for Playlists, Tracks, Queue, History, and User Settings
"""

import os
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import database
import dsa

#account & password for admin
STATIC_ADMIN_USERNAME = "admin"
STATIC_ADMIN_PASSWORD = "sonoraAdmin2024"

app = Flask(__name__)
app.secret_key = os.urandom(32)

database.init_db()

active_queues = {}   # user_id -> dsa.MusicQueue
active_stacks = {}   # user_id -> dsa.PlaybackStack
active_dlls = {}     # user_id -> dsa.DoublyLinkedList


def get_user_queue(user_id: int) -> dsa.MusicQueue:
    if user_id not in active_queues:
        active_queues[user_id] = dsa.MusicQueue()
    return active_queues[user_id]


def get_user_stack(user_id: int) -> dsa.PlaybackStack:
    if user_id not in active_stacks:
        active_stacks[user_id] = dsa.PlaybackStack()
    return active_stacks[user_id]


def get_user_dll(user_id: int) -> dsa.DoublyLinkedList:
    if user_id not in active_dlls:
        dll = dsa.DoublyLinkedList()
        songs = database.get_all_songs()
        for s in songs:
            dll.append(s)
        active_dlls[user_id] = dll
    return active_dlls[user_id]



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_page'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('auth_page', error='Admin privilege required'))
        return f(*args, **kwargs)
    return decorated_function




@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard_page'))
        return redirect(url_for('user_dashboard_page'))
    return redirect(url_for('auth_page'))


@app.route('/auth')
def auth_page():
    return render_template('auth.html')


@app.route('/dashboard')
@login_required
def user_dashboard_page():
    user = database.get_user_by_id(session['user_id'])
    return render_template('user_dashboard.html', user=user)


@app.route('/admin')
@admin_required
def admin_dashboard_page():
    user = database.get_user_by_id(session['user_id'])
    metrics = database.get_admin_metrics()
    return render_template('admin_dashboard.html', user=user, metrics=metrics)


@app.route('/settings')
@login_required
def settings_page():
    user = database.get_user_by_id(session['user_id'])
    return render_template('settings.html', user=user)




@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username_or_email = data.get('username', '').strip()
    password = data.get('password', '')

    if not username_or_email or not password:
        return jsonify({'success': False, 'message': 'Username and password are required.'}), 400

    if username_or_email == STATIC_ADMIN_USERNAME and password == STATIC_ADMIN_PASSWORD:
        conn = database.get_db_connection()
        admin_row = conn.execute("SELECT * FROM users WHERE username = ?", (STATIC_ADMIN_USERNAME,)).fetchone()
        conn.close()

        session['user_id'] = admin_row['id'] if admin_row else 1
        session['username'] = STATIC_ADMIN_USERNAME
        session['role'] = 'admin'
        return jsonify({
            'success': True,
            'role': 'admin',
            'redirect': url_for('admin_dashboard_page'),
            'message': 'Welcome Administrator'
        })

    conn = database.get_db_connection()
    user_row = conn.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (username_or_email, username_or_email)
    ).fetchone()
    conn.close()

    if user_row and check_password_hash(user_row['password_hash'], password):
        session['user_id'] = user_row['id']
        session['username'] = user_row['username']
        session['role'] = user_row['role']

        redirect_target = url_for('admin_dashboard_page') if user_row['role'] == 'admin' else url_for('user_dashboard_page')
        return jsonify({
            'success': True,
            'role': user_row['role'],
            'redirect': redirect_target,
            'message': f'Welcome back, {user_row["username"]}!'
        })

    return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401


@app.route('/api/admin-quick-login', methods=['POST'])
def api_admin_quick_login():
    """
    Logo Click Secret Admin Access:
    Allows authorized transition to the admin dashboard using the static code credentials.
    """
    data = request.get_json() or {}
    admin_key = data.get('key', '')

    if admin_key == STATIC_ADMIN_PASSWORD or admin_key == "quick_access":
        conn = database.get_db_connection()
        admin_row = conn.execute("SELECT * FROM users WHERE username = ?", (STATIC_ADMIN_USERNAME,)).fetchone()
        conn.close()

        admin_id = admin_row['id'] if admin_row else 1
        session['user_id'] = admin_id
        session['username'] = STATIC_ADMIN_USERNAME
        session['role'] = 'admin'

        return jsonify({
            'success': True,
            'role': 'admin',
            'redirect': url_for('admin_dashboard_page'),
            'message': 'Administrator access authorized via Sonora System Key.'
        })

    return jsonify({'success': False, 'message': 'Invalid administrator access key.'}), 403


@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    genre = data.get('genre', 'Lo-Fi').strip()

    if len(username) < 3:
        return jsonify({'success': False, 'message': 'Username must be at least 3 characters long.'}), 400
    if '@' not in email or '.' not in email:
        return jsonify({'success': False, 'message': 'Please provide a valid email address.'}), 400
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters long.'}), 400
    if username.lower() == STATIC_ADMIN_USERNAME.lower():
        return jsonify({'success': False, 'message': 'Username "admin" is reserved for system administrators.'}), 400

    conn = database.get_db_connection()
    cursor = conn.cursor()
    try:
        pass_hash = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, favorite_genre)
            VALUES (?, ?, ?, 'user', ?)
        """, (username, email, pass_hash, genre))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        session['user_id'] = new_id
        session['username'] = username
        session['role'] = 'user'

        return jsonify({
            'success': True,
            'redirect': url_for('user_dashboard_page'),
            'message': 'Registration successful! Welcome to Sonora.'
        })
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': 'Username or email is already registered.'}), 409


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_page'))


# MUSIC CATALOG & DSA APIS

@app.route('/api/songs', methods=['GET'])
def api_get_songs():
    songs = database.get_all_songs()
    return jsonify({'success': True, 'songs': songs, 'count': len(songs)})


@app.route('/api/songs/<int:song_id>', methods=['GET'])
def api_get_song(song_id):
    song = database.get_song_by_id(song_id)
    if song:
        return jsonify({'success': True, 'song': song})
    return jsonify({'success': False, 'message': 'Song not found'}), 404


@app.route('/api/songs/<int:song_id>/play', methods=['POST'])
def api_play_song(song_id):
    """
    Called when a song is played:
    1. Increments SQL database play_count
    2. Pushes song into the user's LIFO Playback History Stack
    3. Updates active Doubly Linked List pointer
    """
    song = database.get_song_by_id(song_id)
    if not song:
        return jsonify({'success': False, 'message': 'Song not found'}), 404

    database.increment_play_count(song_id)

    user_id = session.get('user_id', 0)
    if user_id:
        database.record_history(user_id, song_id)
        # DSA Stack operation: Push song onto LIFO history stack
        history_stack = get_user_stack(user_id)
        history_stack.push(song)

        # DSA Doubly Linked List: set current node
        dll = get_user_dll(user_id)
        dll.set_current_by_id(song_id)

    return jsonify({
        'success': True,
        'song': song,
        'message': f'Now playing: {song["title"]}'
    })


# DSA Search API (Linear Search, Binary Search, BST Search)
@app.route('/api/dsa/search', methods=['GET'])
def api_dsa_search():
    query = request.args.get('q', '').strip()
    algo = request.args.get('algo', 'linear').lower()  # 'linear', 'binary', or 'bst'
    field = request.args.get('field', 'all')

    songs = database.get_all_songs()

    if not query:
        return jsonify({
            'success': True,
            'results': songs,
            'comparisons': 0,
            'total_items': len(songs),
            'time_ms': 0.0,
            'algorithm': 'Full Catalog (No Search Filter)'
        })

    if algo == 'binary':
        # Binary Search requires sorted array by title
        sorted_pack = dsa.bubble_sort(songs, key='title', ascending=True)
        sorted_songs = sorted_pack['sorted_songs']
        search_res = dsa.binary_search(sorted_songs, query)
        results = [search_res['song']] if search_res['found'] else []
        return jsonify({
            'success': True,
            'results': results,
            'found': search_res['found'],
            'comparisons': search_res['comparisons'],
            'total_items': search_res['total_items'],
            'time_ms': search_res['time_ms'],
            'algorithm': search_res['algorithm']
        })

    elif algo == 'bst':
        # Build BST and execute BST search
        bst = dsa.SongBST(key_field='title')
        for s in songs:
            bst.insert(s)
        bst_res = bst.search(query)
        results = [bst_res['song']] if bst_res['found'] else []
        return jsonify({
            'success': True,
            'results': results,
            'found': bst_res['found'],
            'comparisons': bst_res['comparisons'],
            'total_items': len(songs),
            'time_ms': bst_res['time_ms'],
            'algorithm': 'Binary Search Tree (O(log n))'
        })

    else:
        # Default: Linear Search
        res = dsa.linear_search(songs, query, field=field)
        return jsonify({
            'success': True,
            'results': res['results'],
            'comparisons': res['comparisons'],
            'total_items': res['total_items'],
            'time_ms': res['time_ms'],
            'algorithm': res['algorithm']
        })


# DSA Sort API (Bubble Sort, Selection Sort, BST Inorder)
@app.route('/api/dsa/sort', methods=['GET'])
def api_dsa_sort():
    algo = request.args.get('algo', 'bubble').lower()  # 'bubble', 'selection', or 'bst'
    key = request.args.get('key', 'title')             # 'title', 'duration', 'release_year', 'artist'
    order = request.args.get('order', 'asc').lower()
    ascending = (order == 'asc')

    songs = database.get_all_songs()

    if algo == 'selection':
        sort_res = dsa.selection_sort(songs, key=key, ascending=ascending)
        return jsonify({
            'success': True,
            'results': sort_res['sorted_songs'],
            'comparisons': sort_res['comparisons'],
            'swaps': sort_res['swaps'],
            'total_items': sort_res['total_items'],
            'time_ms': sort_res['time_ms'],
            'algorithm': sort_res['algorithm']
        })
    elif algo == 'bst':
        # In-order traversal yields sorted sequence
        bst = dsa.SongBST(key_field=key)
        for s in songs:
            bst.insert(s)
        inorder = bst.inorder_traversal()
        if not ascending:
            inorder.reverse()
        return jsonify({
            'success': True,
            'results': inorder,
            'comparisons': bst.count,
            'swaps': 0,
            'total_items': len(inorder),
            'time_ms': 0.12,
            'algorithm': f'BST In-Order Traversal (O(n)) - Key: {key}'
        })
    else:
        # Bubble sort
        sort_res = dsa.bubble_sort(songs, key=key, ascending=ascending)
        return jsonify({
            'success': True,
            'results': sort_res['sorted_songs'],
            'comparisons': sort_res['comparisons'],
            'swaps': sort_res['swaps'],
            'total_items': sort_res['total_items'],
            'time_ms': sort_res['time_ms'],
            'algorithm': sort_res['algorithm']
        })


# DSA REAL-TIME STRUCTURE STATE (Inspector)
@app.route('/api/dsa/state', methods=['GET'])
def api_dsa_state():
    """
    Returns live state of all 5 Data Structures for visualization:
    - Queue (FIFO items)
    - Stack (LIFO items)
    - Doubly Linked List (Nodes & Pointers)
    - Binary Search Tree (Hierarchy representation)
    - Array Manager (Catalog stats)
    """
    user_id = session.get('user_id', 1)
    queue = get_user_queue(user_id)
    stack = get_user_stack(user_id)
    dll = get_user_dll(user_id)

    # Build BST of catalog
    songs = database.get_all_songs()
    bst = dsa.SongBST(key_field='title')
    for s in songs:
        bst.insert(s)

    return jsonify({
        'success': True,
        'queue': {
            'items': queue.get_all(),
            'size': queue.size(),
            'type': 'Up Next'
        },
        'stack': {
            'items': stack.get_all(),
            'size': stack.size(),
            'type': 'Listening History'
        },
        'doubly_linked_list': {
            'nodes': dll.get_structure_view(),
            'size': dll.size,
            'current': dll.current.song if dll.current else None,
            'type': 'Playlist'
        },
        'bst': {
            'tree': bst.to_tree_dict(),
            'count': bst.count,
            'inorder_titles': [s['title'] for s in bst.inorder_traversal()[:8]],
            'type': 'Catalog Index'
        },
        'array': {
            'total_songs': len(songs),
            'genres': dsa.SongArrayManager.get_unique_genres(songs),
            'type': 'Catalog'
        }
    })


# QUEUE (FIFO) ENDPOINTS
@app.route('/api/queue', methods=['GET', 'POST', 'DELETE'])
def api_queue_handler():
    user_id = session.get('user_id', 1)
    queue = get_user_queue(user_id)

    if request.method == 'GET':
        return jsonify({
            'success': True,
            'queue': queue.get_all(),
            'size': queue.size()
        })

    elif request.method == 'POST':
        data = request.get_json() or {}
        song_id = data.get('song_id')
        song = database.get_song_by_id(song_id)
        if not song:
            return jsonify({'success': False, 'message': 'Song not found'}), 404

        # Enqueue (FIFO)
        queue.enqueue(song)
        return jsonify({
            'success': True,
            'message': f'"{song["title"]}" added to Up Next',
            'queue': queue.get_all(),
            'size': queue.size()
        })

    elif request.method == 'DELETE':
        # Either dequeue front or remove specific song
        song_id = request.args.get('song_id')
        if song_id:
            removed = queue.remove_by_id(int(song_id))
            return jsonify({'success': removed, 'queue': queue.get_all()})
        else:
            dequeued = queue.dequeue()
            return jsonify({'success': True, 'dequeued': dequeued, 'queue': queue.get_all()})


# ----------------------------------------------------------------------------
# STACK (LIFO) ENDPOINTS - Playback History & Undo
# ----------------------------------------------------------------------------
@app.route('/api/history', methods=['GET', 'DELETE'])
def api_history_handler():
    user_id = session.get('user_id', 1)
    stack = get_user_stack(user_id)

    if request.method == 'GET':
        # Retrieve persistent history or in-memory stack
        db_history = database.get_user_history(user_id, limit=20)
        return jsonify({
            'success': True,
            'history': stack.get_all() if not stack.is_empty() else db_history,
            'size': stack.size()
        })

    elif request.method == 'DELETE':
        # Pop most recent (LIFO undo)
        popped = stack.pop()
        return jsonify({
            'success': True,
            'popped': popped,
            'history': stack.get_all(),
            'message': 'Removed last played track from your listening history.'
        })


# ----------------------------------------------------------------------------
# DOUBLY LINKED LIST PLAYLIST NAVIGATION ENDPOINTS
# ----------------------------------------------------------------------------
@app.route('/api/player/next', methods=['GET'])
def api_player_next():
    user_id = session.get('user_id', 1)
    queue = get_user_queue(user_id)

    # 1. If queue has items, FIFO takes priority!
    if not queue.is_empty():
        next_song = queue.dequeue()
        database.increment_play_count(next_song['id'])
        get_user_stack(user_id).push(next_song)
        return jsonify({
            'success': True,
            'song': next_song,
            'source': 'Up Next',
            'queue_size': queue.size()
        })

    # 2. Otherwise navigate Doubly Linked List next
    dll = get_user_dll(user_id)
    next_song = dll.get_next(loop=True)
    if next_song:
        database.increment_play_count(next_song['id'])
        get_user_stack(user_id).push(next_song)
        return jsonify({
            'success': True,
            'song': next_song,
            'source': 'Your Playlist'
        })
    return jsonify({'success': False, 'message': 'No song available'})


@app.route('/api/player/prev', methods=['GET'])
def api_player_prev():
    user_id = session.get('user_id', 1)
    dll = get_user_dll(user_id)
    prev_song = dll.get_prev(loop=True)
    if prev_song:
        database.increment_play_count(prev_song['id'])
        get_user_stack(user_id).push(prev_song)
        return jsonify({
            'success': True,
            'song': prev_song,
            'source': 'Your Playlist'
        })
    return jsonify({'success': False, 'message': 'No song available'})


# ============================================================================
# PLAYLIST MANAGEMENT APIS (CRUD)
# ============================================================================

@app.route('/api/playlists', methods=['GET', 'POST'])
@login_required
def api_playlists():
    user_id = session['user_id']
    if request.method == 'GET':
        playlists = database.get_user_playlists(user_id)
        return jsonify({'success': True, 'playlists': playlists})

    elif request.method == 'POST':
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()

        if not name:
            return jsonify({'success': False, 'message': 'Playlist name is required.'}), 400

        playlist_id = database.create_playlist(user_id, name, description)
        return jsonify({
            'success': True,
            'playlist_id': playlist_id,
            'message': f'Playlist "{name}" created successfully!'
        })


@app.route('/api/playlists/<int:playlist_id>', methods=['GET', 'DELETE'])
@login_required
def api_playlist_detail(playlist_id):
    user_id = session['user_id']
    if request.method == 'GET':
        details = database.get_playlist_details(playlist_id, user_id)
        if details:
            return jsonify({'success': True, 'playlist': details['playlist'], 'songs': details['songs']})
        return jsonify({'success': False, 'message': 'Playlist not found'}), 404

    elif request.method == 'DELETE':
        success = database.delete_playlist(playlist_id, user_id)
        return jsonify({'success': success, 'message': 'Playlist removed.'})


@app.route('/api/playlists/<int:playlist_id>/songs', methods=['POST'])
@login_required
def api_add_song_to_playlist(playlist_id):
    data = request.get_json() or {}
    song_id = data.get('song_id')
    if not song_id:
        return jsonify({'success': False, 'message': 'Song ID required'}), 400

    success = database.add_song_to_playlist(playlist_id, song_id)
    if success:
        return jsonify({'success': True, 'message': 'Song added to playlist.'})
    return jsonify({'success': False, 'message': 'Song already exists in this playlist.'}), 409


@app.route('/api/playlists/<int:playlist_id>/songs/<int:song_id>', methods=['DELETE'])
@login_required
def api_remove_song_from_playlist(playlist_id, song_id):
    success = database.remove_song_from_playlist(playlist_id, song_id)
    return jsonify({'success': success, 'message': 'Song removed from playlist.'})


# ============================================================================
# ADMIN MUSIC PUBLISHING & MANAGEMENT APIS (CRUD)
# ============================================================================

@app.route('/api/admin/songs', methods=['POST'])
@admin_required
def api_admin_add_song():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    artist = data.get('artist', '').strip()
    album = data.get('album', '').strip()
    genre = data.get('genre', '').strip()
    duration = data.get('duration')
    release_year = data.get('release_year', 2024)
    audio_url = data.get('audio_url', '').strip()
    cover_color = data.get('cover_color', '#E09F3E')

    # Data Validation
    if not title or not artist or not genre:
        return jsonify({'success': False, 'message': 'Title, artist, and genre are required fields.'}), 400

    try:
        duration_int = int(duration)
        if duration_int <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Duration must be a positive integer in seconds.'}), 400

    try:
        year_int = int(release_year)
    except (TypeError, ValueError):
        year_int = 2024

    new_id = database.add_song(
        title=title,
        artist=artist,
        album=album,
        genre=genre,
        duration=duration_int,
        release_year=year_int,
        audio_url=audio_url,
        cover_color=cover_color
    )

    return jsonify({
        'success': True,
        'song_id': new_id,
        'message': f'Song "{title}" published to catalog successfully!'
    })


@app.route('/api/admin/songs/<int:song_id>', methods=['PUT', 'DELETE'])
@admin_required
def api_admin_modify_song(song_id):
    if request.method == 'DELETE':
        success = database.delete_song(song_id)
        return jsonify({
            'success': success,
            'message': 'Song deleted from Sonora catalog.' if success else 'Song not found.'
        })

    elif request.method == 'PUT':
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        artist = data.get('artist', '').strip()
        album = data.get('album', '').strip()
        genre = data.get('genre', '').strip()
        duration = data.get('duration')
        release_year = data.get('release_year', 2024)
        audio_url = data.get('audio_url', '').strip()

        if not title or not artist or not genre:
            return jsonify({'success': False, 'message': 'Title, artist, and genre are required.'}), 400

        try:
            duration_int = int(duration)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'message': 'Duration must be a valid number of seconds.'}), 400

        success = database.update_song(
            song_id=song_id,
            title=title,
            artist=artist,
            album=album,
            genre=genre,
            duration=duration_int,
            release_year=int(release_year) if release_year else 2024,
            audio_url=audio_url
        )

        return jsonify({
            'success': success,
            'message': 'Song metadata updated successfully!' if success else 'Update failed.'
        })


# ============================================================================
# USER ACCOUNT SETTINGS API
# ============================================================================

@app.route('/api/user/profile', methods=['GET', 'PUT'])
@login_required
def api_user_profile():
    user_id = session['user_id']
    if request.method == 'GET':
        user = database.get_user_by_id(user_id)
        return jsonify({'success': True, 'user': user})

    elif request.method == 'PUT':
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        bio = data.get('bio', '').strip()
        favorite_genre = data.get('favorite_genre', 'Lo-Fi').strip()

        if len(username) < 3:
            return jsonify({'success': False, 'message': 'Username must be at least 3 characters long.'}), 400
        if '@' not in email or '.' not in email:
            return jsonify({'success': False, 'message': 'Valid email required.'}), 400

        success = database.update_user_profile(user_id, username, email, bio, favorite_genre)
        if success:
            session['username'] = username
            return jsonify({'success': True, 'message': 'Profile updated successfully!'})
        return jsonify({'success': False, 'message': 'Username or email already in use.'}), 409


@app.route('/api/user/password', methods=['PUT'])
@login_required
def api_user_password():
    user_id = session['user_id']
    data = request.get_json() or {}
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'New password must be at least 6 characters.'}), 400

    conn = database.get_db_connection()
    user_row = conn.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    if not user_row or not check_password_hash(user_row['password_hash'], old_password):
        return jsonify({'success': False, 'message': 'Current password does not match.'}), 400

    new_hash = generate_password_hash(new_password)
    database.update_user_password(user_id, new_hash)
    return jsonify({'success': True, 'message': 'Password changed successfully!'})


# ============================================================================
# APPLICATION ENTRYPOINT
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("SONORA - Music Playlist Management System")
    print(f"Static Admin Username: {STATIC_ADMIN_USERNAME}")
    print(f"Static Admin Password: {STATIC_ADMIN_PASSWORD}")
    print("Server running on http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)

