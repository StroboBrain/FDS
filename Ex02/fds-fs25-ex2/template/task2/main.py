from cls_module import CLS

# example from the excercise
def main():
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

    alice_list.remove('Sausage')
    alice_list.add('Tofu')
    alice_list.remove('Potato')

    alice_list.mutual_sync([bob_list])

    print("Bob’s list contains ‘Potato’? ", bob_list.contains('Potato'))

if __name__ == "__main__":
    main()