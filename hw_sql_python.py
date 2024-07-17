import psycopg2


def create_db():
    conn = psycopg2.connect(database="postgres", user="postgres", password="123", host="127.0.0.1", client_encoding="UTF8")
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname='clients_db'")
        exists = cur.fetchone()
        if not exists:
            cur.execute("""CREATE DATABASE IF NOT EXISTS clients_db""")
            print("База данных clients_db успешно создана")
        else:
            print("База данных clients_db уже существует")            

def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS clients(
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    email VARCHAR(100) UNIQUE);
                    """)
        conn.commit()
        print("Таблица clients успешно создана")

        cur.execute("""
                    CREATE TABLE IF NOT EXISTS phones(
                    id SERIAL PRIMARY KEY,
                    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
                    phone VARCHAR(20));
                    """)
        conn.commit()
        print("Таблица phones успешно создана")

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO clients(first_name, last_name, email)
                    VALUES (%s, %s, %s) RETURNING id;
                    """, (first_name, last_name, email))

        client_id = cur.fetchone()[0]

        if phones:
            for phone in phones:
                cur.execute("""
                            INSERT INTO phones(client_id, phone)
                            VALUES (%s, %s);
                            """, (client_id, phone))
        conn.commit()
        print("Клиент успешно добавлен")
        return client_id

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO phones(client_id, phone)
                    VALUES (%s, %s);
                    """, (client_id, phone))
        conn.commit()
        print("Телефон успешно добавлен")

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute("""
                        UPDATE clients SET first_name = %s WHERE id = %s;
                        """, (first_name, client_id))

        if last_name:
            cur.execute("""
                        UPDATE clients SET last_name = %s WHERE id = %s;
                        """, (last_name, client_id))

        if email:
            cur.execute("""
                        UPDATE clients SET email = %s WHERE id = %s;
                        """, (email, client_id))

        if phones is not None:
            cur.execute("""
                        DELETE FROM phones WHERE client_id = %s;
                        """, (client_id,))
            for phone in phones:
                cur.execute("""
                            INSERT INTO phones (client_id, phone)
                            VALUES (%s, %s);
                            """, (client_id, phone))
        conn.commit()

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
                    DELETE FROM phones WHERE client_id = %s AND phone = %s;
                    """, (client_id, phone))
        conn.commit()
        print("Телефон успешно удален")

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
                    DELETE FROM clients WHERE id = %s;
                    """, (client_id,))
        conn.commit()
        print("Клиент успешно удален")

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        find_query = """
        SELECT c.id, c.first_name, c.last_name, c.email, p.phone FROM clients c
        LEFT JOIN phones p ON c.id = p.client_id
        WHERE 1=1
        """
        params = []
        if first_name:
            find_query += " AND c.first_name = %s"
            params.append(first_name)
        if last_name:
            find_query += " AND c.last_name = %s"
            params.append(last_name)
        if email:
            find_query += " AND c.email = %s"
            params.append(email)
        if phone:
            find_query += " AND p.phone = %s"
            params.append(phone)
        cur.execute(find_query, tuple(params))
        return cur.fetchall()


if __name__ == "__main__":
    create_db()
    with psycopg2.connect(database="clients_db", user="postgres", password="123", host="127.0.0.1", client_encoding="UTF8") as conn:
        create_tables(conn)
        client_id = add_client(conn, 'Test', 'Test', 'test@mail.ru')
        add_phone(conn, client_id, '+77755555555')
        change_client(conn, client_id, first_name='Onegin')
        delete_phone(conn, client_id, '+79876543210')
        delete_client(conn, client_id)
        clients = find_client(conn, first_name='Onegin')
        for client in clients:
            print(client)
