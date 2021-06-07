DROP USER IF EXISTS 'crudautousr'@'%';
DROP DATABASE IF EXISTS `crudauto-demo`;
CREATE DATABASE IF NOT EXISTS `crudauto-demo` DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_zh_0900_as_cs;
USE `crudauto-demo`;
SET NAMES 'utf8mb4';
SET CHARACTER SET utf8mb4;
CREATE USER 'crudautousr'@'%' IDENTIFIED BY 'usrcrudauto';
GRANT all privileges ON `crudauto-demo`.* TO 'crudautousr'@'%';
flush privileges;
