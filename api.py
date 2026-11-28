import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from advice import TIPS

DB_PATH = Path(os.getenv("DATABASE_PATH", "data/climate_nearby.sqlite3"))

app = FastAPI(
    title="Climate Nearby API",
    description="Экологические советы и карта сообщений о локальных проблемах.",
    version="1.0.0",
)


class ProblemCreate(BaseModel):
    category: Literal["мусор", "загрязнение воздуха", "жара", "другое"]
    description: str = Field(min_length=5, max_length=500)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


def connect_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with closing(connect_db()) as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
            )"""
        )
        connection.commit()


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/tips")
def get_tips(category: str | None = None) -> dict[str, list[dict[str, str]]]:
    tips = TIPS
    if category:
        tips = [tip for tip in TIPS if tip["category"] == category]
    return {"tips": tips}


@app.post("/api/problems", status_code=201)
def create_problem(problem: ProblemCreate) -> dict[str, object]:
    with closing(connect_db()) as connection:
        cursor = connection.execute(
            """INSERT INTO problems (category, description, latitude, longitude)
               VALUES (?, ?, ?, ?)""",
            (problem.category, problem.description.strip(), problem.latitude, problem.longitude),
        )
        connection.commit()
        problem_id = cursor.lastrowid
    return {"id": problem_id, "message": "Сообщение добавлено на карту как непроверенное."}


@app.get("/api/problems")
def get_problems() -> dict[str, object]:
    with closing(connect_db()) as connection:
        rows = connection.execute(
            "SELECT id, category, description, latitude, longitude, created_at "
            "FROM problems ORDER BY id DESC"
        ).fetchall()
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row["longitude"], row["latitude"]]},
                "properties": {
                    "id": row["id"],
                    "category": row["category"],
                    "description": row["description"],
                    "created_at": row["created_at"],
                    "status": "не проверено",
                },
            }
            for row in rows
        ],
    }


@app.get("/map", response_class=HTMLResponse)
def map_page() -> HTMLResponse:
    page = Path(__file__).parent / "map.html"
    if not page.exists():
        raise HTTPException(status_code=404, detail="Страница карты не найдена")
    return HTMLResponse(page.read_text(encoding="utf-8"))
