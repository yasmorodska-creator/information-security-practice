# Dockerfile — Security Hardened
 
# 1. Мінімальний базовий образ (менша поверхня атаки)
FROM python:3.12-slim AS builder
 
# 2. Встановлюємо залежності окремим шаром (кешування)
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
 
# 3. Фінальний образ
FROM python:3.12-slim
 
# 4. Створюємо non-root користувача
#	КРИТИЧНО: контейнер НЕ повинен працювати від root
RUN groupadd -r appuser && \
	useradd -r -g appuser -d /app -s /sbin/nologin appuser
 
WORKDIR /app
 
# 5. Копіюємо залежності від builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH
 
# 6. Копіюємо код додатку
COPY ./app ./app
COPY ./scripts ./scripts
COPY ./alembic ./alembic
COPY alembic.ini .
 
# 7. Створюємо директорію для даних з правами appuser
RUN mkdir -p /app/data && chown -R appuser:appuser /app
 
# 8. Перемикаємося на non-root користувача
USER appuser
 
# 9. Health Check — перевірка працездатності
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; \
  urllib.request.urlopen('http://localhost:8000/docs')" || exit 1
 
# 10. Запуск додатку
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
