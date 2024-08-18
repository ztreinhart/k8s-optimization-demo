from pprint import pprint

from ortools.linear_solver import pywraplp


def create_data_model():
    """Create the data for the example."""
    data = {}
    cpu_requests = [200, 300, 400, 100, 600, 160, 240, 180, 220, 280]
    memory_requests = [512, 1024, 2048, 256, 1536, 512, 1024, 256, 1024, 512]
    assert len(cpu_requests) == len(memory_requests)
    data["cpu_weights"] = cpu_requests
    data["memory_weights"] = memory_requests
    data["items"] = list(range(len(cpu_requests)))
    data["bin_cpu_capacity"] = [1200, 2000, 800, 1000, 1500]
    data["bin_mem_capacity"] = [3072, 8192, 2048, 2048, 4096]
    assert len(data["bin_cpu_capacity"]) == len(data["bin_mem_capacity"])
    data["bins"] = list(range(len(data['bin_cpu_capacity'])))
    return data


def main():
    data = create_data_model()
    pprint(data)
    print('\n')

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        return

    # Variables
    # x[i, j] = 1 if item i is packed in bin j.
    x = {}
    for item in data["items"]:
        for bin_ in data["bins"]:
            x[(item, bin_)] = solver.IntVar(0, 1, f"x_{item}_{bin_}")

    # y[j] = 1 if bin j is used.
    y = {}
    for bin_ in data["bins"]:
        y[bin_] = solver.IntVar(0, 1, f"y[{bin_}]")

    # Constraints
    # Each item must be in exactly one bin.
    for item in data["items"]:
        # Each row in the x array indicates the location of an item. The sum of all entries in an item's row should be 1.
        solver.Add(sum(x[item, bin_] for bin_ in data["bins"]) == 1)

    # The amount packed in each bin cannot exceed its capacity.
    for bin_ in data["bins"]:
        # If you sum the weights of all the items in a column in the x array, it has to be less than or equal to the bin capacity
        solver.Add(
            # CPU capacity
            (sum(x[(item, bin_)] * data["cpu_weights"][item] for item in data["items"]) <= y[bin_] * data["bin_cpu_capacity"][bin_])
            and
            # Memory capacity
            (sum(x[(item, bin_)] * data["memory_weights"][item] for item in data["items"]) <= y[bin_] * data["bin_mem_capacity"][bin_])
        )
        # Memory capacity
        # solver.Add(
        # )

    # Objective: minimize the number of bins used.
    solver.Minimize(solver.Sum([y[j] for j in data["bins"]]))

    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        num_bins = 0
        for bin_ in data["bins"]:
            if y[bin_].solution_value() == 1:
                bin_items = []
                bin_cpu_weight = 0
                bin_mem_weight = 0
                for item in data["items"]:
                    if x[item, bin_].solution_value() > 0:
                        bin_items.append(item)
                        bin_cpu_weight += data["cpu_weights"][item]
                        bin_mem_weight += data["memory_weights"][item]
                if bin_items:
                    num_bins += 1
                    print("Bin number", bin_)
                    print("  Bin CPU capacity:", data["bin_cpu_capacity"][bin_])
                    print("  Bin memory capacity:", data["bin_mem_capacity"][bin_])
                    print("  Items packed:", bin_items)
                    print("  Total cpu weight:", bin_cpu_weight)
                    print("  Total memory weight:", bin_mem_weight)
                    print()
        print()
        print("Number of bins used:", num_bins)
        print("Time = ", solver.WallTime(), " milliseconds")
    else:
        print("The problem does not have an optimal solution.")


if __name__ == "__main__":
    main()
