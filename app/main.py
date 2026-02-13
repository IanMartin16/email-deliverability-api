from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from .config import get_settings
from .database import init_db
from .routers import email_router

settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    🚀 Email Deliverability Checker API
    
    Validate email addresses with comprehensive checks:
    - ✅ Syntax validation
    - ✅ MX record verification  
    - ✅ Disposable email detection
    - ✅ SMTP mailbox verification
    - 📊 Deliverability scoring (0-100)
    
    Perfect for:
    - User registration validation
    - Email list cleaning
    - Marketing campaign prep
    - Fraud prevention
    
    ## Authentication
    Available on RapidAPI with tiered pricing:
    - **Free**: 100 validations/month
    - **Basic ($19)**: 5,000 validations/month
    - **Pro ($49)**: 50,000 validations/month
    
    ## Rate Limits
    Limits are enforced by RapidAPI based on your subscription tier.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup"""
    init_db()
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} started successfully")
    print(f"📚 Documentation available at: /docs")


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "online",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "endpoints": {
            "validate_single": f"{settings.API_PREFIX}/email/validate",
            "validate_batch": f"{settings.API_PREFIX}/email/validate/batch",
            "stats": f"{settings.API_PREFIX}/email/stats"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected",
        "smtp_check_enabled": settings.SMTP_CHECK_ENABLED
    }


# Include routers
app.include_router(email_router, prefix=settings.API_PREFIX)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": str(request.url)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
