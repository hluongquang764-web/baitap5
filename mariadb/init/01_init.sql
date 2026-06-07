CREATE TABLE IF NOT EXISTS petrol_price (
    id         INT PRIMARY KEY AUTO_INCREMENT,
    fuel_type  VARCHAR(50)   NOT NULL COMMENT 'Loại xăng: RON95, RON92, DO',
    price      DECIMAL(10,0) NOT NULL COMMENT 'Giá (VNĐ/lít)',
    unit       VARCHAR(20)   DEFAULT 'VNĐ/lít',
    updated_at DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO petrol_price (fuel_type, price) VALUES
('RON95-III', 0),
('RON92-II',  0),
('DO 0.05S',  0);
