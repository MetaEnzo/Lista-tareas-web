-- Script para crear las tablas necesarias en Supabase
-- Ejecuta este script en el SQL Editor de tu proyecto Supabase

-- 1. Crear tabla de perfiles de usuario
CREATE TABLE IF NOT EXISTS profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT NOT NULL,
    nombre TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Crear tabla de tareas
CREATE TABLE IF NOT EXISTS tareas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    texto TEXT NOT NULL,
    categoria TEXT NOT NULL,
    fecha DATE,
    urgente BOOLEAN DEFAULT FALSE,
    completada BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Habilitar Row Level Security (RLS)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE tareas ENABLE ROW LEVEL SECURITY;

-- 4. Crear políticas de seguridad para profiles
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- 5. Crear políticas de seguridad para tareas
CREATE POLICY "Users can view own tasks" ON tareas
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own tasks" ON tareas
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own tasks" ON tareas
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own tasks" ON tareas
    FOR DELETE USING (auth.uid() = user_id);

-- 6. Crear función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 7. Crear triggers para actualizar updated_at
CREATE TRIGGER update_profiles_updated_at 
    BEFORE UPDATE ON profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tareas_updated_at 
    BEFORE UPDATE ON tareas 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 8. Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_tareas_user_id ON tareas(user_id);
CREATE INDEX IF NOT EXISTS idx_tareas_fecha ON tareas(fecha);
CREATE INDEX IF NOT EXISTS idx_tareas_completada ON tareas(completada);
CREATE INDEX IF NOT EXISTS idx_tareas_categoria ON tareas(categoria);
