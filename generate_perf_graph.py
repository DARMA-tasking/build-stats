import os
import argparse
from datetime import date
import matplotlib.pyplot as plt
import pandas as pd


GRAPH_WIDTH = 20
GRAPH_HEIGHT = 10
NUM_LAST_BUILDS = int(os.getenv("INPUT_NUM_LAST_BUILD", "30")) - 1
VT_BUILD_FOLDER = os.getenv("VT_BUILD_FOLDER", "/build/vt")

def generate_bar_graph_for_single_value(test_file_name, title):
    time_df = pd.read_csv(f"{VT_BUILD_FOLDER}/tests/{test_file_name}.csv")

    _, ax = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT))
    x_pos = range(len(time_df))

    ax.bar(x=x_pos, height=time_df['mean'], yerr=time_df['stdev'], align='center', alpha=0.7, ecolor='black', capsize=10)

    plt.title(title)

    plt.xticks(x_pos, time_df['name'])
    plt.xlabel("")

    plt.ylabel("Time (ms)")
    plt.tight_layout()

    plt.savefig(f"{test_file_name}.png")

def ping_pong():
    df = pd.read_csv(f"{VT_BUILD_FOLDER}/tests/test_ping_pong_time.csv")

    # Split data by nodes
    num_nodes = df['node'].nunique()
    time_data = [df[df["node"] == node] for node in range(num_nodes)]

    # Create the plot
    _, ax_1 = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT))
    ax_1.set_title("Bytes time results")

    num_iter = list(range(len(time_data[0])))
    bar_width = 1.0 / (2 * num_nodes)

    # Calculate bar positions for each node
    bar_positions = [
        [i - bar_width * (num_nodes / 2) + bar_width / 2 for i in num_iter]
    ]

    for node in range(1, num_nodes):
        bar_positions.append([x + bar_width for x in bar_positions[node-1]])

    for node in range(num_nodes):
        ax_1.bar(
            bar_positions[node],
            time_data[node]["mean"],
            yerr=time_data[node]["stdev"],
            label=f"node {node}",
            width=bar_width,
            align="center",
            alpha=0.9,
            ecolor="black",
            capsize=5.0,
        )

    ax_1.grid(True, which="both", ls="--", linewidth=0.5)

    # Set x-ticks and labels
    name_list = time_data[0]["name"].tolist()
    ax_1.set_xticks(num_iter)
    ax_1.set_xticklabels([i.split()[0] for i in name_list])
    ax_1.set_xlabel("Bytes")

    # Set y-axis label and scale
    ax_1.set_ylabel("Time (ms)")
    ax_1.set_yscale('log')

    # Customize y-ticks
    y_ticks = [0.03, 1, 5, 40]
    ax_1.set_yticks(y_ticks)
    ax_1.set_yticklabels([f"{y_tick:.2f} ms" for y_tick in y_ticks])
    ax_1.legend()

    plt.xticks(rotation=85)
    plt.tight_layout()

    plt.savefig("ping_pong_time.png")

    memory_df = pd.read_csv(f"{VT_BUILD_FOLDER}/tests/test_ping_pong_mem.csv")
    generate_memory_graph("ping_pong", memory_df)

def ping_pong_am():
    generate_bar_graph_for_single_value("test_ping_pong_am_time", "Time for sending message (ping-pong) 1000 times")

def make_runnable_micro():
    generate_bar_graph_for_single_value("test_make_runnable_micro_time", "Time for calling makeRunnable 1000 times")

def objgroup_local_send():
    generate_bar_graph_for_single_value("test_objgroup_local_send_time", "Time for ObjectGroup Local Send (1000 Iterations)")

def collection_local_send():
    time_df = pd.read_csv(f"{VT_BUILD_FOLDER}/tests/test_collection_local_send_time.csv")
    time_prealloc_df = pd.read_csv(f"{VT_BUILD_FOLDER}/tests/test_collection_local_send_preallocate_time.csv")

    time_df["name"] = "allocate"
    time_prealloc_df["name"] = "preallocate"

    combined_df = pd.concat([time_df, time_prealloc_df], axis=0)

    _, ax = plt.subplots()
    x_pos = range(len(combined_df))

    ax.bar(x=x_pos, height=combined_df['mean'], yerr=combined_df['stdev'], align='center', alpha=0.7, ecolor='black', capsize=10)

    plt.title("Time for Collection Local Send (1000 Iterations)")

    plt.xticks(x_pos, combined_df['name'])
    plt.xlabel("")

    plt.ylabel("Time (ms)")
    plt.tight_layout()

    plt.savefig("./test_collection_local_send_time.png")

def reduce():
    time_df = pd.read_csv(f"{VT_BUILD_FOLDER}/tests/test_reduce_time.csv")
    memory_df = pd.read_csv(f"{VT_BUILD_FOLDER}/tests/test_reduce_mem.csv")

    # Extract iteration number from 'name'
    time_df['iteration'] = time_df['name'].apply(lambda x: int(x.split()[0]))

    _, ax = plt.subplots()
    for node in time_df['node'].unique():
        node_data = time_df[time_df['node'] == node]
        _, caps, bars = ax.errorbar(node_data['iteration'], node_data['mean'], yerr=node_data['stdev'], fmt='-', label=f'Node {node}')

        # loop through bars and caps and set the alpha value
        [bar.set_alpha(0.3) for bar in bars]
        [cap.set_alpha(0.3) for cap in caps]

    ax.set_xlabel('Iteration')
    ax.set_ylabel('Time (ms)')
    ax.set_title('Reduce times over 100 iterations')
    ax.legend()
    plt.tight_layout()
    plt.savefig("test_reduce_time.png")

    generate_memory_graph("reduce", memory_df)

