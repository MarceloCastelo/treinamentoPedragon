-- Script de migração para adicionar a coluna selected_courses na tabela users
-- Execute este script no banco de dados MySQL

USE treinamento_adtsa;

-- Adiciona a coluna selected_courses
ALTER TABLE users 
ADD COLUMN selected_courses JSON COMMENT 'Cursos selecionados pelo usuário em formato JSON';

-- Verifica se a coluna foi adicionada
DESCRIBE users;
