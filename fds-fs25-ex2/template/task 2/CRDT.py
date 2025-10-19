class CLS:

    def __init__(self):
        self.add_lst = []
        self.remove_lst = []

    def add(self, item: str):
        if item.upper() not in self.add_lst:
            self.add_lst.append(item.upper())
        if item.upper() in self.remove_lst:
            self.remove_lst.remove(item.upper())

    def remove(self, item: str):
        if item.upper() in self.add_lst:
            self.add_lst.remove(item.upper())
            self.remove_lst.append(item.upper())

    def mutual_sync(self, lst):        
        match lst:
            case [l]:
                for item in l.add_lst:
                    if item.upper() not in self.add_lst:
                        self.add_lst.append(item.upper())
                for item in l.remove_lst:
                    if item.upper() in self.add_lst:
                        self.add_lst.remove(item.upper())
                for item in self.remove_lst:
                    if item.upper() in self.add_lst:
                        self.add_lst.remove(item.upper())
                l.add_lst = self.add_lst.copy()
                self.remove_lst = []
                l.remove_lst = []

    def contains(self, item) -> bool:
        return item.upper() in self.add_lst

    def print(self):
        print([item for item in self.add_lst])

alice_list = CLS()
bob_list = CLS()

alice_list.add('Milk')
alice_list.add('Potato')
alice_list.add('Eggs')

bob_list.add('Sausage')
bob_list.add('Mustard')
bob_list.add('Coke')
bob_list.add('Potato')
bob_list.print()
bob_list.mutual_sync([alice_list])
bob_list.print()

alice_list.print()
alice_list.remove('Sausage')
alice_list.add('Tofu')
alice_list.remove('Potato')
alice_list.print()
print("Bob's list contains 'Potato' ?", bob_list.contains('Potato'))
alice_list.mutual_sync([bob_list])
bob_list.print()
print("Bob's list contains 'Potato' ?", bob_list.contains('Potato'))

