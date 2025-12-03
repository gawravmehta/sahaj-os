from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.webhook_routes import router
from app.cron.scheduler import init_scheduler
from app.core.logging_config import logger

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specific origins in a production environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup event triggered.")
    init_scheduler()
    logger.info("Scheduler initialized and started.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown event triggered.")
    # You might want to gracefully stop the scheduler here if necessary
    # scheduler.shutdown() # if scheduler is a global variable
