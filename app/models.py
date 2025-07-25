import threading

# In-memory storage for URL mappings
# Structure: short_code -> { 'url': ..., 'clicks': ..., 'created_at': ... }
url_store = {}

# Lock for thread safety
store_lock = threading.Lock()