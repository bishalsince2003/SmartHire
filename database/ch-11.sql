-- REAL TIME SCENARIOS

-- SCENARIO 1 [Finding the nth value]

-- Information of the product of maximum price
SELECT 
	*
FROM 
	dim_product
WHERE 
	unit_price = ( SELECT MAX(unit_price) FROM dim_product);

WITH cte_table AS
(
SELECT 
	*
FROM 
	dim_product
ORDER BY
	unit_price DESC
LIMIT 5
)
SELECT * FROM cte_table
WHERE unit_price = ( SELECT MIN(unit_price) FROM cte_table);

SELECT 
	subquery.*
FROM 
(
SELECT
	*,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY unit_price DESC) AS ranking
FROM 
	dim_product
) subquery
WHERE 
	ranking =5 AND
    category IN ('Toys' , 'Sports');
    
USE ecom;
-- SCENARIO 2 [ REMOVING DUPLICATES ] 

SELECT 
	subquery.*
FROM
(
SELECT 
	*,
    ROW_NUMBER() OVER (PARTITION by id ORDER BY id) AS dedup
FROM 
	customers
) subquery
WHERE 
	dedup >1;
INSERT INTO customers
VALUES
(101,'bishal' , 'aa');


-- SCENARIO 3 [LAG AND LEAD]
CREATE TABLE weather
(
	id INT,
    temp float
)

INSERT INTO weather 
VALUES
(1,10),
(2,12),
(3,9),
(4,15),
(5,20),
(6,15),
(7,12)

SELECT * FROM weather

SELECT 
	*,
    LAG (temp,1,0) OVER (ORDER BY id ASC) AS pre_day_temp,
    LAG (temp,2,0) OVER (ORDER BY id ASC) AS pre2_day_temp,
    LEAD (temp,1,0) OVER (ORDER BY id ASC) AS post_day_temp
FROM 
	weather
