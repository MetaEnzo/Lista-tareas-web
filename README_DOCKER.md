# 🐳 Docker Setup - App de Tareas

Este proyecto ahora está configurado para ejecutarse con Docker, lo que garantiza consistencia entre diferentes entornos.

## 📋 Archivos creados

- `Dockerfile` - Configuración del contenedor
- `.dockerignore` - Archivos a excluir del build
- `docker-compose.yml` - Orquestación de servicios
- `env.example` - Plantilla de variables de entorno

## 🚀 Cómo usar

### Opción 1: Con Docker Compose (Recomendado)

1. **Configurar variables de entorno:**
   ```bash
   # Copia el archivo de ejemplo
   cp env.example .env
   
   # Edita .env con tus credenciales de Supabase
   nano .env
   ```

2. **Ejecutar la aplicación:**
   ```bash
   docker-compose up
   ```

3. **Acceder a la app:**
   - Abre tu navegador en: http://localhost:8501

### Opción 2: Con Docker directamente

1. **Construir la imagen:**
   ```bash
   docker build -t tareas-app .
   ```

2. **Ejecutar el contenedor:**
   ```bash
   docker run -p 8501:8501 \
     -e SUPABASE_URL=tu_url_aqui \
     -e SUPABASE_KEY=tu_key_aqui \
     tareas-app
   ```

## 🔧 Comandos útiles

### Desarrollo
```bash
# Ejecutar en modo desarrollo (con hot reload)
docker-compose up --build

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

### Producción
```bash
# Ejecutar en segundo plano
docker-compose up -d

# Ver estado de contenedores
docker-compose ps

# Reiniciar servicios
docker-compose restart
```

### Limpieza
```bash
# Eliminar contenedores y volúmenes
docker-compose down -v

# Eliminar imagen
docker rmi tareas-app

# Limpiar todo (cuidado!)
docker system prune -a
```

## 📝 Variables de entorno

Crea un archivo `.env` con:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_clave_anonima_aqui
```

## 🎯 Beneficios de usar Docker

- ✅ **Consistencia**: Mismo entorno en desarrollo y producción
- ✅ **Portabilidad**: Funciona en cualquier sistema con Docker
- ✅ **Aislamiento**: No interfiere con otras aplicaciones
- ✅ **Escalabilidad**: Fácil de escalar horizontalmente
- ✅ **Deployment**: Un comando para desplegar

## 🐛 Solución de problemas

### Puerto ocupado
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8502:8501"  # Usar puerto 8502 en lugar de 8501
```

### Problemas de permisos
```bash
# En Linux/Mac, cambiar permisos
sudo chown -R $USER:$USER .
```

### Reconstruir imagen
```bash
# Forzar rebuild sin cache
docker-compose build --no-cache
```

## 📚 Recursos adicionales

- [Documentación de Docker](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Streamlit en Docker](https://docs.streamlit.io/deploy/docker)
