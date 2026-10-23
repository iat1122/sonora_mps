"""
Sonora - Data Structures and Algorithms (DSA) Engine
=====================================================
Contains pure, clean, and highly educational implementations of:

DATA STRUCTURES:
1. DoublyLinkedList: Playback sequence (O(1) next/prev navigation & reordering)
2. MusicQueue: Playback queue (FIFO - First In, First Out)
3. PlaybackStack: Playback history & undo operations (LIFO - Last In, First Out)
4. SongBST: Binary Search Tree for catalog indexing and in-order alphabetical retrieval
5. SongArrayManager: Array/List operations with bounds checking & filtering

ALGORITHMS:
1. Linear Search: Unsorted search with comparison counters
2. Binary Search: O(log n) divide-and-conquer on sorted lists
3. Bubble Sort: O(n^2) adjacent pairwise comparison and swap
4. Selection Sort: O(n^2) minimum element selection and swap
5. BST In-Order Traversal & Search: Recursive tree search and sorted traversal
"""

from typing import List, Dict, Any, Optional
import time


# ============================================================================
# 1. DATA STRUCTURE: DOUBLY LINKED LIST
# Used for: Sequential Playlist Navigation (Next Song, Previous Song, Loop)
# ============================================================================

class SongNode:
    """Node representing an individual track in a Doubly Linked List."""
    def __init__(self, song: Dict[str, Any]):
        self.song = song
        self.prev: Optional['SongNode'] = None
        self.next: Optional['SongNode'] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'song': self.song,
            'has_prev': self.prev is not None,
            'prev_id': self.prev.song['id'] if self.prev else None,
            'has_next': self.next is not None,
            'next_id': self.next.song['id'] if self.next else None
        }


class DoublyLinkedList:
    """
    Doubly Linked List implementation for active playlist navigation.
    Allows O(1) moving to the next track and previous track.
    """
    def __init__(self):
        self.head: Optional[SongNode] = None
        self.tail: Optional[SongNode] = None
        self.current: Optional[SongNode] = None
        self.size: int = 0

    def append(self, song: Dict[str, Any]) -> SongNode:
        """Add a song node to the end of the linked list."""
        new_node = SongNode(song)
        if not self.head:
            self.head = new_node
            self.tail = new_node
            self.current = new_node
        else:
            assert self.tail is not None
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self.size += 1
        return new_node

    def insert_at(self, index: int, song: Dict[str, Any]) -> bool:
        """Insert a song at a specific index."""
        if index < 0 or index > self.size:
            return False

        if index == self.size:
            self.append(song)
            return True

        new_node = SongNode(song)
        if index == 0:
            new_node.next = self.head
            if self.head:
                self.head.prev = new_node
            self.head = new_node
            if not self.tail:
                self.tail = new_node
            self.size += 1
            return True

        curr = self.head
        for _ in range(index):
            curr = curr.next

        new_node.prev = curr.prev
        new_node.next = curr
        if curr.prev:
            curr.prev.next = new_node
        curr.prev = new_node
        self.size += 1
        return True

    def remove_by_id(self, song_id: int) -> Optional[Dict[str, Any]]:
        """Remove a song from the linked list by song ID."""
        curr = self.head
        while curr:
            if curr.song.get('id') == song_id:
                if curr.prev:
                    curr.prev.next = curr.next
                else:
                    self.head = curr.next

                if curr.next:
                    curr.next.prev = curr.prev
                else:
                    self.tail = curr.prev

                if self.current == curr:
                    self.current = curr.next if curr.next else curr.prev

                self.size -= 1
                return curr.song
            curr = curr.next
        return None

    def set_current_by_id(self, song_id: int) -> Optional[Dict[str, Any]]:
        """Set the currently playing song node by song ID."""
        curr = self.head
        while curr:
            if curr.song.get('id') == song_id:
                self.current = curr
                return curr.song
            curr = curr.next
        return None

    def get_next(self, loop: bool = True) -> Optional[Dict[str, Any]]:
        """Move to the next song node in O(1) time."""
        if not self.current:
            self.current = self.head
            return self.current.song if self.current else None

        if self.current.next:
            self.current = self.current.next
            return self.current.song
        elif loop and self.head:
            self.current = self.head
            return self.current.song
        return None

    def get_prev(self, loop: bool = True) -> Optional[Dict[str, Any]]:
        """Move to the previous song node in O(1) time."""
        if not self.current:
            self.current = self.tail
            return self.current.song if self.current else None

        if self.current.prev:
            self.current = self.current.prev
            return self.current.song
        elif loop and self.tail:
            self.current = self.tail
            return self.current.song
        return None

    def to_list(self) -> List[Dict[str, Any]]:
        """Convert linked list to Python list for serialization."""
        result = []
        curr = self.head
        while curr:
            result.append(curr.song)
            curr = curr.next
        return result

    def get_structure_view(self) -> List[Dict[str, Any]]:
        """Returns visual representation of nodes and pointers for UI display."""
        nodes = []
        curr = self.head
        idx = 0
        while curr:
            nodes.append({
                'index': idx,
                'id': curr.song.get('id'),
                'title': curr.song.get('title'),
                'artist': curr.song.get('artist'),
                'is_current': (curr == self.current),
                'has_prev': curr.prev is not None,
                'has_next': curr.next is not None,
                'prev_title': curr.prev.song.get('title') if curr.prev else None,
                'next_title': curr.next.song.get('title') if curr.next else None
            })
            curr = curr.next
            idx += 1
        return nodes

    def clear(self):
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0


