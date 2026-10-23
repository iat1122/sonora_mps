# Sonora - Music Playlist Management System
A full-stack, data-structures-and-algorithms-driven music playlist management system built with Python (Flask), SQLite, and a custom **Neumorphic** user interface.

---

## 🎨 Theme & Color Palette
Sonora is crafted with a soft, tactile **Neumorphism** aesthetic using the required color scheme:
- **`#540B0E`** — Deep Burgundy (Base background gradient & header tone)
- **`#9E2A2B`** — Rust / Terracotta Red (Raised surfaces, interactive buttons, accents)
- **`#E09F3E`** — Amber Ochre Gold (Glowing playback rings, active states, badges)
- **`#FFF3B0`** — Soft Vanilla Cream (Typography, icons, high-contrast labels)

---

## 🧠 Data Structures & Algorithms (DSA) Implementation

### 1. Data Structures (5 Implemented)
| Data Structure | Implementation Class | System Role | Time Complexity |
| :--- | :--- | :--- | :--- |
| **Doubly Linked List** | `dsa.DoublyLinkedList` | Sequential playlist playback; supports $O(1)$ navigation to **Previous** and **Next** songs, looping, and track reordering. | Next/Prev: $O(1)$, Insert/Delete: $O(1)$ |
| **Queue (FIFO)** | `dsa.MusicQueue` | **"Up Next" Play Queue**; tracks are enqueued at the rear and automatically dequeued at the front when the active song finishes. | Enqueue/Dequeue: $O(1)$ |
| **Stack (LIFO)** | `dsa.PlaybackStack` | **Listening History & Undo Engine**; tracks pushed to the top upon play, allowing instant "Undo Last Played" via stack pop. | Push/Pop: $O(1)$ |
| **Binary Search Tree** | `dsa.SongBST` | Catalog title indexing; enables fast logarithmic lookup and sorted retrieval. | Search/Insert: $O(\log n)$ avg |
| **Array / List** | `dsa.SongArrayManager` | Contiguous catalog storage, genre filtering, and bounds checking. | Access: $O(1)$, Filter: $O(n)$ |

### 2. Algorithms (4+ Implemented)
| Algorithm | Function | System Role | Comparisons & Complexity |
| :--- | :--- | :--- | :--- |
| **Linear Search** | `dsa.linear_search()` | Unsorted multi-field search across song Title, Artist, and Genre. | Best: $O(1)$, Worst: $O(n)$ |
| **Binary Search** | `dsa.binary_search()` | Divide-and-conquer search on sorted catalog by song title with comparison tracking. | Best: $O(1)$, Worst: $O(\log n)$ |
| **Bubble Sort** | `dsa.bubble_sort()` | Pairwise adjacent comparison and swap sorting tracks by Duration, Title, or Year. | Comparisons: $O(n^2)$, Swaps: $O(n^2)$ |
| **Selection Sort** | `dsa.selection_sort()` | Finds minimum element in unsorted prefix to sort playlists and tracks. | Comparisons: $O(n^2)$, Swaps: $O(n)$ |
| **BST In-Order Traversal** | `dsa.SongBST.inorder_traversal()` | Mathematical traversal (Left $\to$ Root $\to$ Right) producing an alphabetically sorted catalog. | Time: $O(n)$ |

*Note: The system features a live **DSA Inspector** and **Live Algorithm Metrics Panel** displaying actual comparison counts, swap counts, and execution times in milliseconds!*

---

## ⚡ Quick Start & Execution

### 1. Requirements
- Python 3.8+ (Tested on Python 3.14)
- Flask (`pip install flask werkzeug`)

### 2. Launch the Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Authentication & In-Code Static Admin Access

### 1. In-Code Static Admin Account
As requested, the administrator credentials are static and visible directly in code (`app.py`):
```python
STATIC_ADMIN_USERNAME = "admin"
STATIC_ADMIN_PASSWORD = "sonoraAdmin2024"
```

### 2. Logo Admin Access Trigger
- On the **Sign In / Auth page** and on the **Navbar**, clicking the glowing **Sonora Logo disc** opens the **Administrator Access Portal**.
- One click on **"Authorize Direct Admin Session"** immediately authenticates the session and redirects to the **Admin Dashboard**.

### 3. Pre-Seeded Accounts for Testing
- **Administrator:** `admin` / `sonoraAdmin2024`
- **Demo User:** `melodymaster` / `user123`

---

## 📁 Project Architecture & Clean Separation
Every page features strictly separated HTML, CSS, and JS files:

```
SONORA/
├── app.py                      # Flask routes, API endpoints, session security
├── database.py                 # SQLite SQL queries, schema, seeding, and CRUD
├── dsa.py                      # Pure Python DSA data structures & algorithms
├── sonora.db                   # SQLite persistent database file
├── README.md                   # Full documentation
├── templates/
│   ├── auth.html               # Sign In / Register & Logo Admin Gate
│   ├── user_dashboard.html     # Music player, catalog, playlists, DSA inspector
│   ├── admin_dashboard.html    # Admin KPIs, music publishing & deletion
│   └── settings.html           # User profile & security settings
└── static/
    ├── css/
    │   ├── neumorphism.css     # Core neumorphic theme tokens & elevation shadows
    │   ├── auth.css            # Auth layout & vinyl spinning animations
    │   ├── user_dashboard.css  # Player bar, 2-column layout, song rows
    │   ├── admin_dashboard.css # Admin data tables, KPI cards, form grids
    │   └── settings.css        # Profile cards & password forms
    └── js/
        ├── audio_synth.js      # Web Audio API real procedural music synthesizer
        ├── auth.js             # Form validation & logo click modal logic
        ├── user_dashboard.js   # DSA Search/Sort, Playlists CRUD, Inspector
        ├── player.js           # Playback engine (Doubly Linked List, Queue, Stack)
        ├── admin_dashboard.js  # Admin publishing, editing, and deleting songs
        └── settings.js         # User profile update & password change validation
```

---

## 🎵 Real Audio Experience (Procedural Web Audio Synthesizer)
Sonora contains a built-in **Web Audio API synthesizer** (`static/js/audio_synth.js`). When you hit **Play** on any track, the browser produces melodious genre-specific chord progressions (Synthwave, Lo-Fi, Jazz, Acoustic, Classical, Electronic) and drives the animated frequency wave visualizer on the player bar! You can also enter custom MP3/Audio URLs in the Admin dashboard.

