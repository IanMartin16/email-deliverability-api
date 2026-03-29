from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.api.auth import router as auth_router
from app.core.config import settings
#from app.core.database import init_db

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## Email Deliverability Checker API
    
    Comprehensive email validation service with:
    
    * **Syntax Validation** - RFC-compliant email format checking
    * **MX Records** - Domain mail server verification
    * **Disposable Detection** - Temporary email provider identification
    * **SMTP Verification** - Mailbox existence validation (optional)
    * **Deliverability Score** - 0-100 score indicating email quality
    
    ### Rate Limits (RapidAPI)
    
    - **Free Plan**: 100 validations/month
    - **Basic Plan** ($19/mo): 5,000 validations/month
    - **Pro Plan** ($49/mo): 50,000 validations/month
    
    ### Quick Start
    
    1. Get your API key from RapidAPI
    2. Make a POST request to `/api/v1/validate`
    3. Receive comprehensive validation results
    
    ### Performance
    
    - **Standard validation**: ~100-300ms per email
    - **With SMTP check**: ~1-3s per email
    - **Bulk validation**: Optimized for batch processing
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.ALLOWED_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.API_V1_PREFIX, tags=["Email Validation"])
app.include_router(auth_router, prefix=settings.API_V1_PREFIX, tags=["Authentication"])

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print("✅ Startup completed")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler
    """
    print(f"👋 {settings.APP_NAME} shutting down...")