def prepare_data():
    """Parse the input data, read CSV file and append the new results"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-time", "--time_test", help="Time-based results", required=True
    )
    parser.add_argument("-mem", "--memory_test", help="Memory usage", required=True)
    parser.add_argument(
        "-r", "--run_num", help="Run number", required=False, type=int, default=0
    )
    parser.add_argument(
        "-wiki",
        "--wiki_dir",
        help="vt.wiki directory",
        required=False,
        type=str,
        default=".",
    )

    time_test_file = parser.parse_args().time_test
    memory_test_file = parser.parse_args().memory_test
    path_to_wiki = parser.parse_args().wiki_dir

    time_df = pd.read_csv(time_test_file)
    memory_df = pd.read_csv(memory_test_file)

    num_nodes = time_df["node"].max() + 1

    memory_data = []
    time_data = []
    for node in range(num_nodes):
        node_memory_data = memory_df.loc[memory_df["node"] == node]
        node_time_data = time_df.tail(-num_nodes).loc[time_df["node"] == node]

        if not node_memory_data.empty:
            memory_data.append(node_memory_data)

        if not node_time_data.empty:
            time_data.append(node_time_data)

    print(f"Memory: {memory_data}")
    print(f"Time: {time_data}")

    new_run_num = parser.parse_args().run_num
    new_date = date.today().strftime("%d %B %Y")
    commit_id = os.getenv("GITHUB_SHA", "")

    test_name = time_df["name"].loc[1]
    out_dir = f"{path_to_wiki}/perf_tests"
    file_name = f"{out_dir}/{test_name}_times.csv"

    current = time_df.head(num_nodes).copy()

    if os.path.isfile(file_name):
        total_df = pd.read_csv(file_name)
        total_df = total_df.tail(NUM_LAST_BUILDS * num_nodes)

        if new_run_num == 0:
            new_run_num = total_df["run_num"].iloc[-1] + 1

        for node in range(num_nodes):
            current.loc[current["node"] == node, "run_num"] = new_run_num
            current.loc[current["node"] == node, "date"] = new_date
            current.loc[current["node"] == node, "commit"] = commit_id
        current = pd.concat([total_df, current])
    else:
        for node in range(num_nodes):
            current.loc[current["node"] == node, "run_num"] = new_run_num
            current.loc[current["node"] == node, "date"] = new_date
            current.loc[current["node"] == node, "commit"] = commit_id

        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

    current.to_csv(file_name, index=False, float_format="%.3f")
    generate_historic_graph(test_name, num_nodes, current)

    return test_name, time_data, memory_data


def set_graph_properties():
    small_size = 15
    medium_size = 25
    big_size = 35

    plt.rc("font", size=medium_size, family="serif")
    plt.rc("axes", titlesize=medium_size, labelsize=medium_size)
    plt.rc("xtick", labelsize=small_size)
    plt.rc("ytick", labelsize=medium_size)
    plt.rc("legend", fontsize=small_size)
    plt.rc("figure", titlesize=big_size)

def generate_memory_graph(test_name, memory_data):
    _, ax1 = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT))

    ax1.set_title(f"{test_name} Memory Usage")
    plt.xlabel("Iteration")
    plt.ylabel("Size (MiB)")

    num_nodes = memory_data['node'].max() + 1

    for node in range(num_nodes):
        node_data = memory_data[memory_data['node'] == node]
        num_iter = list(range(len(node_data)))  # Ensure num_iter matches the length of node_data

        ax1.plot(
            num_iter,
            node_data['mem'] / 1024 / 1024,
            label=f"Node {node}",
            linewidth=4
        )

    ax1.xaxis.get_major_locator().set_params(integer=True)
    ax1.legend()
    ax1.grid(True)

    plt.tight_layout()
    plt.savefig(f"{test_name}_memory.png")


def generate_historic_graph(test_name, num_nodes, dataframe):
    _, ax1 = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT), nrows=1, ncols=1)

    ax1.set_title(f"{test_name} run history")
    plt.xlabel("Run number")

    run_nums = pd.unique(dataframe["run_num"]).tolist()
    times = []
    errors = []
    for node in range(num_nodes):
        times.append(dataframe["mean"].loc[dataframe["node"] == node].tolist())
        errors.append(dataframe["stdev"].loc[dataframe["node"] == node].tolist())

    print(f"generate_historic_graph::times: {times}")
    print(f"generate_historic_graph::errors: {errors}")

    bar_width = 1.0 / (2 * num_nodes)

    bar_positions = [
        [i - bar_width * (num_nodes / 2) + bar_width / 2 for i in run_nums]
    ]

    for node in range(num_nodes - 1):
        bar_positions.append([x + bar_width for x in bar_positions[node]])

    for node in range(num_nodes):
        ax1.bar(
            bar_positions[node],
            times[node],
            yerr=errors[node],
            label=f"node {node}",
            width=bar_width,
            align="center",
            alpha=0.9,
            ecolor="black",
            capsize=5.0,
        )

    ax1.xaxis.get_major_locator().set_params(integer=True)
    ax1.legend()
    ax1.grid(True)
    ax1.set_ylabel("Time (ms)")

    plt.tight_layout()

    plt.savefig(f"{test_name}_past_runs.png")


if __name__ == "__main__":
    set_graph_properties()

    reduce()
    collection_local_send()
    objgroup_local_send()
    make_runnable_micro()
    ping_pong_am()
    ping_pong()

