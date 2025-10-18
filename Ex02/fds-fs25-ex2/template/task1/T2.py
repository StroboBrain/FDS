class CLS:
    #replica_id = alice or bob, if this is not given, we take the id of the object.
    #we then create a dict to store all future adds
    def __init__(self, replica_id=None):
        self.replica_id = replica_id if replica_id is not None else id(self)
        self.counter = 0
        self.adds = {}
        self.removes = set()

    #each tag gets a unique tag
    def _next_tag(self):
        self.counter += 1
        return (self.replica_id, self.counter)

    #create a tag for an item and if item is already present, we create multible tags for one item.
    def add(self, item):
        tag = self._next_tag()
        if item not in self.adds:
            self.adds[item] = set()
        self.adds[item].add(tag)

    #reove "adds" the current tags matching the remove in the removes list.
    def remove(self, item):
        if item in self.adds:
            self.removes.update(self.adds[item])

    #returns if some item is current or not
    def contains(self, item):
        if item not in self.adds:
            return False
        for tag in self.adds[item]:
            if tag not in self.removes:
                return True
        return False
    
    #merge 2 CLS (Causal length sets), so all adds and removes are merged. Get changes from ...
    def _merge_from(self, other):
        for item, tags in other.adds.items():
            if item not in self.adds:
                self.adds[item] = set()
            self.adds[item].update(tags)
        self.removes.update(other.removes)
        if isinstance(other.counter, int):
            self.counter = max(self.counter, other.counter)

    #update both lists. (merge both ways)
    def mutual_sync(self, peers):
        for p in peers:
            self._merge_from(p)
            p._merge_from(self)


alice_list = CLS()
bob_list = CLS()

alice_list.add('Milk')
alice_list.add('Potato')
alice_list.add('Eggs')

bob_list.add('Sausage')
bob_list.add('Mustard')
bob_list.add('Coke')
bob_list.add('Potato')

bob_list.mutual_sync([alice_list])

alice_list.remove('Sausage') #remove Tag Sausage
alice_list.add('Tofu')
alice_list.remove('Potato')

#bob_list.mutual_sync([alice_list])
alice_list.mutual_sync([bob_list])

print("Bob's list contains 'Potato' ?", bob_list.contains('Potato'))
