from slowapi import Limiter
from slowapi.util import get_remote_address

# This single instance is imported everywhere else
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/hour"]
    # storage_uri="redis://localhost:6379"  # If distributed
)
