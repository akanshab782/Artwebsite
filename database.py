import sqlite3

def create_tables():
    conn = sqlite3.connect("art_gallery.db")
    cursor = conn.cursor()

    # Table 1: Keychains
    cursor.execute('''CREATE TABLE IF NOT EXISTS keychains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        base TEXT NOT NULL,
        starting_price REAL NOT NULL,
        image TEXT,
        stock INTEGER DEFAULT 0
    )''')

    # Table 2: Flowers
    cursor.execute('''CREATE TABLE IF NOT EXISTS flowers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        price REAL NOT NULL,
        image TEXT,
        stock INTEGER DEFAULT 0
    )''')

    # Table 3: Customers
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        email TEXT,
        visit_date DATE
    )''')

    # Table 4: Page Visits
    cursor.execute('''CREATE TABLE IF NOT EXISTS page_visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        page_visited TEXT,
        product_viewed TEXT,
        time_spent INTEGER,
        visit_date DATE,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )''')

    # Table 5: Sales
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        product_id INTEGER,
        product_type TEXT,
        amount_paid REAL,
        date DATE,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )''')

    # Table 6: Chatbot Conversations
    cursor.execute('''CREATE TABLE IF NOT EXISTS chatbot (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        question_asked TEXT,
        response_given TEXT,
        sentiment TEXT,
        date DATE,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )''')

    # Table 7: Feedback
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        product_id INTEGER,
        liked BOOLEAN,
        reason TEXT,
        rating INTEGER,
        date DATE,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )''')

    # Sample data for keychains
    cursor.execute("SELECT COUNT(*) FROM keychains")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO keychains (base, starting_price, stock) VALUES (?,?,?)", [
            ("Wooden", 119, 10),
            ("Acrylic", 199, 15),
            ("Black Acrylic", 149, 8),
        ])

    # Sample data for flowers
    cursor.execute("SELECT COUNT(*) FROM flowers")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO flowers (type, price, stock) VALUES (?,?,?)", [
            ("Rose Bouquet", 299, 20),
            ("Sunflower", 299, 25),
            ("Tulip", 249, 18),
        ])

    conn.commit()
    conn.close()
    print("✅ Database and tables created successfully!")

if __name__ == "__main__":
    create_tables()