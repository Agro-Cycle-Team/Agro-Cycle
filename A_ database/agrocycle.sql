-- =====================================================
-- AGROCYCLE DATABASE
-- =====================================================

CREATE DATABASE IF NOT EXISTS agrocycle;
USE agrocycle;

-- =====================================================
-- 1️⃣ FARMERS TABLE
-- =====================================================

CREATE TABLE farmers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    land_size DECIMAL(10,2) NOT NULL,
    crop_type VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    contract_status ENUM('Pending','Accepted') DEFAULT 'Pending',
    contract_date DATE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 2️⃣ COMPANIES TABLE
-- =====================================================

CREATE TABLE companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 3️⃣ ADMIN TABLE
-- =====================================================

CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 4️⃣ FERTILIZER REQUESTS TABLE
-- =====================================================

CREATE TABLE fertilizer_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    crop_type VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    harvest_date DATE NOT NULL,
    status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (farmer_id) REFERENCES farmers(id)
    ON DELETE CASCADE
);

-- =====================================================
-- 5️⃣ FARM WASTE TABLE
-- =====================================================

CREATE TABLE farm_waste (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    waste_type VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    description TEXT,
    image VARCHAR(255),
    status ENUM('Pending','Approved','Rejected','Sold') DEFAULT 'Pending',
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (farmer_id) REFERENCES farmers(id)
    ON DELETE CASCADE
);

-- =====================================================
-- 6️⃣ WASTE PURCHASE TABLE
-- =====================================================

CREATE TABLE waste_purchases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    waste_id INT NOT NULL,
    company_id INT NOT NULL,
    quantity INT NOT NULL,
    total_cost DECIMAL(12,2) NOT NULL,
    status ENUM('Pending','Completed') DEFAULT 'Pending',
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (waste_id) REFERENCES farm_waste(id)
    ON DELETE CASCADE,

    FOREIGN KEY (company_id) REFERENCES companies(id)
    ON DELETE CASCADE
);

-- =====================================================
-- 7️⃣ INSERT DEFAULT ADMIN
-- Password should be hashed in real system
-- =====================================================

INSERT INTO admin (username, email, password)
VALUES ('admin', 'admin@agrocycle.com', 'admin123');

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX idx_farmer_id ON fertilizer_requests(farmer_id);
CREATE INDEX idx_waste_farmer ON farm_waste(farmer_id);
CREATE INDEX idx_purchase_company ON waste_purchases(company_id);

-- =====================================================
-- DATABASE SETUP COMPLETE
-- =====================================================