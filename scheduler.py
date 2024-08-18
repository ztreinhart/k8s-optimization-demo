# from models import Pod, Node
from ortools.linear_solver import pywraplp



# schedule_pods_to_nodes will assign pods to nodes.
# It treats the scheduling problem as a bin-packing problem: minimize the number of bins (nodes) used to
# hold all the items (pods) without exceeding the capacity of a bin (memory and cpu).
# It conservatively uses the cpu_limit and memory_limit of each pod to make its scheduling decisions
def schedule_pods_to_nodes(pods, nodes, use_requests=False):
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Maximum number of nodes (worst case: one pod per node)
    max_nodes = len(nodes)

    # Decision variables
    pod_assigned_to_node = {}
    node_used = [solver.IntVar(0, 1, f'node_used_{j}') for j in range(max_nodes)]

    for i in range(len(pods)):
        for j in range(max_nodes):
            pod_assigned_to_node[i, j] = solver.IntVar(0, 1, f'pod_{i}_assigned_to_node_{j}')

    # Constraints
    # Each pod is placed on exactly one node
    for i in range(len(pods)):
        solver.Add(sum(pod_assigned_to_node[i, j] for j in range(max_nodes)) == 1)

    # Node capacity constraints
    for j, node in enumerate(nodes):
        if use_requests:
            # CPU capacity constraint (using cpu_request)
            solver.Add(sum(pod_assigned_to_node[i, j] * pods[i].cpu_request for i in range(len(pods))) <= node.cpu_capacity)
            # Memory capacity constraint (using memory_request)
            solver.Add(
                sum(pod_assigned_to_node[i, j] * pods[i].memory_request for i in range(len(pods))) <= node.memory_capacity)
        else:
            # CPU capacity constraint (using cpu_limit)
            solver.Add(sum(pod_assigned_to_node[i, j] * pods[i].cpu_limit for i in range(len(pods))) <= node.cpu_capacity)
            # Memory capacity constraint (using memory_limit)
            solver.Add(
                sum(pod_assigned_to_node[i, j] * pods[i].memory_limit for i in range(len(pods))) <= node.memory_capacity)

    # Link node usage to pod placement
    for j in range(max_nodes):
        solver.Add(node_used[j] >= sum(pod_assigned_to_node[i, j] for i in range(len(pods))) / len(pods))

    # Objective: Minimize the number of nodes used
    solver.Minimize(sum(node_used))

    # Solve
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        nodes_used = sum(node_used[j].solution_value() for j in range(max_nodes))
        placements = []
        for j in range(max_nodes):
            if node_used[j].solution_value() > 0:
                node_pods = []
                for i in range(len(pods)):
                    if pod_assigned_to_node[i, j].solution_value() > 0:
                        node_pods.append(pods[i])
                placements.append((nodes[j], node_pods))
        return nodes_used, placements
    else:
        return None

def print_scheduler_output(scheduler_result, verbose, use_requests=False):
    print()
    if scheduler_result:
        nodes_used, placements = scheduler_result
        print(f'Optimized Node Usage: {nodes_used:.0f}')
        if verbose:
            for node, node_pods in placements:
                print(f'Node: {node.name} (capacity: {node.cpu_capacity} CPU, {node.memory_capacity} Memory):')
                if use_requests:
                    print_requests(node, node_pods)
                else:
                    print_limits(node, node_pods)
        else:
            print()
            print('Pod to Node Mapping:')
            for node, node_pods in placements:
                print(f'- {node.name}: ', end='')
                print(*[pod.name for pod in node_pods], sep=', ')

    else:
        print('No solution found')

def print_limits(node, node_pods):
    total_cpu = sum(pod.cpu_limit for pod in node_pods)
    total_mem = sum(pod.memory_limit for pod in node_pods)
    for pod in node_pods:
        print(f'  Pod: {pod.name} (limits: {pod.cpu_limit} CPU, {pod.memory_limit} Memory)')
    print(f'  Total usage: {total_cpu}/{node.cpu_capacity} CPU, {total_mem}/{node.memory_capacity} Memory')

def print_requests(node, node_pods):
    total_cpu = sum(pod.cpu_request for pod in node_pods)
    total_mem = sum(pod.memory_request for pod in node_pods)
    for pod in node_pods:
        print(f'  Pod: {pod.name} (requests: {pod.cpu_request} CPU, {pod.memory_request} Memory)')
    print(f'  Total usage: {total_cpu}/{node.cpu_capacity} CPU, {total_mem}/{node.memory_capacity} Memory')