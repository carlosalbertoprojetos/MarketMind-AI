"""
Rate limiting com SlowAPI. Limites por IP (key_func=get_remote_address).
Use: @limiter.limit("60/minute") na rota.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
