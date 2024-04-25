import sqlite3

def check_database(db_path):
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Count the total number of entries
    cursor.execute("SELECT COUNT(*) FROM listings")
    total_entries = cursor.fetchone()[0]
    print(f"Total entries in the database: {total_entries}")

    # Fetch the first 5 entries to review
    cursor.execute("SELECT * FROM listings")
    sample_entries = cursor.fetchall()
    print("Sample entries:")
    for entry in sample_entries:
        print(entry)

    # Close database connection
    conn.close()

def filter_and_sort_best_opportunities(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Adjust the SQL query for floating-point division and include price filtering
    cursor.execute("""
        SELECT address, price, size,
               CAST(REPLACE(price, '$', '') AS REAL) / 
               CAST(REPLACE(size, ' acres', '') AS REAL) AS price_per_acre
        FROM listings
        WHERE price LIKE '%$%' AND size LIKE '% acres'
          AND CAST(REPLACE(price, '$', '') AS REAL) < 200000  -- Filter for prices below $200,000
        ORDER BY price_per_acre ASC
        LIMIT 5
    """)
    best_opportunities = cursor.fetchall()

    print("Best 5 land opportunities (sorted by price per acre):")
    for opportunity in best_opportunities:
        print(f"Address: {opportunity[0]}")
        print(f"Price: {opportunity[1]}, Size: {opportunity[2]}, Price/Acre: {opportunity[3]:.2f}")
        print("--------------------------")

    # Close database connection
    conn.close()

if __name__ == '__main__':
    db_path = 'lodb.db'  # Path to your database file
    check_database(db_path)

    filter_and_sort_best_opportunities(db_path)