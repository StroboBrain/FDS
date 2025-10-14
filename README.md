# Exercise 1 — Execution Guide (Task 1 & Task 2)

Task 1:
requirements:
- python 3
- graphviz

Run the python file: python main.py and ensure the path is correct to the .json file.

expected outcome: pdf-file with graph.


Task 2:
requirements:
- python 3
- node.js
- packages: grpcio, grpcio-tools, protobuf

1. Start a Server with node dataServer.js (in folder dataServer)
2. Start a Hash Server with python server.py (in folder hashServer)
3. Start a client with python client.py (in folder client)

expected outcome: passcode, SHA256 Hashsum.
