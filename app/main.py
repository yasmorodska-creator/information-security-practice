from fastapi import FastAPI
from app.database import Base, engine
from app import models  # ★ Новий імпорт
from app.routers import auth

app = FastAPI(title="Electronic Dean's Office")

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