from flask import Flask, jsonify
import os
import socket
import psycopg

app = Flask(__name__)


def get_db_connection():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )


def initialise_database():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS visits (
                    id SERIAL PRIMARY KEY,
                    visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()


@app.route("/api/health")
def health():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            database_version = cur.fetchone()[0]

    return jsonify(
        status="healthy",
        service="python-api",
        hostname=socket.gethostname(),
        database="connected",
        database_version=database_version
    )


@app.route("/api/visits")
def visits():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO visits DEFAULT VALUES RETURNING id;")
            visit_id = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM visits;")
            total_visits = cur.fetchone()[0]

        conn.commit()

    return jsonify(
        visit_id=visit_id,
        total_visits=total_visits,
        database="PostgreSQL"
    )


if __name__ == "__main__":
    initialise_database()
    app.run(host="0.0.0.0", port=5000)
