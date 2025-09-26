# 🔧 Troubleshooting - Symplifika

Documentação para resolução de problemas e correções implementadas.

## 📁 Arquivos Disponíveis

### 🐛 **Correções de Bugs**
- **`API_FIXES_SUMMARY.md`** - Correções nas APIs
- **`ISSUES_FIXED.md`** - Problemas resolvidos
- **`CLEANUP_SUMMARY.md`** - Limpezas e otimizações

### 🔧 **Fixes Específicos**
- **`CATEGORY_MULTIPLE_SUBMISSION_FIX.md`** - Fix submissões múltiplas
- **`SHORTCUT_CREATION_FIX.md`** - Correções criação de atalhos
- **`SHORTCUT_EDITING_FIX.md`** - Correções edição de atalhos

## 🚨 Problemas Comuns

### **APIs 404/500**
```bash
# Verificar URLs
python manage.py show_urls | grep api
# Reiniciar servidor
python manage.py runserver
```

### **CORS Errors**
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "chrome-extension://*",
]
```

### **JWT Auth Issues**
```python
# Verificar tokens
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

### **Database Problems**
```bash
# Migrações
python manage.py showmigrations
python manage.py migrate
```

### **Chrome Extension**
```bash
# Recompilar
cd chrome_extension && npm run build
# Recarregar no chrome://extensions/
```

## 🔍 Debug Tools

### **Django**
```python
DEBUG = True  # settings.py
```

### **Logs**
```bash
tail -f logs/django.log
grep -i error logs/django.log
```

### **Health Check**
```bash
curl http://localhost:8000/health/
```

## 🚨 Emergência

### **Rollback**
```bash
git revert HEAD
python manage.py migrate app_name 0001
```

### **Restart**
```bash
pkill -f "python manage.py runserver"
python manage.py runserver
```

---

**🎯 Consulte logs primeiro, reinicie serviços, verifique documentação.**
