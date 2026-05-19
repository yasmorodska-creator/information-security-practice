from app.audit.middleware import AuditMiddleware
from fastapi import FastAPI
from app.database import Base, engine
from app import models  # ★ Новий імпорт
from app.routers import auth

app = FastAPI(title="Electronic Dean's Office")
app.add_middleware(AuditMiddleware)
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.rate_limiter import limiter

# Підключаємо наші захисні заголовки
app.add_middleware(SecurityHeadersMiddleware)

# Налаштовуємо CORS (зверніть увагу, я додав ваш порт 3010)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:3010", 
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
from app.routes.students import router as students_router
from app.routes.teachers import router as teachers_router
from app.routes.admin import router as admin_router

app.include_router(students_router)
app.include_router(teachers_router)
app.include_router(admin_router)
@app.get("/")
def root():
    return {"message": "Electronic Dean's Office API"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "SQLite",
        "tables": len(Base.metadata.tables)
    }