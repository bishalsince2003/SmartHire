-- VIEWS 
USE ecom;
CREATE VIEW dedup_view AS 
SELECT
	subquery.*
FROM
(
SELECT 
	*,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY ID) AS dedup
FROM 
	customers
) subquery
WHERE 
	dedup = 1;
    
SELECT * FROM dedup_view