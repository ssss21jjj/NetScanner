"""
models.py — Data model classes for scan results.
"""
from dataclasses import dataclass, field
from typing import Optional
import uuid
from datetime import datetime


@dataclass
class PortResult:
    """Represents the scan result for a single port."""
    port: int
    state: str                     # 'open' | 'closed' | 'filtered'
    service: str = "Unknown"
    response_ms: float = 0.0

    def to_dict(self) -> dict:
        """Serialise to dictionary for JSON/DB storage."""
        return {
            "port": self.port,
            "state": self.state,
            "service": self.service,
            "response_ms": self.response_ms,
        }


@dataclass
class HostNode:
    """Represents a scanned host with its open ports."""
    ip: str
    hostname: str = ""
    open_ports: list = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialise to dictionary."""
        return {
            "ip": self.ip,
            "hostname": self.hostname,
            "open_ports": [p.to_dict() for p in self.open_ports],
        }


@dataclass
class ScanJob:
    """Metadata for a scan session."""
    target: str
    port_start: int
    port_end: int
    timeout: float
    threads: int
    job_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "target": self.target,
            "port_start": self.port_start,
            "port_end": self.port_end,
            "timeout": self.timeout,
            "threads": self.threads,
            "timestamp": self.timestamp,
        }
