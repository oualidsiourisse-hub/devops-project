from contextlib import asynccontextmanager, closing
import os
import time
import logging
from fastapi import FastAPI, HTTPException
import psycopg2
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TaskCreate(BaseModel):
    title: str


def get_db_connection():
    """Ouvre et retourne une connexion à la base PostgreSQL via les variables d'environnement."""
    return psycopg2.connect(
        host=os.getenv("DATABASE_HOST", "db"),
        port=os.getenv("DATABASE_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def init_db():
    """Crée la table tasks si elle n'existe pas."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS tasks (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        done BOOLEAN NOT NULL DEFAULT FALSE
    );
    """
    with closing(get_db_connection()) as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute(create_table_sql)


@asynccontextmanager
async def lifespan(app: FastAPI):
    max_attempts = 10
    for attempt in range(1, max_attempts + 1):
        try:
            init_db()
            break
        except Exception:
            if attempt == max_attempts:
                raise
            logger.warning("Base indisponible (tentative %s/%s)", attempt, max_attempts)
            time.sleep(2)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    """Crée une nouvelle tâche à partir d'un titre."""
    insert_sql = """
    INSERT INTO tasks (title)
    VALUES (%s)
    RETURNING id, title, done;
    """
    try:
        with closing(get_db_connection()) as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(insert_sql, (task.title,))
                    row = cur.fetchone()
        return {
            "id": row[0],
            "title": row[1],
            "done": row[2],
        }
    except Exception:
        logger.exception("Erreur lors de la création de la tâche")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la création de la tâche.",
        )

@app.get("/tasks")
def list_tasks():
    """Liste toutes les tâches enregistrées."""
    select_sql = """
    SELECT id, title, done
    FROM tasks
    ORDER BY id ASC;
    """
    try:
        with closing(get_db_connection()) as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(select_sql)
                    rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "title": row[1],
                "done": row[2],
            }
            for row in rows
        ]
    except Exception:
        logger.exception("Erreur lors de la création de la tâche")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la création de la tâche.",
        )