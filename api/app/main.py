from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import Config
from app.models.database import Base
from app.routes import groups, countries, resources, auctions

engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        db.bind.dispose()  # Close connection pool
app = FastAPI(title="EcoTech Auction API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(groups.router)
app.include_router(countries.router)
app.include_router(resources.router)
app.include_router(auctions.router)

@app.get("/")
def root():
    return {"message": "EcoTech Auction API", "version": "2.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}