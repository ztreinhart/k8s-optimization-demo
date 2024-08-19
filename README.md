# Kubernetes Resource Optimization Demo

This repo contains a demonstration/proof-of-concept application for resource scheduling/optimization on Kubernetes.
This application will optimally schedule kubernetes pods onto nodes based on either resource limits (default) or requests (optional).

## Getting Started
Python 3.9 or better is required to run this applcation

Follow these steps to try it out:

- Clone this repository: `git clone https://github.com/ztreinhart/k8s-optimization-demo.git`
- Change into the repository directory: `cd k8s-optimization-demo`
- Make a new virtual environment: `python -m venv .venv`
- Activate the virtual environment: `source .venv/bin/activate` (command may vary based on your shell/OS)
- Install dependencies: `pip install -r requirements.txt`
- Run the demo with the sample input file `python main.py sample_input.json`

At this point, you should see output like this:

```shell
❯ python main.py sample_input.json
Number of pods: 10

Total CPU requests: 1340
Total CPU limits: 2680

Total Memory requests: 4352
Total Memory limits: 8704
```

By default, the program will just summarize the resource requests and limits from the pods in the input file. 
To run the demo with the scheduler enabled, add the `-s` flag to the command:

`python main.py -s sample_input.json`

Which will produce output like this:

```shell
❯ python main.py -s sample_input.json
Number of pods: 10

Total CPU requests: 1340
Total CPU limits: 2680

Total Memory requests: 4352
Total Memory limits: 8704

Optimized Node Usage: 2

Pod to Node Mapping:
- node4: pod1, pod2, pod3, pod5, pod6, pod9
- node5: pod4, pod7, pod8, pod10
```

If you'd like to see more information about the scheduled resources, you can add the `-v` (verbose) command line flag.

```shell
❯ python main.py -s -v sample_input.json
Number of pods: 10

Total CPU requests: 1340
Total CPU limits: 2680

Total Memory requests: 4352
Total Memory limits: 8704

Optimized Node Usage: 2
Node: node4 (capacity: 2000 CPU, 8192 Memory):
  Pod: pod1 (limits: 200 CPU, 512 Memory)
  Pod: pod2 (limits: 300 CPU, 1024 Memory)
  Pod: pod3 (limits: 400 CPU, 2048 Memory)
  Pod: pod5 (limits: 600 CPU, 1536 Memory)
  Pod: pod6 (limits: 160 CPU, 512 Memory)
  Pod: pod9 (limits: 220 CPU, 1024 Memory)
  Total usage: 1880/2000 CPU, 6656/8192 Memory
Node: node5 (capacity: 800 CPU, 2048 Memory):
  Pod: pod4 (limits: 100 CPU, 256 Memory)
  Pod: pod7 (limits: 240 CPU, 1024 Memory)
  Pod: pod8 (limits: 180 CPU, 256 Memory)
  Pod: pod10 (limits: 280 CPU, 512 Memory)
  Total usage: 800/800 CPU, 2048/2048 Memory
```

A simple help screen with an explanation of all command line flags is available with the `-h`:

```shell
❯ python main.py -h
usage: main.py [-h] [-s] [-v] [-r] input_file

positional arguments:
  input_file          Path to JSON input file

optional arguments:
  -h, --help          show this help message and exit
  -s, --schedule      Enable pod scheduling
  -v, --verbose       Show verbose scheduler output
  -r, --use_requests  Schedule pods based on requests instead of limits
```
## Documentation

### Input File
The input file is a JSON file that contains a description of the pods and nodes in a Kubernetes cluster.
Pod descriptions are stored as an array of objects under the key `pods`, with each object containing the name of the pod, its namespace, and its CPU and memory requests and limits.
Similarly, node descriptions are stored as an array of objects under the key `nodes`, with each object containing the name of the node and its CPU and memory capacity.

An example of this format is shown below:

```json
{
  "pods": [
    {"name": "pod1", "namespace": "default", "cpu_request": 100, "cpu_limit": 200, "memory_request": 256, "memory_limit": 512},
    {"name": "pod2", "namespace": "default", "cpu_request": 150, "cpu_limit": 300, "memory_request": 512, "memory_limit": 1024},
  ],
  "nodes": [
    {"name": "node1", "cpu_capacity": 1000, "memory_capacity": 2048},
  ]
}
```
A sample input file is given in the repo as `sample_input.json`

### Solution Strategy
This demo treats the resource allocation problem as a special case of the 1-D bin-packing problem.
The bin packing problem is a combinatorial optimization problem that seeks to pack a set of items each with a given weight into a series of bins each with a given capacity.
The optimal solution is the solution that uses the minimum number of bins to hold all of the items.
In this case, the nodes of the kubernetes cluster are considered to be bins, and the pods are considered to be items.
The cpu and memory resources required by each pod define the "weight" of the pod, and the cpu and memory capacity of the node define the capacity of the bin.

The bin packing problem is governed by three primary constraints in this case:

1. Each pod can be assigned to one and only one node 
2. The total memory consumed by the pods allocated to a node must be less than or equal to the memory capacity of the node.
3. The total CPU consumed by the pods allocated to a node must be less than or equal to the CPU capacity of the node.

By default, the CPU limit and memory limit for each pod are used to schedule the pods onto nodes. 
This is a conservative choice that will prevent CPU starvation or OOM kills even in more extreme circumstances.
However, it is worth noting that by default Kubernetes itself schedules based on resource requests, not limits. 
With that in mind, the demo has a command line flag to schedule based on resource requests instead of limits:

```shell
❯ python main.py -s -v --use_requests sample_input.json
Number of pods: 10

Total CPU requests: 1340
Total CPU limits: 2680

Total Memory requests: 4352
Total Memory limits: 8704

Optimized Node Usage: 1
Node: node4 (capacity: 2000 CPU, 8192 Memory):
  Pod: pod1 (requests: 100 CPU, 256 Memory)
  Pod: pod2 (requests: 150 CPU, 512 Memory)
  Pod: pod3 (requests: 200 CPU, 1024 Memory)
  Pod: pod4 (requests: 50 CPU, 128 Memory)
  Pod: pod5 (requests: 300 CPU, 768 Memory)
  Pod: pod6 (requests: 80 CPU, 256 Memory)
  Pod: pod7 (requests: 120 CPU, 512 Memory)
  Pod: pod8 (requests: 90 CPU, 128 Memory)
  Pod: pod9 (requests: 110 CPU, 512 Memory)
  Pod: pod10 (requests: 140 CPU, 256 Memory)
  Total usage: 1340/2000 CPU, 4352/8192 Memory
```

In this demo, the optimization problem is solved using the [OR Tools](https://developers.google.com/optimization) package from Google, a package that contains a variety of tools and highly-optimized solvers for combinatorial optimization problems such as the bin-packing problem.

### Future Work

In reality, the most optimal possible solution will depend on the actual behavior of the pods in question. 
If historical data on the resource consumption of the pods is available, the likely real-world resource usage of the pods could be predicted and used to optimally schedule them on the available nodes.

This strategy could also be extended with cost information for the available nodes. 
In this case, the optimization problem would become one of allocating the pods in such a way to minimize total cost instead of strictly minimizing the number of nodes (bins) used.

This demo assumes that the information about the pods and nodes is fully available before the solver is run.
This is known as the offline form of the bin-packing problem.
In the real world, however, new pods may be submitted to be scheduled at any time.
Fortunately, the analogy with the bin-packing problem is still apt, as there are online algorithms for solving the problem that can place items into bins (pods onto nodes) as they arrive without complete information.

