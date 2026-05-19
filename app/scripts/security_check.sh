(scripts/security_check.sh)
#!/bin/bash
# scripts/security_check.sh
# Автоматична перевірка безпеки перед деплоєм
 
echo "=== SECURITY CHECK ==="
ERRORS=0
 
# 1. Перевірка секретів у коді
echo "1. Перевірка секретів у коді..."
if grep -rn "password\s*=" app/ --include="*.py" \
   | grep -v password_hash | grep -v "# " \
   | grep -v "Field(" | grep -v "def " | grep -v getenv; then
  echo "   ПОПЕРЕДЖЕННЯ: можливі захардкоджені паролі"
  ERRORS=$((ERRORS + 1))
else
  echo "   OK: Секрети не знайдені у коді"
fi
 
# 2. Перевірка .env у .gitignore
echo "2. Перевірка .gitignore..."
if grep -q "\.env" .gitignore 2>/dev/null; then
  echo "   OK: .env додано до .gitignore"
else
  echo "   ПОМИЛКА: .env НЕ в .gitignore!"
  ERRORS=$((ERRORS + 1))
fi
 
# 3. Перевірка Dockerfile на USER
echo "3. Перевірка Dockerfile..."
if grep -q "^USER" Dockerfile; then
  echo "   OK: Non-root user налаштований"
else
  echo "   ПОМИЛКА: Контейнер працює від root!"
  ERRORS=$((ERRORS + 1))
fi
 
# 4. Перевірка HEALTHCHECK
if grep -q "HEALTHCHECK" Dockerfile; then
  echo "   OK: HEALTHCHECK налаштований"
else
  echo "   ПОПЕРЕДЖЕННЯ: HEALTHCHECK відсутній"
fi
 
# 5. pip-audit
echo "4. Перевірка залежностей (pip-audit)..."
if command -v pip-audit &> /dev/null; then
  pip-audit -r requirements.txt --desc 2>/dev/null
  if [ $? -ne 0 ]; then
      echo "   ПОПЕРЕДЖЕННЯ: Знайдені вразливі залежності"
      ERRORS=$((ERRORS + 1))
  else
      echo "   OK: Залежності безпечні"
  fi
fi
 
# 6. Bandit
echo "5. Статичний аналіз коду (Bandit)..."
if command -v bandit &> /dev/null; then
  BANDIT_ISSUES=$(bandit -r app/ -q --severity-level high \
      2>/dev/null | grep -c "Issue")
  if [ "$BANDIT_ISSUES" -gt 0 ]; then
      echo "   ПОПЕРЕДЖЕННЯ: Bandit знайшов $BANDIT_ISSUES проблем"
      ERRORS=$((ERRORS + 1))
  else
      echo "   OK: Критичних проблем не знайдено"
  fi
fi
 
# Підсумок
echo "=========================="
if [ $ERRORS -eq 0 ]; then
  echo "SECURITY CHECK PASSED"
else
  echo "SECURITY CHECK FAILED ($ERRORS проблем)"
fi
exit $ERRORS