# Gunicorn configuration optimized for Render free tier
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
backlog = 2048

# Worker processes - optimized for free tier (512MB RAM limit)
workers = 1  # Single worker to minimize memory usage
worker_class = "gthread"
threads = 2  # Multiple threads for I/O bound operations
worker_connections = 1000
max_requests = 1000  # Restart workers after handling this many requests
max_requests_jitter = 50  # Add randomness to prevent thundering herd

# Timeouts
timeout = 120  # Request timeout (Render has 60s timeout, but we set higher for processing)
keepalive = 5  # Keep-alive timeout
graceful_timeout = 30  # Graceful shutdown timeout

# Application
wsgi_app = "backend.app:app"
preload_app = True  # Preload application for memory efficiency

# Logging
loglevel = "info"
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
user = None  # Run as current user (non-root in container)
group = None
umask = 0
tmp_upload_dir = None

# Performance
enable_stdio_inheritance = False
reuse_port = False

# Process naming
proc_name = "physicslab-backend"

# Server mechanics
daemon = False
pidfile = None
worker_tmp_dir = None
chdir = "/app"

# SSL (not needed for Render as it handles SSL termination)
keyfile = None
certfile = None

# Performance tuning for limited resources
def when_ready(server):
    """Called just after the server is started."""
    server.log.info("PhysicsLab backend server is ready. Listening on %s", bind)

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker aborted (pid: %s)", worker.pid)

def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info("Worker exited (pid: %s)", worker.pid)