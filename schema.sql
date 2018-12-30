-- 配置MySQL连接为utf-8
SET NAMES 'utf8';
SET CHARSET 'utf8';

-- 创建数据库
CREATE DATABASE IF NOT EXISTS forum DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
USE forum;
-- 创建管理员
CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';
#GRANT ALL PRIVILEGES ON * . * TO 'newuser'@'localhost';
GRANT INSERT, SELECT, UPDATE, DELETE ON forum.users TO 'newuser'@'localhost';
GRANT INSERT, SELECT, UPDATE, DELETE ON forum.posts TO 'newuser'@'localhost';
GRANT INSERT, SELECT, UPDATE, DELETE ON forum.comments TO 'newuser'@'localhost';
FLUSH PRIVILEGES;

-- 创建表users 
CREATE TABLE IF NOT EXISTS users
(
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL, # 不能改的账号
    nickname VARCHAR(20), #
    birthday VARCHAR(30),
    gender VARCHAR(20),
    age INT UNSIGNED,
    email VARCHAR(100) NOT NULL,
    degree VARCHAR(20),
    password TEXT NOT NULL,
    picture TEXT NOT NULL,
    description TEXT,
    time TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY(id),
    UNIQUE KEY(email),
    UNIQUE KEY(name)
);

-- 创建表posts
CREATE TABLE IF NOT EXISTS posts
(
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    part VARCHAR(20),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    time TIMESTAMP DEFAULT NOW(),
    click_count INT UNSIGNED,
    reply_count INT UNSIGNED,
    user_id INT UNSIGNED,
    PRIMARY KEY(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- 创建表comments
CREATE TABLE IF NOT EXISTS comments
(
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    content TEXT NOT NULL,
    time TIMESTAMP DEFAULT NOW(),
    user_id INT UNSIGNED,
    title INT UNSIGNED,#回复还需要标题？
    like_count INT UNSIGNED,
    parent_id INT UNSIGNED,
    quote_id INT UNSIGNED,
    layer INT UNSIGNED,
    PRIMARY KEY(id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(parent_id) REFERENCES posts(id),
    FOREIGN KEY(quote_id) REFERENCES comments(id)
);

-- 设置时区为北京时间
-- 1.以下命令仅在当前会话期间有效
/*SET time_zone = '+8:00';*/
-- 2.以下命令则全局有效
SET GLOBAL time_zone = '+8:00';
