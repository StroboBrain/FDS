import graphviz
g = graphviz.Digraph("hello", format="pdf")
g.edge("A", "B")
g.view()
