import pytest

from chronos.ring_buffer import RingBuffer


def test_enqueue_and_dequeue():
    buffer = RingBuffer(3)

    buffer.enqueue("A")
    buffer.enqueue("B")

    assert buffer.dequeue() == "A"
    assert buffer.dequeue() == "B"


def test_fifo_order():
    buffer = RingBuffer(3)

    buffer.enqueue(10)
    buffer.enqueue(20)
    buffer.enqueue(30)

    assert buffer.dequeue() == 10
    assert buffer.dequeue() == 20
    assert buffer.dequeue() == 30


def test_circular_reuse():
    buffer = RingBuffer(3)

    buffer.enqueue("A")
    buffer.enqueue("B")
    buffer.enqueue("C")

    assert buffer.dequeue() == "A"

    buffer.enqueue("D")

    assert buffer.dequeue() == "B"
    assert buffer.dequeue() == "C"
    assert buffer.dequeue() == "D"


def test_full_buffer():
    buffer = RingBuffer(2)

    buffer.enqueue(1)
    buffer.enqueue(2)

    with pytest.raises(OverflowError):
        buffer.enqueue(3)


def test_empty_buffer():
    buffer = RingBuffer(2)

    with pytest.raises(IndexError):
        buffer.dequeue()


def test_is_empty_and_is_full():
    buffer = RingBuffer(2)

    assert buffer.is_empty()
    assert not buffer.is_full()

    buffer.enqueue(1)
    buffer.enqueue(2)

    assert buffer.is_full()
    assert not buffer.is_empty()


def test_length():
    buffer = RingBuffer(3)

    assert len(buffer) == 0

    buffer.enqueue(10)
    assert len(buffer) == 1

    buffer.dequeue()
    assert len(buffer) == 0


def test_invalid_capacity():
    with pytest.raises(ValueError):
        RingBuffer(0)

    with pytest.raises(ValueError):
        RingBuffer(-1)

    with pytest.raises(TypeError):
        RingBuffer(2.5)

    with pytest.raises(TypeError):
        RingBuffer(True)