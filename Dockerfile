# 1. Мінімальний базовий образ
FROM python:3.12-slim AS builder

# 2. Встановлюємо залежності у віртуальне середовище
WORKDIR /app
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# 3. Фінальний образ
FROM python:3.12-slim

# 4. Створюємо non-root користувача
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# 5. Копіюємо віртуальне середовище від builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 6. Копіюємо код додатку
COPY ./app ./app
COPY ./scripts ./scripts
COPY ./alembic ./alembic
COPY alembic.ini .
COPY Dockerfile .
COPY .gitignore .

# 7. Створюємо директорію для даних з правами appuser
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# 8. Перемикаємося на non-root користувача
USER appuser

# 9. Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

# 10. Запуск додатку
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
