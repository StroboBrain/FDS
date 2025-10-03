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
