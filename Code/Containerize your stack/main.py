from contextlib import asynccontextmanager
import os

import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting server...")

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS people (
                    name TEXT,
                    last_name TEXT
                );
            """)
            conn.commit()

    yield

    print("Stopping server...")


app = FastAPI(lifespan=lifespan)


@app.post("/new_user")
async def new_user(name: str, last_name: str):
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO people (name, last_name) VALUES (%s, %s);",
                (name, last_name),
            )
            conn.commit()

    return {"message": "User added successfully"}


@app.delete("/remove_user")
async def remove_user(name: str, last_name: str):
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM people WHERE name = %s AND last_name = %s;",
                (name, last_name),
            )
            conn.commit()

    return {"message": "User removed successfully"}


@app.get("/show_users")
async def show_users():
    with psycopg.connect(**DB_CONFIG, row_factory=dict_row) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM people;")
            users = cursor.fetchall()

    return users
