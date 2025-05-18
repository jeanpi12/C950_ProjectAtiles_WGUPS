# hash_table.py
"""
Hash Table
Implements a simple hash table using linear probing to store Package objects.
"""

class HashTable:
    def __init__(self, capacity=40):
        self.capacity = capacity
        self.table = [None] * capacity
        self.status = ["EMPTY"] * capacity

    def _hash(self, key):
        return key % self.capacity

    def insert(self, key, value):
        index = self._hash(key)
        start_index = index
        while True:
            if self.status[index] in ("EMPTY", "REMOVED"):
                self.table[index] = (key, value)
                self.status[index] = "OCCUPIED"
                return
            else:
                stored_key, _ = self.table[index]
                if stored_key == key:
                    self.table[index] = (key, value)
                    return
            index = (index + 1) % self.capacity
            if index == start_index:
                raise Exception("Hash table is full.")

    def lookup(self, key):
        index = self._hash(key)
        start_index = index
        while self.status[index] != "EMPTY":
            if self.status[index] == "OCCUPIED":
                stored_key, stored_value = self.table[index]
                if stored_key == key:
                    return stored_value
            index = (index + 1) % self.capacity
            if index == start_index:
                break
        return None
