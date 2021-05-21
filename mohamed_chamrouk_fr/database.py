from sqlalchemy import create_engine
from mohamed_chamrouk_fr import app


def create_connection():
    try:
        engine = create_engine(str(app.config['SQLALCHEMY_DATABASE_URI']))
        return engine
    except Exception as e:
        print(e)


def create_table(c, sql):
    c.execute(sql)


"""def update_or_create_page(c, data):
    sql = "SELECT * FROM public.pages where name=%s and session=%s"
    connection = c.raw_connection().cursor()
    connection.execute(sql, data[:-1])
    result = connection.fetchone()
    if result is None:
        create_pages(c, data)
    else:
        print(result)
        update_pages(c, result['id'])
    connection.close()"""


def update_or_create_page(c, data):
    sql = "SELECT * FROM public.pages where name=%s and session=%s"
    with c.connect() as connection:
        result = connection.execute(sql, data[:-1]).fetchone()
        if result is None:
            create_pages(c, data)
        else:
            print(result)
            update_pages(c, result['id'])


def create_pages(c, data):
    print(data)
    sql = ''' INSERT INTO public.pages(name,session,first_visited)
              VALUES (%s,%s,%s) '''
    with c.connect() as connection:
        connection.execute(sql, data)


def update_pages(c, pageId):
    print(pageId)
    sql = ''' UPDATE public.pages
              SET visits = visits+1
              WHERE id = %s'''
    with c.connect() as connection:
        connection.execute(sql, [pageId])


def create_session(c, data):
    sql = ''' INSERT INTO public.sessions(ip, continent, country, city, os, browser, session, created_at)
              VALUES (%s,%s,%s,%s,%s,%s,%s,%s) '''
    with c.connect() as connection:
        connection.execute(sql, data)


def select_all_sessions(c):
    sql = "SELECT * FROM public.sessions"
    with c.connect() as connection:
        rows = connection.execute(sql).fetchall()
        return rows


def select_all_pages(c):
    sql = "SELECT * FROM public.pages"
    with c.connect() as connection:
        rows = connection.execute(sql).fetchall()
        return rows


def select_all_user_visits(c, session_id):
    sql = "SELECT * FROM public.pages where session =%s"
    with c.connect() as connection:
        rows = connection.execute(sql, [session_id]).fetchall()
        return rows


def main():
    sql_create_pages = """
        CREATE TABLE IF NOT EXISTS public.pages (
            id SERIAL PRIMARY KEY,
            name varchar(225) NOT NULL,
            session varchar(255) NOT NULL,
            first_visited TIMESTAMP NOT NULL,
            visits integer NOT NULL Default 1
        );
    """
    sql_create_session = """
        CREATE TABLE IF NOT EXISTS public.sessions (
            id SERIAL PRIMARY KEY,
            ip varchar(225) NOT NULL,
            continent varchar(225) NOT NULL,
            country varchar(225) NOT NULL,
            city varchar(225) NOT NULL,
            os varchar(225) NOT NULL,
            browser varchar(225) NOT NULL,
            session varchar(225) NOT NULL,
            created_at TIMESTAMP NOT NULL
        );
    """
    # create a database connection
    conn = create_connection()
    if conn is not None:
        # create tables
        create_table(conn, sql_create_pages)
        create_table(conn, sql_create_session)
        print("Connection established!")
    else:
        print("Could not establish connection")


if __name__ == '__main__':
    main()
