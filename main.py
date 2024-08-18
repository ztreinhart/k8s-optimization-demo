import argparse
import json
import models
import scheduler


# parse_cli_args will parse the CLI arguments and return the ones we need individually.
def parse_cli_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('input_file', help='Path to JSON input file')
    arg_parser.add_argument('-s', '--schedule', action='store_true', help='Enable pod scheduling')
    arg_parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose scheduler output')
    arg_parser.add_argument('--use_requests', action='store_true', help='Schedule pods based on requests instead of limits')
    args = arg_parser.parse_args()
    return args.input_file, args.schedule, args.verbose, args.use_requests

# load_input_file will load the JSON file specified by filename. It utilizes models.pod_node_decoder
# to parse the input data into a list of Pods and a list of Nodes.
def load_input_file(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file, object_hook=models.pod_node_decoder)
            return data['pods'], data['nodes']
    except FileNotFoundError:
        print(f'Error: File "{filename}" not found.')
        exit(1)
    except json.JSONDecodeError:
        print(f'Error: File "{filename}" contains invalid JSON.')
        exit(1)
    except Exception as e:
        print(f'An error occurred: {str(e)}')
        exit(1)


# print_pod_summary will print a summary of the list of pods passed to it onto the console
def print_pod_summary(pods):
    print(f'Number of pods: {len(pods)}\n')

    total_CPU_reqs = 0
    total_CPU_limits = 0
    total_mem_reqs = 0
    total_mem_limits = 0

    for pod in pods:
        total_CPU_reqs += pod.cpu_request
        total_CPU_limits += pod.cpu_limit
        total_mem_reqs += pod.memory_request
        total_mem_limits += pod.memory_limit

    print(f'Total CPU requests: {total_CPU_reqs}')
    print(f'Total CPU limits: {total_CPU_limits}')
    print()
    print(f'Total Memory requests: {total_mem_reqs}')
    print(f'Total Memory limits: {total_mem_limits}')

def main():
    # Parse the command line arguments to the input file name
    input_file, schedule, verbose, use_requests = parse_cli_args()

    # Load and parse the input file
    pods, nodes = load_input_file(input_file)

    # Print the pod summary
    print_pod_summary(pods)

    # If the 'schedule' flag has been set, run the scheduler
    if schedule:
        result = scheduler.schedule_pods_to_nodes(pods, nodes, use_requests)
        scheduler.print_scheduler_output(result, verbose, use_requests)

if __name__ == '__main__':
    main()
