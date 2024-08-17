import argparse
import json

# Set up command line arguments
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('input_file', help='Path to JSON input file')
args = arg_parser.parse_args()

# Dictionary for our parsed data
data = dict()

# Open the file and load its contents as JSON
try:
    with open(args.input_file, 'r') as file:
        data = json.load(file)

except FileNotFoundError:
    print(f"Error: File '{args.input_file}' not found.")
except json.JSONDecodeError:
    print(f"Error: File '{args.input_file}' contains invalid JSON.")
except Exception as e:
    print(f"An error occurred: {str(e)}")

# Summarize pod data
print(f"Number of pods: {len(data['pods'])}\n")

total_CPU_reqs = 0
total_CPU_limits = 0
total_mem_reqs = 0
total_mem_limits = 0

for pod in data['pods']:
    total_CPU_reqs += pod['cpu_request']
    total_CPU_limits += pod['cpu_limit']
    total_mem_reqs += pod['memory_request']
    total_mem_limits += pod['memory_limit']

print(f"Total CPU requests: {total_CPU_reqs}")
print(f"Total CPU limits: {total_CPU_limits}\n")
print(f"Total Memory requests: {total_mem_reqs}")
print(f"Total Memory limits: {total_mem_limits}")
