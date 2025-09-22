-- Script para agregar campos de hora y zona horaria a la tabla tareas
-- Ejecuta este script en el SQL Editor de Supabase

-- Agregar columnas de hora y zona horaria
ALTER TABLE tareas 
ADD COLUMN IF NOT EXISTS hora TIME,
ADD COLUMN IF NOT EXISTS zona_horaria TEXT DEFAULT 'America/Mexico_City';

-- Crear índice para mejorar rendimiento en consultas por hora
CREATE INDEX IF NOT EXISTS idx_tareas_hora ON tareas(hora);

-- Actualizar comentarios de las columnas
COMMENT ON COLUMN tareas.hora IS 'Hora específica del día para la tarea';
COMMENT ON COLUMN tareas.zona_horaria IS 'Zona horaria de la tarea (ej: America/Mexico_City)';
