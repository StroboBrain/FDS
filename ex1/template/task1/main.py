import json
import graphviz

def findStartingNode(data):
    for groups, nodes in data.items():
        for node, neighbours in nodes.items():
            if neighbours == []:
                return node

def createResultDict(data):
    size = len(data)
    for element in data.keys():
        for node in data[element]:
            result_dict[node] = [0]*size

def findParents(target, data):
    index = 0
    parentList = []
    for group, nodes in data.items():
        for node, neighbours in nodes.items():
            if target in neighbours:
                parentList.append(node)
        index += 1
    return parentList
        
def determineVisitOrder(data):
    topologicalOrder = []
    index = 0
    topologicalOrder.append(findStartingNode(data))
    while index < len(topologicalOrder):
        neighboursOfTarget = findParents(topologicalOrder[index], data)
        for node in neighboursOfTarget:
            if node in topologicalOrder:
                topologicalOrder.remove(node)
                topologicalOrder.append(node)
            else:
                topologicalOrder.append(node)
        index += 1
    return(topologicalOrder)

def getChildrenVC(children):
    childrenVectorClocks = []
    for node in children:
        childrenVectorClocks.append(result_dict.get(node))
    return childrenVectorClocks

def findChildren(target, data):
    children = []
    children.append(target)
    for values in data.values():
        if target in values.keys():
            return values[target] + children

def incrementCurrentGroupVC(target, data):
    position = 0
    for values in data.values():
        if target in values.keys():
            break
        else:
            position+=1
    result_dict[target][position] += 1
    return

def elementwiseMax(lists):
    return [max(col) for col in zip(*lists)]

def calculateVectorClock(topologicalOrder):
    for node in topologicalOrder:
        children = findChildren(node, data)
        #increment current group
        #get Vector Clock from children
        childrenVectorClocks = getChildrenVC(children)
        result_dict[node] = elementwiseMax(childrenVectorClocks)
        incrementCurrentGroupVC(node, data)

def causally_precedes(a, b):
    for ai, bi in zip(a, b):
        if ai > bi:
            return False
    return True

def drawGraph():
    g = graphviz.Digraph("G", filename = "VectorClock.gv")
    for nodes in result_dict:
        print("hello")


if __name__ == '__main__':
    data = json.load(open(r'template\task1\data1.json', 'r'))

    #create the dictonary with the right format ({'A1': [0, 0, 0, 0], 'A2': [0, 0, 0, 0],...)
    result_dict = {}
    createResultDict(data)

    #find the starting node and determine parents of Starting node
    findParents(findStartingNode(data), data)

    #determine order to visit nodes: Child before parent order
    topologicalOrder = determineVisitOrder(data)

    #calculate Vector clock from the topologicalOrder
    calculateVectorClock(topologicalOrder)
    out_path = r'template\task1/result1.json'
    with open(out_path, 'w') as f:
        json.dump(result_dict, f)

    vals = list(result_dict.values())
    for x in range(5):
        print(causally_precedes(vals[x], vals[x+1]))
    