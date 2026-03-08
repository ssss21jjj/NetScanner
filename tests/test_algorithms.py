"""
tests/test_algorithms.py — Unit tests for merge_sort and service_fingerprint.
"""
import pytest
from core.algorithms import merge_sort, service_fingerprint
from core.models import PortResult


class TestMergeSort:
    def _make_results(self, ports):
        return [PortResult(p, "open") for p in ports]
    







    def test_sort_by_port_ascending(self):
        results = self._make_results([443, 22, 80])
        sorted_r = merge_sort(results, key=lambda r: r.port)
        assert [r.port for r in sorted_r] == [22, 80, 443]

    def test_sort_by_response_ms(self):
        r = [PortResult(80, "open", response_ms=5.0),
             PortResult(443, "open", response_ms=1.0)]
        sorted_r = merge_sort(r, key=lambda x: x.response_ms)
        assert sorted_r[0].port == 443

    def test_empty_list(self):
        assert merge_sort([]) == []

    def test_single_element(self):
        r = self._make_results([80])
        assert merge_sort(r, key=lambda x: x.port)[0].port == 80

    def test_already_sorted(self):
        r = self._make_results([22, 80, 443])
        sorted_r = merge_sort(r, key=lambda x: x.port)
        assert [x.port for x in sorted_r] == [22, 80, 443]

    def test_reverse_sort(self):
        r = self._make_results([22, 80, 443])
        sorted_r = merge_sort(r, key=lambda x: x.port, reverse=True)
        assert [x.port for x in sorted_r] == [443, 80, 22]


class TestServiceFingerprint:
    def test_known_ports(self):
        assert service_fingerprint(80)  == "HTTP"
        assert service_fingerprint(443) == "HTTPS"
        assert service_fingerprint(22)  == "SSH"

    def test_unknown_port_returns_unknown(self):
        assert service_fingerprint(9999) == "Unknown"
