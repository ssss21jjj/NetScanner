"""
input_validator.py — Safe input parsing for scan parameters.
Uses netaddr (third-party) for CIDR expansion.
"""
from __future__ import annotations

try:
    import netaddr  # pip install netaddr
    NETADDR_AVAILABLE = True
except ImportError:
    import ipaddress
    NETADDR_AVAILABLE = False


def expand_targets(target: str) -> list[str]:
    target = target.strip()
    try:
        if NETADDR_AVAILABLE:
            network = netaddr.IPNetwork(target)
            return [str(ip) for ip in network.iter_hosts() or [netaddr.IPAddress(target)]]
        else:
            try:
                net = ipaddress.ip_network(target, strict=False)
                hosts = list(net.hosts())
                return [str(ip) for ip in hosts] if hosts else [target]
            except ValueError:
                ipaddress.ip_address(target)
                return [target]
    except Exception as exc:
        raise ValueError(f"Invalid target '{target}': {exc}") from exc


def validate_port_range(start: int, end: int) -> None:
    """
    Validate port range bounds.

    Raises:
        ValueError: If ports are out of [1, 65535] or start > end.
    """
    if not (1 <= start <= 65535) or not (1 <= end <= 65535):
        raise ValueError(f"Ports must be in range 1–65535, got {start}–{end}")
    if start > end:
        raise ValueError(f"Port start ({start}) must be ≤ port end ({end})")


def validate_timeout(timeout: float) -> None:
    """Validate timeout is positive and within safe bounds."""
    if not (0.05 <= timeout <= 30.0):
        raise ValueError(f"Timeout must be 0.05–30.0 seconds, got {timeout}")
