"""Application Settings and Configuration"""

import os
from typing import Dict, Any

def get_settings() -> Dict[str, Any]:
    """Get application settings from environment variables"""
    return {
        'GOOGLE_API_KEY': os.environ.get('GOOGLE_API_KEY'),
        'EMBEDDING_MODEL': os.environ.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2'),
        'MAX_CHUNK_SIZE': int(os.environ.get('MAX_CHUNK_SIZE', '1000')),
        'RETRIEVAL_TOP_K': int(os.environ.get('RETRIEVAL_TOP_K', '5')),
        'DEBUG_MODE': os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
    }