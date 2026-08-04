from nl2sql import is_safe_select


def test_allows_simple_select():
    assert is_safe_select("SELECT * FROM customer_lookup;") == True


def test_blocks_delete():
    assert is_safe_select("DELETE FROM customer_lookup;") == False


def test_blocks_drop():
    assert is_safe_select("DROP TABLE sales_data;") == False


def test_blocks_update():
    assert is_safe_select("UPDATE customer_lookup SET annual_income = 0;") == False


def test_blocks_insert():
    assert is_safe_select("INSERT INTO customer_lookup VALUES (1,2,3);") == False


def test_blocks_multiple_statements():
    assert is_safe_select("SELECT * FROM customer_lookup; DROP TABLE customer_lookup;") == False


def test_blocks_non_select_start():
    assert is_safe_select("EXPLAIN SELECT * FROM customer_lookup;") == False


def test_allows_select_with_join_and_group_by():
    sql = """
    SELECT t.country, SUM(s.order_quantity) AS total
    FROM sales_data s
    JOIN territory_lookup t ON s.territory_key = t.territory_key
    GROUP BY t.country;
    """
    assert is_safe_select(sql) == True
