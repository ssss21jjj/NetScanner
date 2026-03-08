"""
file_repo.py — JSON, CSV and log file persistence.
"""
from __future__ import annotations
import json
import csv
import os
import logging
from datetime import datetime

from core.models import PortResult
from core.data_structures import NetworkGraph


EXPORT_DIR = os.path.join("data", "exports")
LOG_PATH   = os.path.join("data", "logs", "scanner.log")

# Create directories BEFORE setting up logging (fixes FileNotFoundError)
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(os.path.join("data", "logs"), exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger("netscanner")


class FileRepository:
    """Handles JSON, CSV export/import and structured log writes."""

    def __init__(self, export_dir: str = EXPORT_DIR) -> None:
        os.makedirs(export_dir, exist_ok=True)
        self._export_dir = export_dir

    def export_json(self, graph: NetworkGraph, filename: str) -> str:
        """
        Serialise graph to JSON file.

        Args:
            graph:    NetworkGraph instance to serialise.
            filename: Output filename (not full path).

        Returns:
            Absolute path of written file.
        """
        path = os.path.join(self._export_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(graph.to_dict(), f, indent=2)
        logger.info("Exported JSON: %s", path)
        return path

    def import_json(self, path: str) -> NetworkGraph:
        """
        Deserialise a NetworkGraph from a JSON file.

        Args:
            path: Full path to the JSON file.

        Returns:
            Reconstructed NetworkGraph.

        Raises:
            FileNotFoundError: If file does not exist.
            json.JSONDecodeError: If file content is invalid JSON.
        """
        with open(path, "r", encoding="utf-8") as f:
            data: dict = json.load(f)
        graph = NetworkGraph()
        for ip, ports in data.items():
            graph.add_host(ip)
            for p in ports:
                graph.add_port(
                    ip,
                    PortResult(
                        port=p["port"],
                        state=p["state"],
                        service=p["service"],
                        response_ms=p["response_ms"],
                    ),
                )
        logger.info("Imported JSON: %s", path)
        return graph

    def export_csv(self, graph: NetworkGraph, filename: str) -> str:
        """
        Write flat CSV with columns: ip, port, state, service, response_ms.

        Args:
            graph:    NetworkGraph instance to serialise.
            filename: Output filename (not full path).

        Returns:
            Absolute path of written file.
        """
        path = os.path.join(self._export_dir, filename)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["ip", "port", "state", "service", "response_ms"],
            )
            writer.writeheader()
            for ip in graph.get_hosts():
                for pr in graph.get_ports(ip):
                    writer.writerow({
                        "ip": ip,
                        "port": pr.port,
                        "state": pr.state,
                        "service": pr.service,
                        "response_ms": pr.response_ms,
                    })
        logger.info("Exported CSV: %s", path)
        return path

    def log_event(self, message: str) -> None:
        """
        Write a custom event message to the log file.

        Args:
            message: Text to log.
        """
        logger.info(message)
