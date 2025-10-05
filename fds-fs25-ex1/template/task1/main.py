import json
import matplotlib.pyplot as plt
import networkx as nx


def causally_precedes(a: list, b: list) -> bool:
    if len(a) != len(b):
        raise Exception("Vector clock values must have same length")
    if a == b:  # non-reflexivity: commits must be different.
        return False
    for i in range(len(a)):
        if a[i] > b[i]:
            return False
    return True

# A commit a directly causally precedes another commit b if a causally
# precedes b, denoted a < b, and there doesn't exist a thrid commit
# c such that a < c and c < b.
def directly_causally_precedes(d: dict) -> bool:
    G = nx.DiGraph(directed=True)
    for k in d.keys():
        G.add_node(k)
    for k1 in d.keys():
        for k2 in d.keys():
            if causally_precedes(d[k1], d[k2]):
                dcp: bool = True
                for k3 in d.keys():
                    if causally_precedes(d[k1], d[k3]) and causally_precedes(d[k3], d[k2]):
                        dcp = False
                if dcp:
                    G.add_edge(k2, k1)
    pos = nx.spring_layout(G)
    nx.draw(G, pos=pos, with_labels=True)
    plt.show()                    
                    
if __name__ == '__main__':
    data = json.load(open('data.json', 'r'))
    # Determine the number of nodes
    n = len(data)
    # Instantiate dictionary and find root
    dct = {}
    branches = data.keys()
    to_process = []
    processed = []
    for i, b in enumerate(branches):
        for c in data[b].keys():
            dct[c] = [0] * n
            to_process += [c]
            if data[b][c] == []:
                dct[c][i] += 1
                root = c
                to_process.remove(c)
                processed += [c]
    while len(to_process) > 0:
        for i, b in enumerate(branches):
            for c in data[b].keys():
                if c in to_process and set(data[b][c]).issubset(processed):
                    for p in data[b][c]:
                        dct[c] = [max(dct[c][j],dct[p][j]) for j in range(n)]
                    dct[c][i] += 1
                    #print("processed: ", c)
                    to_process.remove(c)
                    processed += [c]

    
    G = nx.DiGraph(directed=True)
    for k in dct.keys():
        G.add_node(k)
    for k1 in dct.keys():
        for k2 in dct.keys():
            if causally_precedes(dct[k1],dct[k2]):
                G.add_edge(k2, k1)  # switch order of nodes
    pos = nx.spring_layout(G)
    nx.draw(G, pos=pos, with_labels=True)
    plt.show()

    directly_causally_precedes(dct)
    
