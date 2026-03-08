"""
sqlite_repo.py — SQLite persistence layer.
"""
from __future__ import annotations
import sqlite3
import os
from typing import Optional

from core.models import ScanJob, PortResult
from core.data_structures import NetworkGraph


DB_PATH = os.path.join("data", "scans.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS scan_jobs (
    job_id TEXT PRIMARY KEY, target TEXT NOT NULL,
    port_start INTEGER NOT NULL, port_end INTEGER NOT NULL,
    timeout REAL NOT NULL, threads INTEGER NOT NULL,
    timestamp TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS hosts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL, ip TEXT NOT NULL, hostname TEXT DEFAULT '',
    FOREIGN KEY (job_id) REFERENCES scan_jobs(job_id)
);
CREATE TABLE IF NOT EXISTS ports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id INTEGER NOT NULL, port INTEGER NOT NULL,
    state TEXT NOT NULL, service TEXT, response_ms REAL,
    FOREIGN KEY (host_id) REFERENCES hosts(id)
);
CREATE INDEX IF NOT EXISTS idx_hosts_job ON hosts(job_id);
CREATE INDEX IF NOT EXISTS idx_ports_host ON ports(host_id);
"""


class SQLiteRepository:
    """Handles all SQLite read/write operations for scan data."""

    def __init__(self, db_path: str = DB_PATH) -> None:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        """Create tables and indexes if they do not exist."""
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()

    def save_scan(self, job: ScanJob, graph: NetworkGraph) -> None:
        """
        Persist a complete scan (job metadata + all hosts + ports).

        Args:
            job:   ScanJob instance with metadata.
            graph: Populated NetworkGraph from the scan.
        """
        cur = self._conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO scan_jobs VALUES (?,?,?,?,?,?,?)",
            (job.job_id, job.target, job.port_start, job.port_end,
             job.timeout, job.threads, job.timestamp),
        )
        for ip in graph.get_hosts():
            cur.execute(
                "INSERT INTO hosts (job_id, ip) VALUES (?,?)", (job.job_id, ip)
            )
            host_id = cur.lastrowid
            for pr in graph.get_ports(ip):
                cur.execute(
                    "INSERT INTO ports (host_id, port, state, service, response_ms)"
                    " VALUES (?,?,?,?,?)",
                    (host_id, pr.port, pr.state, pr.service, pr.response_ms),
                )
        self._conn.commit()

    def list_scans(self) -> list[dict]:
        """Return summary list of all saved scan jobs."""
        cur = self._conn.execute(
            "SELECT job_id, target, timestamp FROM scan_jobs ORDER BY timestamp DESC"
        )
        return [{"job_id": r[0], "target": r[1], "timestamp": r[2]} for r in cur]

    def load_scan(self, job_id: str) -> Optional[NetworkGraph]:
        """
        Reconstruct a NetworkGraph from the database for a given job_id.

        Returns:
            NetworkGraph if found, None otherwise.
        """
        graph = NetworkGraph()
        hosts = self._conn.execute(
            "SELECT id, ip FROM hosts WHERE job_id=?", (job_id,)
        ).fetchall()
        if not hosts:
            return None
        for host_id, ip in hosts:
            graph.add_host(ip)
            ports = self._conn.execute(
                "SELECT port, state, service, response_ms FROM ports WHERE host_id=?",
                (host_id,),
            ).fetchall()
            for port, state, service, rms in ports:
                graph.add_port(ip, PortResult(port, state, service, rms))
        return graph

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()
