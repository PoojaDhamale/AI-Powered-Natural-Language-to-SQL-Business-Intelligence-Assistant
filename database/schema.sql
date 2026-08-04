--  ===== Dimension tables =====

CREATE TABLE calendar_lookup (
    date DATE PRIMARY KEY
);

CREATE TABLE territory_lookup (
    territory_key INT PRIMARY KEY,
    region VARCHAR(100),
    country VARCHAR(100),
    continent VARCHAR(100)
);

CREATE TABLE product_category_lookup (
    product_category_key INT PRIMARY KEY,
    category_name VARCHAR(100)
);

CREATE TABLE product_subcategory_lookup (
    product_subcategory_key INT PRIMARY KEY,
    subcategory_name VARCHAR(100),
    product_category_key INT REFERENCES product_category_lookup(product_category_key)
);

CREATE TABLE product_lookup (
    product_key INT PRIMARY KEY,
    product_subcategory_key INT REFERENCES product_subcategory_lookup(product_subcategory_key),
    product_sku VARCHAR(50),
    product_name VARCHAR(200),
    model_name VARCHAR(100),
    product_description TEXT,
    product_color VARCHAR(50),
    product_size VARCHAR(20),
    product_style VARCHAR(20),
    product_cost NUMERIC(10,2),
    product_price NUMERIC(10,2)
);

CREATE TABLE customer_lookup (
    customer_key INT PRIMARY KEY,
    prefix VARCHAR(10),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    birth_date DATE,
    marital_status VARCHAR(5),
    gender VARCHAR(5),
    email_address VARCHAR(150),
    annual_income NUMERIC(12,2),
    total_children INT,
    education_level VARCHAR(50),
    occupation VARCHAR(50),
    home_owner VARCHAR(5)
);

-- ===== Fact tables =====

CREATE TABLE sales_data (
    order_date DATE,
    stock_date DATE,
    order_number VARCHAR(20),
    product_key INT REFERENCES product_lookup(product_key),
    customer_key INT REFERENCES customer_lookup(customer_key),
    territory_key INT REFERENCES territory_lookup(territory_key),
    order_line_item INT,
    order_quantity INT,
    PRIMARY KEY (order_number, order_line_item)
);

CREATE TABLE returns_data (
    return_date DATE,
    territory_key INT REFERENCES territory_lookup(territory_key),
    product_key INT REFERENCES product_lookup(product_key),
    return_quantity INT
);