import logging
import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# ==========================================
# 1. Logger Configuration
# ==========================================

# Configure a named logger instead of using print().
# This allows for better control over log levels and output formats.
logger = logging.getLogger("api_tracker")
logger.setLevel(logging.INFO)

# Create a console handler to output logs to the terminal
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)

# Disable Uvicorn's default access logger to prevent double logging
# of the same request (since we are creating our own custom log).
logging.getLogger("uvicorn.access").disabled = True


# ==========================================
# 2. Middleware Configuration Function
# ==========================================

def register_middleware(app: FastAPI):
    """
    Configures and adds all middleware (CORS, Logging, etc.) to the FastAPI application.
    
    Args:
        app (FastAPI): The application instance to attach middleware to.
    """
    # B. Custom Logging Middleware
    # ------------------------------------------
    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        """
        Intercepts every request to log execution time and status codes.
        """
        # Start timer: perf_counter is more precise than time.time() for execution duration
        start_time = time.perf_counter()

        # Pass the request to the next handler (the actual API route)
        response: Response = await call_next(request)

        # Calculate duration
        processing_time = time.perf_counter() - start_time

        # Extract client info safely (handles cases where client might be None in tests)
        host = request.client.host if request.client else "unknown"
        port = request.client.port if request.client else "0"

        # Add trusted host middleware
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1"],
        )

        # Construct a readable log message
        message = (
            f"{host}:{port} - "
            f"{request.method} - "
            f"{request.url.path} - "
            f"Status: {response.status_code} - "
            f"Completed in {processing_time:.4f}s"
        )

        

        # Output using the configured logger
        logger.info(message)

        return response
