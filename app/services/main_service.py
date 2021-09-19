import psycopg2
from dotenv import load_dotenv
import os
from psycopg2 import sql
from psycopg2.errors import UndefinedColumn, UniqueViolation, UndefinedTable




class Anime:
    def __init__(self, data: dict):
        self.id, self.anime, self.released_date, self.seasons = data

    @staticmethod
    def connect_db():
        load_dotenv()

        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST'),
            database=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PWD')
            )

        cur = conn.cursor()

        return conn, cur

    @staticmethod
    def commit_and_close(conn, cur):

        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def create_table():
        conn, cur = Anime.connect_db()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS animes (
                id BIGSERIAL PRIMARY KEY,
                anime VARCHAR(100) NOT NULL UNIQUE,
                released_date DATE NOT NULL,
                seasons INTEGER NOT NULL
            );
            """
        )

        Anime.commit_and_close(conn, cur)

    @staticmethod
    def checking_method(method, request):
        if method == 'POST':
            output = Anime.save(request)
            return output

        output = Anime.get_all()
        return output

    @staticmethod
    def save(request):
        try:
            for item in request:
                if item == 'anime':
                    request[item] = request[item].title()

            Anime.create_table()
            conn, cur = Anime.connect_db()
            columns = [sql.Identifier(key) for key in request.keys()]
            values = [sql.Literal(value) for value in request.values()]
            query = sql.SQL(
                """
                    INSERT INTO
                        animes (id, {columns})
                    VALUES
                        (DEFAULT, {values})
                    RETURNING *
                """).format(columns=sql.SQL(',').join(columns),
                            values=sql.SQL(',').join(values))
            cur.execute(query)
            fetch_result = cur.fetchone()
            Anime.commit_and_close(conn, cur)
            serialized_data = Anime(fetch_result).__dict__
            return serialized_data, 201

        except UndefinedColumn:
            k_accepted = ['anime', 'released_date', 'seasons']
            k_not_accepted = [k for k in request.keys() if k not in k_accepted]
            return {f'available_keys': k_accepted, 'wrong_keys_sended': k_not_accepted}, 422

        except UniqueViolation:
            return {"error": 'anime is already exists'}, 409

    @staticmethod
    def get_all():
        try:
            conn, cur = Anime.connect_db()

            cur.execute(' SELECT * FROM animes;')

            fecth_result = cur.fetchall()

            Anime.commit_and_close(conn, cur)

            serialized_data = [Anime(data).__dict__ for data in fecth_result]

            if fecth_result.__len__() == 0:
                return {'data': []}, 200

            return serialized_data, 200
        except UndefinedTable:
            Anime.create_table()
            return {'data': []}, 200

    @staticmethod
    def get_by_id(id):
        try:
            conn, cur = Anime.connect_db()

            cur.execute('SELECT * FROM animes WHERE id=(%s);', (id, ))

            fetch_result = cur.fetchone()
            Anime.commit_and_close(conn, cur)

            serialize_data = Anime(fetch_result).__dict__

            return serialize_data, 200
        except (TypeError, UndefinedTable):
            return {'error': "Not Found"}, 404

    @staticmethod
    def update(id, data):
        try:
            Anime.create_table()
            conn, cur = Anime.connect_db()

            for item in data:
                if item == 'anime':
                    data[item] = data[item].title()

            query = sql.SQL("UPDATE animes SET {datas} WHERE id = {id} RETURNING *").format(
                datas=sql.SQL(', ').join(
                    sql.Composed([sql.Identifier(k), sql.SQL(" = "), sql.Placeholder(k)]) for k in data.keys()
                ),
                id=sql.Placeholder('id')
                )

            data.update(id=id)
            cur.execute(query, data)

            fetch_result = cur.fetchone()
            Anime.commit_and_close(conn, cur)
            serialized_data = Anime(fetch_result).__dict__

            return serialized_data, 200

        except UndefinedColumn:
            k_accepted = ['anime', 'released_date', 'seasons']
            k_not_accepted = [k for k in data.keys() if k not in k_accepted]
            return {f'available_keys': k_accepted, 'wrong_keys_sended': k_not_accepted}, 422

        except UndefinedTable:
            return {"error": 'anime is already exists'}, 409

        except (TypeError, UndefinedTable):
            return {'error': "Not Found"}, 404

    @staticmethod
    def delete(id):
        try:
            conn, cur = Anime.connect_db()
            sql = 'DELETE FROM animes WHERE id=(%s) RETURNING*;'
            cur.execute(sql, (id, ))

            fetch_result = cur.fetchone()
            Anime.commit_and_close(conn, cur)

            serialize_data = Anime(fetch_result).__dict__
            return serialize_data, 204

        except (TypeError, UndefinedTable):
            return {'error': "Not Found"}, 404


# Anime.update(1,{"anime": "mxIsTeR",})