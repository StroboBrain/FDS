# simple test suit for the vector clock generator using pytest



import vector_clock as vc
import json

vector_clock_generator = vc.Vector_Clock_Generator()
data1 = json.load(open('data.json', 'r'))
data2 = json.load(open('dataPDF.json', 'r'))


def test_initialize():
    vector_clock_generator.load_data(data1)
    test = vector_clock_generator.get_vector_clocks_as_dic()
    expected = {'A1': {'A': 0, 'B': 0, 'C': 0, 'D': 0}, 'A2': {'A': 0, 'B': 0, 'C': 0, 'D': 0}, 'B1': {'A': 0, 'B': 0, 'C': 0, 'D': 0}, 'B2': {'A': 0, 'B': 0, 'C': 0, 'D': 0}, 'C1': {'A': 0, 'B': 0, 'C': 0, 'D': 0}, 'C2': {'A': 0, 'B': 0, 'C': 0, 'D': 0}, 'D1': {'A': 0, 'B': 0, 'C': 0, 'D': 0}, 'D2': {'A': 0, 'B': 0, 'C': 0, 'D': 0}}
    assert test == expected

    vector_clock_generator.load_data(data2)
    test = vector_clock_generator.get_vector_clocks_as_dic()
    expected = {'1111': {'B1': 0, 'B2': 0, 'B3': 0}, '12f3': {'B1': 0, 'B2': 0, 'B3': 0}, 'f432': {'B1': 0, 'B2': 0, 'B3': 0}, '2101': {'B1': 0, 'B2': 0, 'B3': 0}, '9634': {'B1': 0, 'B2': 0, 'B3': 0}, 'e13b': {'B1': 0, 'B2': 0, 'B3': 0}}
    assert test == expected

def test_value_change():
    vector_clock_generator.load_data(data1)
    vector_clock_generator.increase_vector_clock('A1', 'A')
    vector_clock_generator.increase_vector_clock('A1', 'A')
    vector_clock_generator.increase_vector_clock('A2', 'A')
    vector_clock_generator.increase_vector_clock('B1', 'B')
    vector_clock_generator.increase_vector_clock('C1', 'C')
    vector_clock_generator.increase_vector_clock('D1', 'D')
    vector_clock_generator.increase_vector_clock('D1', 'D')
    vector_clock_generator.increase_vector_clock('D2', 'D')
    test = vector_clock_generator.get_vector_clocks_as_dic()
    expected = {'A1': {'A': 2, 'B': 0, 'C': 0, 'D': 0}, 'A2': {'A': 1, 'B': 0, 'C': 0, 'D': 0}, 'B1': {'A': 0, 'B': 1, 'C': 0, 'D': 0}, 'B2': {'A': 0, 'B': 0, 'C': 0, 'D': 0}, 'C1': {'A': 0, 'B': 0, 'C': 1, 'D': 0}, 'C2': {'A': 0, 'B': 0, 'C': 0, 'D': 0}, 'D1': {'A': 0, 'B': 0, 'C': 0, 'D': 2}, 'D2': {'A': 0, 'B': 0, 'C': 0, 'D': 1}}
    assert test == expected

    vector_clock_generator._set_vector_clock('A1', 'B', 5)
    vector_clock_generator._set_vector_clock('B1', 'A', 3)
    test = vector_clock_generator.get_vector_clocks_as_dic()
    expected = {'A1': {'A': 2, 'B': 5, 'C': 0, 'D': 0}, 'A2': {'A': 1, 'B': 0, 'C': 0, 'D': 0}, 'B1': {'A': 3, 'B': 1, 'C': 0, 'D': 0}, 'B2': {'A': 0, 'B': 0, 'C': 0, 'D': 0}, 'C1': {'A': 0, 'B': 0, 'C': 1, 'D': 0}, 'C2': {'A': 0, 'B': 0, 'C': 0, 'D': 0}, 'D1': {'A': 0, 'B': 0, 'C': 0, 'D': 2}, 'D2': {'A': 0, 'B': 0, 'C': 0, 'D': 1}}