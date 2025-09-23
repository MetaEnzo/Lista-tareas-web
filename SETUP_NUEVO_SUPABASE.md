# 🔧 Configuración de Nuevo Proyecto Supabase

## 📋 Pasos para crear un nuevo proyecto:

### 1. **Crear nuevo proyecto en Supabase**
1. Ve a [supabase.com](https://supabase.com)
2. Inicia sesión o crea una cuenta
3. Haz click en "New Project"
4. Completa:
   - **Name**: Mi App de Tareas
   - **Database Password**: (guarda esta contraseña)
   - **Region**: Elige la más cercana a ti
5. Haz click en "Create new project"

### 2. **Obtener las nuevas credenciales**
1. Ve a **Settings** → **API**
2. Copia:
   - **Project URL** (ej: https://nuevoprojecto.supabase.co)
   - **anon public** key (empieza con eyJ...)

### 3. **Actualizar el archivo secrets.toml**
Reemplaza las credenciales en `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://tu-nuevo-proyecto.supabase.co"
SUPABASE_KEY = "tu-nueva-clave-aqui"
```

### 4. **Configurar la base de datos**
1. Ve a **SQL Editor** en Supabase
2. Copia y pega el contenido del archivo `setup_database.sql`
3. Ejecuta el script

### 5. **Configurar autenticación**
1. Ve a **Authentication** → **Settings**
2. En **Email Auth**:
   - ✅ **Enable email confirmations**: Desactivar (para desarrollo)
   - ✅ **Enable email change confirmations**: Desactivar (para desarrollo)

## 🚨 **Si el proyecto anterior sigue activo:**

1. Ve a tu dashboard de Supabase
2. Verifica si el proyecto está pausado
3. Si está pausado, haz click en "Resume project"
4. Espera unos minutos para que se reactive

## 📞 **Soporte:**

Si necesitas ayuda:
- Documentación: [docs.supabase.com](https://docs.supabase.com)
- Discord: [discord.supabase.com](https://discord.supabase.com)
