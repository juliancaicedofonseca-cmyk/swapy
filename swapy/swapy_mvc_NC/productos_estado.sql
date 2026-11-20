USE swapy;

ALTER TABLE productos
  ADD COLUMN IF NOT EXISTS estado varchar(20) NOT NULL DEFAULT 'Activo';

UPDATE productos
SET estado = 'Activo'
WHERE estado IS NULL OR estado = '';