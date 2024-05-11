from flask import Flask, request, jsonify

app = Flask(__name__)

class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.head = None
        self.tail = None

    def _remove_node(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

    def _add_to_head(self, node):
        node.next = self.head
        node.prev = None
        if self.head:
            self.head.prev = node
        self.head = node
        if not self.tail:
            self.tail = node

    def put(self, key, value):
        if key in self.cache:
            self.cache[key].value = value
            self._remove_node(self.cache[key])
        elif len(self.cache) >= self.capacity:
            del self.cache[self.tail.key]
            self._remove_node(self.tail)
        new_node = Node(key, value)
        self._add_to_head(new_node)
        self.cache[key] = new_node

    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            self._remove_node(node)
            self._add_to_head(node)
            return node.value
        else:
            return None

# Dictionary to store collections, where key is the collection name and value is an LRUCache instance
collections = {}

@app.route("/create_collection", methods=["POST"])
def create_collection():
    data = request.get_json()
    collection_name = data.get("name")
    capacity = data.get("capacity", 10)  # default capacity is 10
    if collection_name in collections:
        return jsonify({"error": "Collection already exists"}), 400
    collections[collection_name] = LRUCache(capacity)
    return jsonify({"message": f"Collection {collection_name} created"}), 200

@app.route("/update_capacity", methods=["PUT"])
def update_capacity():
    data = request.get_json()
    collection_name = data.get("name")
    capacity = data.get("capacity")
    if collection_name not in collections:
        return jsonify({"error": "Collection does not exist"}), 404
    collections[collection_name].capacity = capacity
    return jsonify({"message": f"Capacity of collection {collection_name} updated"}), 200

@app.route("/put_data", methods=["POST"])
def put_data():
    data = request.get_json()
    collection_name = data.get("collection")
    key = data.get("key")
    value = data.get("value")
    if collection_name not in collections:
        return jsonify({"error": "Collection does not exist"}), 404
    collections[collection_name].put(key, value)
    return jsonify({"message": "Data added successfully"}), 200

@app.route("/get_data", methods=["GET"])
def get_data():
    collection_name = request.args.get("collection")
    key = request.args.get("key")
    if collection_name not in collections:
        return jsonify({"error": "Collection does not exist"}), 404
    value = collections[collection_name].get(key)
    if value is None:
        return jsonify({"error": "Key not found"}), 404
    return jsonify({"value": value}), 200

if __name__ == "__main__":
    app.run(debug=True)
