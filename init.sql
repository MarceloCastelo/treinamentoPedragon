-- Criação do banco de dados (caso não exista)
CREATE DATABASE IF NOT EXISTS treinamento_adtsa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE treinamento_adtsa;

-- Tabela de usuários (dados adicionais além do LDAP)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    department VARCHAR(100),
    position VARCHAR(100),
    empresa VARCHAR(100),
    marca VARCHAR(100),
    unidade VARCHAR(100),
    setor VARCHAR(100),
    cargo VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de progresso de vídeos
CREATE TABLE IF NOT EXISTS video_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    video_name VARCHAR(255) NOT NULL,
    current_time_seconds DECIMAL(10,2) DEFAULT 0,
    duration_seconds DECIMAL(10,2) DEFAULT 0,
    last_watched DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_video (username, topic, video_name),
    INDEX idx_username (username),
    INDEX idx_topic (topic),
    INDEX idx_last_watched (last_watched),
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de resultados de provas
CREATE TABLE IF NOT EXISTS exam_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    total_questions INT NOT NULL,
    correct_answers INT NOT NULL,
    exam_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    time_taken INT DEFAULT 0 COMMENT 'Tempo em segundos',
    answers JSON COMMENT 'Respostas do usuário em formato JSON',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_topic (topic),
    INDEX idx_exam_date (exam_date),
    INDEX idx_score (score),
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela para auditoria/logs (opcional, mas útil)
CREATE TABLE IF NOT EXISTS audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    action VARCHAR(50) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- View para estatísticas de progresso por usuário
CREATE OR REPLACE VIEW user_progress_stats AS
SELECT 
    username,
    topic,
    COUNT(*) as total_videos,
    SUM(CASE WHEN current_time_seconds >= duration_seconds * 0.9 THEN 1 ELSE 0 END) as completed_videos,
    ROUND(SUM(CASE WHEN current_time_seconds >= duration_seconds * 0.9 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as completion_percentage,
    MAX(last_watched) as last_activity
FROM video_progress
WHERE duration_seconds > 0
GROUP BY username, topic;

-- View para histórico de provas
CREATE OR REPLACE VIEW exam_history AS
SELECT 
    er.username,
    er.topic,
    er.score,
    er.correct_answers,
    er.total_questions,
    er.exam_date,
    er.time_taken,
    RANK() OVER (PARTITION BY er.username, er.topic ORDER BY er.score DESC, er.exam_date DESC) as attempt_rank
FROM exam_results er;
