import mysql.connector


def create_tables(db):
    cursor = db.cursor()
    try:
        # Check if the database exists
        print("Checking for the Database...")
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        db_exists = False
        for database in databases:
            if 'blog_db' in database:
                db_exists = True
                break

        # If the database doesn't exist, create it
        if not db_exists:
            print("Database not Found")
            print("Creating Database...")
            cursor.execute("CREATE DATABASE blog_db")
            print("Database 'blog_db' created successfully.")
        else:
            print("Database Found")
    except mysql.connector.Error as err:
        print("Error:", err)

    # Switch to the 'blog_db' database
    cursor.execute("USE blog_db")

    # Create users table if not exists
    cursor.execute("""CREATE TABLE IF NOT EXISTS user (
                          id INT AUTO_INCREMENT PRIMARY KEY,
                          first_name VARCHAR(50),
                          last_name VARCHAR(50),
                          email VARCHAR(50) UNIQUE,
                          password VARCHAR(100)
                      )""")

    # Create posts table if not exists
    cursor.execute("""CREATE TABLE IF NOT EXISTS posts (
                          id INT AUTO_INCREMENT PRIMARY KEY,
                          title VARCHAR(100),
                          content TEXT,
                          date_posted DATETIME DEFAULT CURRENT_TIMESTAMP,
                          user_id INT,
                          FOREIGN KEY (user_id) REFERENCES user(id)
                      )""")

    # Create comment table if not exists
    cursor.execute("""CREATE TABLE IF NOT EXISTS comment (
                          id INT AUTO_INCREMENT PRIMARY KEY,
                          content TEXT,
                          date_posted DATETIME DEFAULT CURRENT_TIMESTAMP,
                          user_id INT,
                          post_id INT,
                          FOREIGN KEY (user_id) REFERENCES user(id),
                          FOREIGN KEY (post_id) REFERENCES posts(id)
                      )""")

    cursor.close()
    print("Tables created successfully.")
