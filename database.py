import sqlite3


class Database:

    def __init__(self):
        self.connect_db()
        self.create_node_tables()
        self.create_setting_tables()

    def connect_db(self):
        self.connection = sqlite3.connect(
            'database.db', check_same_thread=False)

    def close_connection(self):
        if self.connection:
            self.connection.close()

    def create_setting_tables(self):
        cursor = self.connection.cursor()

        # Create the 'settings' table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT UNIQUE,
                value TEXT
            )
        """)

        # Insert initial settings data (if not already present)
        cursor.executemany("""
            INSERT OR IGNORE INTO settings (key, value)
            VALUES (?, ?)
        """, [
            ("Theme", "light"),
            ("WP_URL", ""),
            ("WP_Username", ""),
            ("WP_Password", "")
        ])
        self.connection.commit()

    def get_all_settings(self):
        query = "SELECT DISTINCT * FROM settings"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    
    def get_settings_by_key(self, key):
        cursor = self.connection.cursor()
        # Retrieve values for the specified keys
        cursor.execute("SELECT value FROM settings WHERE key = ?;", (key,))
        return cursor.fetchone()
    
    def update_settings_by_key(self, key, new_value):
        # Connect to the SQLite database
        cursor = self.connection.cursor()
         # Update the value if the key exists
        cursor.execute("UPDATE settings SET value = ? WHERE key = ?;", (new_value, key))
        # Commit the changes and close the connection
        self.connection.commit()

  
    ##########################################
    def create_node_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                title TEXT,
                content TEXT,
                createdDateTime DateTime,
                updatedDateTime DateTime,
                shortcut TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS note_category (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT UNIQUE
            )
        """)
        self.connection.commit()

    def get_all_note_item(self, category):
        cursor = self.connection.cursor()
        if category == "All Categories" or category == "":
            query = "SELECT * FROM notes ORDER BY datetime(updatedDateTime) DESC"
            cursor.execute(query)
        else:
            query = "SELECT * FROM notes WHERE category = ? ORDER BY datetime(updatedDateTime) DESC"
            cursor.execute(query, (category,))
        return cursor.fetchall()

    def get_note_item_by_id(self, id):
        cursor = self.connection.cursor()
        query = "SELECT * FROM notes WHERE id = ?"
        cursor.execute(query, (id,))
        return cursor.fetchone()

    def insert_note_item(self, category, title, content, created_datetime, updated_datetime, shortcut):
        query = "INSERT OR IGNORE INTO notes (category, title, content, createdDateTime, updatedDateTime, shortcut) VALUES (?, ?, ?, ?, ?, ?)"
        cursor = self.connection.cursor()
        cursor.execute(query, (category, title, content,
                            created_datetime, updated_datetime, shortcut))
        self.connection.commit()

    def update_note_item(self, id, category, title, content, updated_datetime, shortcut):
        query = "UPDATE notes SET category = ?, title = ?, content = ?, updatedDateTime = ?, shortcut = ? WHERE id = ?"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (category, title, content,
                           updated_datetime, shortcut, id))
            self.connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")

    def update_note_item_category(self, id, category, updated_datetime):
        query = "UPDATE notes SET category = ?, updatedDateTime = ? WHERE id = ?"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (category, updated_datetime, id))
            self.connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")

    def update_all_note_categories(self, old_category, new_category):
        query = "UPDATE notes SET category = ? WHERE category = ?"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (new_category, old_category))
            self.connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")


    def search_by_shortcut(self, shortcut):
        cursor = self.connection.cursor()
        query = "SELECT * FROM notes WHERE shortcut = ?"
        cursor.execute(query, (shortcut,))
        return cursor.fetchone()

    def update_shortcut(self, id, shortcut):
        if shortcut != "":
            # Check if shortcut already exists in other note item
            existing_shortcuts = self.search_by_shortcut(shortcut)
            for row in existing_shortcuts:
                if row['shortcut'] == shortcut and row['id'] != id:
                    raise sqlite3.IntegrityError("Shortcut already exists")
        query = "UPDATE notes SET shortcut = ? WHERE id = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (shortcut, id))
        self.connection.commit()

    def delete_note_item(self, id):
        query = "DELETE FROM notes WHERE id = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (id,))
        self.connection.commit()

    def count_total_note_item(self):
        query = "SELECT Count(*) FROM notes"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchone()[0]

    def search_note_item_by_title_for_treeview(self, text):
        query = """
            SELECT id, title, shortcut FROM notes
            WHERE title LIKE ?
            ORDER BY datetime(updatedDateTime) DESC
        """
        cursor = self.connection.cursor()
        cursor.execute(query, ('%' + text + '%',))  # Correct parameter passing
        return cursor.fetchall()

    def search_note_item_by_shortcut(self, shortcut):
        query = "SELECT * FROM notes WHERE shortcut = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (shortcut,))
        return cursor.fetchall()
    
    def search_note_category(self, category):
        query = "SELECT DISTINCT category FROM note_category WHERE category = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (category,))
        return cursor.fetchone()

    def insert_note_category(self, category):
        query = "INSERT OR IGNORE INTO note_category (category) VALUES (?)"
        cursor = self.connection.cursor()
        cursor.execute(query, (category,))
        self.connection.commit()

    def update_note_category(self, old_category,new_category):
        query = "UPDATE note_category SET category = ? WHERE category = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (new_category, old_category))
        self.connection.commit()

    def delete_note_category(self, category):
        query = "DELETE FROM note_category WHERE category = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (category,))
        self.connection.commit()

    def get_all_note_category(self):
        query = "SELECT DISTINCT category FROM note_category"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def count_total_note_category(self):
        query = "SELECT Count(*) FROM note_category"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchone()[0]

    def get_all_note_by_category(self, category):
        query = "SELECT * FROM notes WHERE category = ? ORDER BY datetime(updatedDateTime) DESC"
        cursor = self.connection.cursor()
        cursor.execute(query, (category,))
        return cursor.fetchall()

    def get_all_note_by_category_for_treeview(self, category):
        cursor = self.connection.cursor()

        if (category == "All Categories"): # select all note
            query = "SELECT id, title, shortcut FROM notes ORDER BY datetime(updatedDateTime) DESC"
            cursor.execute(query)
        else:
            query = "SELECT id, title, shortcut FROM notes WHERE category = ? ORDER BY datetime(updatedDateTime) DESC"
            cursor.execute(query, (category,))

        return cursor.fetchall()

    def search_note_category(self, text):
        query = "SELECT * FROM note_category WHERE category LIKE '%' || ? || '%'"
        cursor = self.connection.cursor()
        cursor.execute(query, (text,))
        return cursor.fetchall()
