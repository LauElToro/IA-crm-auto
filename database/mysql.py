# database/mysql.py
from __future__ import annotations
import os, json, pymysql
from typing import Any, Dict, List
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "ia_crm_auto")

def _connect(database: str | None = None):
    return pymysql.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
        database=database, cursorclass=DictCursor, autocommit=True
    )

def get_conn():
    try:
        return _connect(DB_NAME)
    except pymysql.err.OperationalError as e:
        # 1049 -> Unknown database
        if getattr(e, "args", [None])[0] == 1049:
            # Conecta sin DB, crea la DB y reintenta
            with _connect(None) as admin, admin.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            return _connect(DB_NAME)
        raise

def ensure_tables():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(255) NULL,
                email VARCHAR(255) NULL,
                telefono VARCHAR(50) NULL,
                empresa VARCHAR(255) NULL,
                cargo VARCHAR(255) NULL,
                industria VARCHAR(255) NULL,
                puntaje DECIMAL(10,2) NULL,
                explicacion TEXT NULL,
                payload JSON NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

def get_all_leads(limit: int = 500) -> List[Dict[str, Any]]:
    try:
        ensure_tables()
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM leads ORDER BY id DESC LIMIT %s", (limit,))
            return cur.fetchall()
    except pymysql.err.OperationalError as e:
        print(f"[DB] OperationalError en get_all_leads: {e}")
        return []

def insert_lead(lead: Dict[str, Any]) -> None:
    try:
        ensure_tables()
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO leads (nombre, email, telefono, empresa, cargo, industria, puntaje, explicacion, payload)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    lead.get("nombre"), lead.get("email"), lead.get("telefono"),
                    lead.get("empresa"), lead.get("cargo"), lead.get("industria"),
                    lead.get("puntaje"), lead.get("explicacion"), json.dumps(lead, ensure_ascii=False),
                ),
            )
    except pymysql.err.OperationalError as e:
        print(f"[DB] OperationalError en insert_lead: {e}")
        # si preferís cortar el request: raise
