CREATE DATABASE IF NOT EXISTS friendship_db;

USE friendship_db;


-- =====================================================
-- USERS
-- =====================================================

CREATE TABLE IF NOT EXISTS users (

    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    email VARCHAR(150) NOT NULL UNIQUE,

    password VARCHAR(255) NOT NULL,

    age INT NOT NULL,

    gender VARCHAR(30),

    city VARCHAR(100),

    interests VARCHAR(500),

    bio TEXT,

    profile_photo VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- =====================================================
-- FRIEND REQUESTS
-- =====================================================

CREATE TABLE IF NOT EXISTS friend_requests (

    id INT AUTO_INCREMENT PRIMARY KEY,

    sender_id INT NOT NULL,

    receiver_id INT NOT NULL,

    status ENUM(
        'pending',
        'accepted',
        'rejected'
    ) DEFAULT 'pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (sender_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (receiver_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);


-- =====================================================
-- FRIENDSHIPS
-- =====================================================

CREATE TABLE IF NOT EXISTS friendships (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user1_id INT NOT NULL,

    user2_id INT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user1_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (user2_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    UNIQUE(user1_id, user2_id)

);


-- =====================================================
-- MESSAGES
-- =====================================================

CREATE TABLE IF NOT EXISTS messages (

    id INT AUTO_INCREMENT PRIMARY KEY,

    sender_id INT NOT NULL,

    receiver_id INT NOT NULL,

    message TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (sender_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (receiver_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);