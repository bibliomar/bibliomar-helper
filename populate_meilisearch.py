from bibliomar_helper.populate_meili.helper import connect_to_mysql

# Add relevant fields from the database to the main Meilisearch index in batches of 100.
if __name__ == "__main__":
    conn = connect_to_mysql()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM fiction LIMIT 100")
            print(cursor.fetchall())
