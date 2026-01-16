import time
from collections import defaultdict
from threading import Lock
from src.utils.logger import logger

class RateLimiter:
    """Simple rate limiter to prevent too many requests"""
    
    def __init__(self, max_calls: int = 10, period: int = 60):
        self.max_calls = max_calls
        self.period = period
        self.calls = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, key: str = 'default') -> bool:
        """Check if a call is allowed"""
        with self.lock:
            now = time.time()
            # Remove old calls outside the period
            self.calls[key] = [
                call_time for call_time in self.calls[key]
                if now - call_time < self.period
            ]
            
            if len(self.calls[key]) >= self.max_calls:
                logger.warning(f'Rate limit exceeded for {key}')
                return False
            
            self.calls[key].append(now)
            return True
    
    def wait_if_needed(self, key: str = 'default'):
        """Wait if rate limit is exceeded"""
        if not self.is_allowed(key):
            oldest_call = min(self.calls[key])
            wait_time = self.period - (time.time() - oldest_call) + 1
            if wait_time > 0:
                logger.info(f'Rate limit reached, waiting {wait_time:.1f}s')
                time.sleep(wait_time)
                return self.is_allowed(key)
        return True
