CREATE USER 'taxonomy'@'%' IDENTIFIED BY  'super_secret_password';
GRANT USAGE ON * . * TO  'taxonomy'@'%' IDENTIFIED BY  'super_secret_password' WITH MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0 ;
CREATE DATABASE IF NOT EXISTS  `taxonomy` ;
GRANT ALL PRIVILEGES ON  `taxonomy` . * TO  'taxonomy'@'%';

