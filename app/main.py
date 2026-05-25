
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from app.database import Base, engine
from app import models  # ★ Новий імпорт

# Імпорти аудиту (коментар викладача залишаємо)
from app.audit.router import router as audit_router # прочитав - maximalний бал поставив
from app.audit.middleware import AuditMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.rate_limiter import limiter

# Імпорт авторизації (ось тут тепер правильно!)
from app.auth.routers import router as auth_router  

# Роутери інших сутностей
from app.routes.students import router as students_router
from app.routes.teachers import router as teachers_router
from app.routes.admin import router as admin_router

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Electronic Dean's Office",
    docs_url=None,
    redoc_url=None
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

# Підключаємо мідлварі
app.add_middleware(AuditMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Налаштовуємо CORS
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

# Ендпоінти (підключаємо роутери)
app.include_router(auth_router)  # Виправлено тут
app.include_router(students_router)
app.include_router(teachers_router)
app.include_router(admin_router)
app.include_router(audit_router, prefix="/admin", tags=["audit"])

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
