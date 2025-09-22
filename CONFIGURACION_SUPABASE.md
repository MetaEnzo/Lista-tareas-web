# 🔧 Configuración de Supabase para la App de Tareas

## 📋 Pasos para configurar Supabase

### 1. **Acceder a tu proyecto Supabase**
- Ve a [supabase.com](https://supabase.com)
- Inicia sesión en tu cuenta
- Selecciona tu proyecto: `ydyxvjgntouxnxoktbuy`

### 2. **Configurar Autenticación**
- Ve a **Authentication** → **Settings**
- En **Auth Providers**, asegúrate que **Email** esté habilitado
- En **Email Auth**, configura:
  - ✅ **Enable email confirmations**: Desactivar (para desarrollo)
  - ✅ **Enable email change confirmations**: Desactivar (para desarrollo)

### 3. **Crear las tablas de base de datos**
- Ve a **SQL Editor**
- Copia y pega el contenido del archivo `setup_database.sql`
- Ejecuta el script completo

### 4. **Verificar configuración**
- Ve a **Table Editor**
- Deberías ver las tablas: `profiles` y `tareas`
- Ve a **Authentication** → **Users** para ver usuarios registrados

### 5. **Configurar políticas de seguridad (ya incluidas en el script)**
- Las políticas RLS (Row Level Security) ya están configuradas
- Los usuarios solo pueden ver/editar sus propios datos

## 🚨 **Problemas Comunes y Soluciones**

### **Error: "Table doesn't exist"**
- **Solución**: Ejecuta el script `setup_database.sql` en Supabase

### **Error: "Authentication failed"**
- **Solución**: Verifica que las credenciales en `.streamlit/secrets.toml` sean correctas

### **Error: "Email already registered"**
- **Solución**: El email ya existe, intenta con otro email o inicia sesión

### **Error: "Invalid email"**
- **Solución**: Usa un formato de email válido (ej: usuario@dominio.com)

### **Error: "Password too weak"**
- **Solución**: Usa una contraseña de al menos 6 caracteres

## 🔍 **Verificar que todo funciona**

1. **Ejecuta la app**:
   ```bash
   streamlit run app_web.py
   ```

2. **Prueba la conexión**:
   - Haz clic en "🔧 Verificar Conexión"
   - Debería mostrar "✅ Conexión a Supabase exitosa"

3. **Prueba el registro**:
   - Ve a la pestaña "📝 Crear Cuenta"
   - Completa el formulario
   - Debería mostrar "✅ Registro exitoso!"

4. **Prueba el login**:
   - Ve a la pestaña "🔑 Iniciar Sesión"
   - Usa las credenciales que acabas de crear
   - Debería iniciar sesión correctamente

## 📞 **Si sigues teniendo problemas**

1. **Verifica las credenciales** en `.streamlit/secrets.toml`
2. **Revisa la consola** de Streamlit para errores
3. **Verifica en Supabase** que las tablas existan
4. **Prueba con un email diferente**

## 🔑 **Credenciales actuales**
- **URL**: `https://ydyxvjgntouxnxoktbuy.supabase.co`
- **Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (completa en secrets.toml)