# ============================================================================
# 2. DATA STRUCTURE: QUEUE (FIFO)
# Used for: "Up Next" Play Queue
# ============================================================================

class MusicQueue:
    """
    Queue (First-In, First-Out) implementation for the "Up Next" music queue.
    Songs enqueued first are played first.
    """
    def __init__(self):
        self.items: List[Dict[str, Any]] = []

    def enqueue(self, song: Dict[str, Any]) -> None:
        """Add song to the end of the queue."""
        self.items.append(song)

    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Remove and return the front song from the queue (FIFO)."""
        if not self.is_empty():
            return self.items.pop(0)
        return None

    def peek(self) -> Optional[Dict[str, Any]]:
        """Inspect the front song without removing it."""
        if not self.is_empty():
            return self.items[0]
        return None

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def size(self) -> int:
        return len(self.items)

    def clear(self) -> None:
        self.items.clear()

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self.items)

    def remove_by_id(self, song_id: int) -> bool:
        for i, item in enumerate(self.items):
            if item.get('id') == song_id:
                self.items.pop(i)
                return True
        return False


# ============================================================================
# 3. DATA STRUCTURE: STACK (LIFO)
# Used for: Playback History and Undo Deleted Songs
# ============================================================================

class PlaybackStack:
    """
    Stack (Last-In, First-Out) implementation for Playback History and Undo actions.
    The most recently played or modified item sits on top.
    """
    def __init__(self, max_size: int = 50):
        self.items: List[Dict[str, Any]] = []
        self.max_size = max_size

    def push(self, item: Dict[str, Any]) -> None:
        """Push a song onto the top of the history stack."""
        self.items.append(item)
        if len(self.items) > self.max_size:
            self.items.pop(0)  # Maintain bounded history

    def pop(self) -> Optional[Dict[str, Any]]:
        """Pop and return the top item from the stack (LIFO)."""
        if not self.is_empty():
            return self.items.pop()
        return None

    def peek(self) -> Optional[Dict[str, Any]]:
        """Inspect top item without removing it."""
        if not self.is_empty():
            return self.items[-1]
        return None

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def size(self) -> int:
        return len(self.items)

    def clear(self) -> None:
        self.items.clear()

    def get_all(self) -> List[Dict[str, Any]]:
        """Return history from most recent to oldest."""
        return list(reversed(self.items))


# ============================================================================
# 4. DATA STRUCTURE: BINARY SEARCH TREE (BST)
# Used for: Fast catalog search by song title and In-Order alphabetical traversal
# ============================================================================

class BSTNode:
    """Node in a Binary Search Tree holding a song."""
    def __init__(self, song: Dict[str, Any], key_field: str = 'title'):
        self.song = song
        self.key_field = key_field
        self.key: str = str(song.get(key_field, '')).strip().lower()
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None


class SongBST:
    """
    Binary Search Tree for indexing songs by Title or Artist.
    Provides O(log n) average search and In-Order sorted retrieval.
    """
    def __init__(self, key_field: str = 'title'):
        self.root: Optional[BSTNode] = None
        self.key_field = key_field
        self.count: int = 0

    def insert(self, song: Dict[str, Any]) -> None:
        """Insert a song into the BST."""
        new_node = BSTNode(song, self.key_field)
        if not self.root:
            self.root = new_node
            self.count += 1
            return

        curr = self.root
        while True:
            if new_node.key < curr.key:
                if curr.left is None:
                    curr.left = new_node
                    self.count += 1
                    break
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = new_node
                    self.count += 1
                    break
                curr = curr.right

    def search(self, target_key: str) -> Dict[str, Any]:
        """
        Search for a song by key. Returns match and algorithm metrics.
        """
        normalized_target = target_key.strip().lower()
        comparisons = 0
        curr = self.root
        start_time = time.perf_counter()

        while curr:
            comparisons += 1
            if curr.key == normalized_target:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                return {
                    'found': True,
                    'song': curr.song,
                    'comparisons': comparisons,
                    'time_ms': round(elapsed_ms, 4)
                }
            elif normalized_target < curr.key:
                curr = curr.left
            else:
                curr = curr.right

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return {
            'found': False,
            'song': None,
            'comparisons': comparisons,
            'time_ms': round(elapsed_ms, 4)
        }

    def inorder_traversal(self) -> List[Dict[str, Any]]:
        """
        In-Order Traversal (Left, Root, Right).
        Mathematically yields songs sorted alphabetically by key.
        """
        result = []
        def _inorder(node: Optional[BSTNode]):
            if node:
                _inorder(node.left)
                result.append(node.song)
                _inorder(node.right)
        _inorder(self.root)
        return result

    def preorder_traversal(self) -> List[Dict[str, Any]]:
        """Pre-Order Traversal (Root, Left, Right)."""
        result = []
        def _preorder(node: Optional[BSTNode]):
            if node:
                result.append(node.song)
                _preorder(node.left)
                _preorder(node.right)
        _preorder(self.root)
        return result

    def postorder_traversal(self) -> List[Dict[str, Any]]:
        """Post-Order Traversal (Left, Right, Root)."""
        result = []
        def _postorder(node: Optional[BSTNode]):
            if node:
                _postorder(node.left)
                _postorder(node.right)
                result.append(node.song)
        _postorder(self.root)
        return result

    def to_tree_dict(self) -> Optional[Dict[str, Any]]:
        """Serialize tree into nested dict for visual graph rendering."""
        def _serialize(node: Optional[BSTNode]) -> Optional[Dict[str, Any]]:
            if not node:
                return None
            return {
                'title': node.song.get('title'),
                'artist': node.song.get('artist'),
                'key': node.key,
                'id': node.song.get('id'),
                'left': _serialize(node.left),
                'right': _serialize(node.right)
            }
        return _serialize(self.root)


# ============================================================================
# 5. DATA STRUCTURE: ARRAY / LIST MANAGER
# Used for: Managing contiguous collections with bounds checking & filtering
# ============================================================================

class SongArrayManager:
    """Manages raw Python arrays/lists of songs with indexed utility operations."""
    @staticmethod
    def filter_by_genre(songs: List[Dict[str, Any]], genre: str) -> List[Dict[str, Any]]:
        if not genre or genre.lower() == 'all':
            return list(songs)
        return [s for s in songs if s.get('genre', '').lower() == genre.lower()]

    @staticmethod
    def get_unique_genres(songs: List[Dict[str, Any]]) -> List[str]:
        genres = set()
        for s in songs:
            g = s.get('genre')
            if g:
                genres.add(g)
        return sorted(list(genres))


# ============================================================================
# ALGORITHMS IMPLEMENTATION
# ============================================================================

# ----------------------------------------------------------------------------
# Algorithm 1: Linear Search
# ----------------------------------------------------------------------------
def linear_search(songs: List[Dict[str, Any]], query: str, field: str = 'all') -> Dict[str, Any]:
    """
    Linear Search: O(n) sequential scan.
    Returns matched songs along with comparison counts and execution time.
    """
    start_time = time.perf_counter()
    query_clean = query.strip().lower()
    matches = []
    comparisons = 0

    for song in songs:
        comparisons += 1
        matched = False
        if field == 'title':
            matched = query_clean in str(song.get('title', '')).lower()
        elif field == 'artist':
            matched = query_clean in str(song.get('artist', '')).lower()
        elif field == 'genre':
            matched = query_clean in str(song.get('genre', '')).lower()
        else:
            # Search all fields
            title_match = query_clean in str(song.get('title', '')).lower()
            artist_match = query_clean in str(song.get('artist', '')).lower()
            genre_match = query_clean in str(song.get('genre', '')).lower()
            matched = title_match or artist_match or genre_match

        if matched:
            matches.append(song)

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return {
        'results': matches,
        'comparisons': comparisons,
        'total_items': len(songs),
        'time_ms': round(elapsed_ms, 4),
        'algorithm': 'Linear Search (O(n))'
    }


# ----------------------------------------------------------------------------
# Algorithm 2: Binary Search
# ----------------------------------------------------------------------------
def binary_search(sorted_songs: List[Dict[str, Any]], target_title: str) -> Dict[str, Any]:
    """
    Binary Search: O(log n) divide and conquer on an array sorted by title.
    Requires list sorted by title beforehand.
    """
    start_time = time.perf_counter()
    target_clean = target_title.strip().lower()
    low = 0
    high = len(sorted_songs) - 1
    comparisons = 0
    found_idx = -1

    while low <= high:
        comparisons += 1
        mid = (low + high) // 2
        mid_title = str(sorted_songs[mid].get('title', '')).strip().lower()

        if mid_title == target_clean:
            found_idx = mid
            break
        elif mid_title < target_clean:
            low = mid + 1
        else:
            high = mid - 1

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return {
        'found': found_idx != -1,
        'index': found_idx,
        'song': sorted_songs[found_idx] if found_idx != -1 else None,
        'comparisons': comparisons,
        'total_items': len(sorted_songs),
        'time_ms': round(elapsed_ms, 4),
        'algorithm': 'Binary Search (O(log n))'
    }


# ----------------------------------------------------------------------------
# Algorithm 3: Bubble Sort
# ----------------------------------------------------------------------------
def bubble_sort(songs: List[Dict[str, Any]], key: str = 'title', ascending: bool = True) -> Dict[str, Any]:
    """
    Bubble Sort: O(n^2) algorithm comparing and swapping adjacent items.
    """
    arr = [dict(s) for s in songs]
    n = len(arr)
    comparisons = 0
    swaps = 0
    start_time = time.perf_counter()

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comparisons += 1
            val_a = arr[j].get(key, '')
            val_b = arr[j + 1].get(key, '')

            # Case insensitive comparison for strings
            if isinstance(val_a, str):
                val_a = val_a.lower()
            if isinstance(val_b, str):
                val_b = val_b.lower()

            should_swap = (val_a > val_b) if ascending else (val_a < val_b)
            if should_swap:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
        if not swapped:
            break

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return {
        'sorted_songs': arr,
        'comparisons': comparisons,
        'swaps': swaps,
        'total_items': n,
        'time_ms': round(elapsed_ms, 4),
        'algorithm': f'Bubble Sort (O(n^2)) - Key: {key}'
    }


# ----------------------------------------------------------------------------
# Algorithm 4: Selection Sort
# ----------------------------------------------------------------------------
def selection_sort(songs: List[Dict[str, Any]], key: str = 'title', ascending: bool = True) -> Dict[str, Any]:
    """
    Selection Sort: O(n^2) algorithm finding minimum element and placing at front.
    """
    arr = [dict(s) for s in songs]
    n = len(arr)
    comparisons = 0
    swaps = 0
    start_time = time.perf_counter()

    for i in range(n):
        target_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            val_target = arr[target_idx].get(key, '')
            val_j = arr[j].get(key, '')

            if isinstance(val_target, str):
                val_target = val_target.lower()
            if isinstance(val_j, str):
                val_j = val_j.lower()

            if ascending:
                if val_j < val_target:
                    target_idx = j
            else:
                if val_j > val_target:
                    target_idx = j

        if target_idx != i:
            arr[i], arr[target_idx] = arr[target_idx], arr[i]
            swaps += 1

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return {
        'sorted_songs': arr,
        'comparisons': comparisons,
        'swaps': swaps,
        'total_items': n,
        'time_ms': round(elapsed_ms, 4),
        'algorithm': f'Selection Sort (O(n^2)) - Key: {key}'
    }

