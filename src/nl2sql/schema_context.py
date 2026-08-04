SCHEMA_CONTEXT = """
You are working with a PostgreSQL database for a business analytics assistant.
The database models sales for a bicycle/outdoor equipment company (AdventureWorks)
across 2020-2022. Below are the tables, their columns, and how they relate.

TABLE: calendar_lookup
  date DATE PRIMARY KEY

TABLE: territory_lookup
  territory_key INT PRIMARY KEY
  region VARCHAR
  country VARCHAR
  continent VARCHAR

TABLE: product_category_lookup
  product_category_key INT PRIMARY KEY
  category_name VARCHAR

TABLE: product_subcategory_lookup
  product_subcategory_key INT PRIMARY KEY
  subcategory_name VARCHAR
  product_category_key INT REFERENCES product_category_lookup(product_category_key)

TABLE: product_lookup
  product_key INT PRIMARY KEY
  product_subcategory_key INT REFERENCES product_subcategory_lookup(product_subcategory_key)
  product_sku VARCHAR
  product_name VARCHAR
  model_name VARCHAR
  product_description TEXT
  product_color VARCHAR
  product_size VARCHAR
  product_style VARCHAR
  product_cost NUMERIC
  product_price NUMERIC

TABLE: customer_lookup
  customer_key INT PRIMARY KEY
  prefix VARCHAR
  first_name VARCHAR
  last_name VARCHAR
  birth_date DATE
  marital_status VARCHAR
  gender VARCHAR
  email_address VARCHAR
  annual_income NUMERIC
  total_children INT
  education_level VARCHAR
  occupation VARCHAR
  home_owner VARCHAR

TABLE: sales_data
  order_date DATE
  stock_date DATE
  order_number VARCHAR
  product_key INT REFERENCES product_lookup(product_key)
  customer_key INT REFERENCES customer_lookup(customer_key)
  territory_key INT REFERENCES territory_lookup(territory_key)
  order_line_item INT
  order_quantity INT
  PRIMARY KEY (order_number, order_line_item)

TABLE: returns_data
  return_date DATE
  territory_key INT REFERENCES territory_lookup(territory_key)
  product_key INT REFERENCES product_lookup(product_key)
  return_quantity INT

RELATIONSHIPS SUMMARY:
  sales_data.product_key -> product_lookup.product_key
  sales_data.customer_key -> customer_lookup.customer_key
  sales_data.territory_key -> territory_lookup.territory_key
  product_lookup.product_subcategory_key -> product_subcategory_lookup.product_subcategory_key
  product_subcategory_lookup.product_category_key -> product_category_lookup.product_category_key
  returns_data.product_key -> product_lookup.product_key
  returns_data.territory_key -> territory_lookup.territory_key

IMPORTANT NOTES FOR WRITING SQL:
- Revenue = SUM(sales_data.order_quantity * product_lookup.product_price), requires a JOIN.
- Profit = SUM(sales_data.order_quantity * (product_lookup.product_price - product_lookup.product_cost)).
- To break revenue down by category, join sales_data -> product_lookup ->
  product_subcategory_lookup -> product_category_lookup.
- To break down by region, join sales_data -> territory_lookup.
- Always use explicit JOINs.
- Only generate SELECT statements.
- Dates are stored as proper DATE types; use standard PostgreSQL date functions.
- For monthly/time-trend questions spanning more than one year, ALWAYS use
  DATE_TRUNC('month', date_column) rather than EXTRACT(MONTH FROM date_column).
  EXTRACT(MONTH FROM ...) discards the year and would incorrectly merge every
  January across all years into a single bucket. DATE_TRUNC('month', ...)
  returns a proper date value that preserves the year, is safe to chart on a
  time axis, and is required whenever the question could span multiple years.
- The dataset only contains data from 2020-01-01 to 2022-12-31. When a question
  uses relative terms like "last year", "this year", "recently", or "last quarter",
  interpret them relative to the most recent date in the data (2022-12-31), NOT
  today's actual calendar date.
"""