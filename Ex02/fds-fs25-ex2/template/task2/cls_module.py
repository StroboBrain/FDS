from collections import Counter

class CLS:
    def __init__(self):
        self.added = Counter()
        self.removed = Counter()
    
    def add(self, word):
        self.added[word] += 1

    def remove(self, word):
        self.removed[word] += 1
    
    def set_added(self, counter):
        self.added = counter
    
    def set_removed(self,counter):
        self.removed(self,counter)
    
    def get_added(self):
        return self.added
    
    def get_removed(self):
        return self.removed

    def merge(self, other):
        for w, count in other.get_added().items():
            self.added[w] += count
        
        for w, count in other.get_removed().items():
            self.removed[w] += count

    def contains(self, word):
        return self.added[word] > self.removed[word]

    def mutual_sync(self, others):
        for other in others:
            self.merge(other)
            other = self
