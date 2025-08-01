-- MySQL 초기화 스크립트
-- 기본 설정 및 권한 부여

-- 시간대 설정
SET GLOBAL time_zone = '+00:00';
SET time_zone = '+00:00';

-- SQL 모드 설정 (표준 준수)
SET GLOBAL sql_mode = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';

-- 문자셋 설정
ALTER DATABASE sql_course CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 사용자 권한 설정
GRANT ALL PRIVILEGES ON sql_course.* TO 'student'@'%';
FLUSH PRIVILEGES;

-- 로깅 설정
SET GLOBAL general_log = 'ON';
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;