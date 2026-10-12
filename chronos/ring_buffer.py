class RingBuffer:
    def __init__(self, capacity):
        if not isinstance(capacity, int) or isinstance(capacity, bool):
            raise TypeError("Capacity must be an integer")

        if capacity <= 0:
            raise ValueError("Capacity must be positive")

        self.capacity = capacity
        self.buffer = [None] * capacity
        self.head = 0
        self.tail = 0
        self.size = 0

    def enqueue(self, item):
        if self.size == self.capacity:
            raise OverflowError("Ring buffer is full")

        self.buffer[self.tail] = item
        self.tail = (self.tail + 1) % self.capacity
        self.size += 1

    def dequeue(self):
        if self.size == 0:
            raise IndexError("Ring buffer is empty")

        item = self.buffer[self.head]
        self.buffer[self.head] = None
        self.head = (self.head + 1) % self.capacity
        self.size -= 1

        return item

    def is_empty(self):
        return self.size == 0

    def is_full(self):
        return self.size == self.capacity

    def __len__(self):
        return self.size

    def __repr__(self):
        return (
            f"RingBuffer(capacity={self.capacity}, "
            f"size={self.size})"
        )