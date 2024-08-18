pod_keys = ["name", "namespace", "cpu_request", "cpu_limit", "memory_request", "memory_limit"]
node_keys = ["name", "cpu_capacity", "memory_capacity"]

class Pod:
    def __init__(self, name="", namespace="", cpu_request=0, cpu_limit=0, memory_request=0, memory_limit=0):
        self.name = name
        self.namespace = namespace
        self.cpu_request = cpu_request
        self.cpu_limit = cpu_limit
        self.memory_request = memory_request
        self.memory_limit = memory_limit

class Node:
    def __init__(self, name="", cpu_capacity=0, memory_capacity=0):
        self.name = name
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity

def pod_node_decoder(obj):
    if type(obj) == dict:
        keys_set = set(obj.keys())
        if keys_set == set(pod_keys):
            return Pod(obj['name'], obj['namespace'], obj['cpu_request'], obj['cpu_limit'], obj['memory_request'],obj['memory_limit'])
        elif keys_set == set(node_keys):
            return Node(obj['name'], obj['cpu_capacity'], obj['memory_capacity'])
        else:
            return obj
    return obj
