USE swapy;

SET @sql := IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'usuario' AND COLUMN_NAME = 'descripcion') = 0,
  'ALTER TABLE `usuario` ADD COLUMN `descripcion` text DEFAULT NULL',
  'SELECT "descripcion ya existe"'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql := IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'usuario' AND COLUMN_NAME = 'foto') = 0,
  'ALTER TABLE `usuario` ADD COLUMN `foto` varchar(255) DEFAULT NULL',
  'SELECT "foto ya existe"'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql := IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'usuario' AND COLUMN_NAME = 'categorias') = 0,
  'ALTER TABLE `usuario` ADD COLUMN `categorias` varchar(255) DEFAULT NULL',
  'SELECT "categorias ya existe"'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

ALTER TABLE `usuario`
  MODIFY COLUMN `categorias` varchar(255) DEFAULT NULL;
