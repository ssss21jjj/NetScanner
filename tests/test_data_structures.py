"""
tests/test_data_structures.py — Unit tests for CustomQueue and NetworkGraph.
Run: pytest tests/ --cov=netscanner
"""
import pytest
from core.data_structures import CustomQueue, NetworkGraph
from core.models import PortResult


class TestCustomQueue:
    def test_enqueue_dequeue_fifo_order(self):
        q = CustomQueue()
        q.enqueue("a"); q.enqueue("b"); q.enqueue("c")
        assert q.dequeue() == "a"
        assert q.dequeue() == "b"
        assert q.dequeue() == "c"

    def test_len_tracks_correctly(self):
        q = CustomQueue()
        assert len(q) == 0
        q.enqueue(1); q.enqueue(2)
        assert len(q) == 2
        q.dequeue()
        assert len(q) == 1

    def test_dequeue_empty_raises_index_error(self):
        q = CustomQueue()
        with pytest.raises(IndexError):
            q.dequeue()

    def test_is_empty(self):
        q = CustomQueue()
        assert q.is_empty() is True
        q.enqueue("x")
        assert q.is_empty() is False

    def test_peek_does_not_remove(self):
        q = CustomQueue()
        q.enqueue(42)
        assert q.peek() == 42
        assert len(q) == 1


class TestNetworkGraph:
    def test_add_host_and_get_hosts(self):
        g = NetworkGraph()
        g.add_host("10.0.0.1")
        assert "10.0.0.1" in g.get_hosts()

    def test_add_host_idempotent(self):
        g = NetworkGraph()
        g.add_host("10.0.0.1")
        g.add_host("10.0.0.1")
        assert g.get_hosts().count("10.0.0.1") == 1

    def test_add_port_to_host(self):
        g = NetworkGraph()
        g.add_host("10.0.0.1")
        pr = PortResult(80, "open", "HTTP", 12.5)
        g.add_port("10.0.0.1", pr)
        assert len(g.get_ports("10.0.0.1")) == 1
        assert g.get_ports("10.0.0.1")[0].port == 80

    def test_add_port_unknown_host_raises(self):
        g = NetworkGraph()
        with pytest.raises(KeyError):
            g.add_port("1.2.3.4", PortResult(80, "open"))

    def test_to_dict_structure(self):
        g = NetworkGraph()
        g.add_host("10.0.0.1")
        d = g.to_dict()
        assert "10.0.0.1" in d
        assert isinstance(d["10.0.0.1"], list)
