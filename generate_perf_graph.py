import os
from datetime import date
import matplotlib.pyplot as plt
import pandas as pd


GRAPH_WIDTH = 20
GRAPH_HEIGHT = 10
NUM_LAST_BUILDS = int(os.getenv("INPUT_NUM_LAST_BUILD", "30")) - 1
VT_BUILD_FOLDER = os.getenv("VT_BUILD_FOLDER", "/build/vt")
RUN_NUM = os.getenv("RUN_NUMBER")
DATE = date.today().strftime("%d %B %Y")
COMMIT_ID = os.getenv("GITHUB_SHA", "")


def generate_bar_graph_for_single_value(test_file_name, title, hisotry_title):
    time_df = pd.read_csv(f"{VT_BUILD_FOLDER}/tests/{test_file_name}.csv")

    _, ax_1 = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT))
    x_pos = range(len(time_df))

    ax_1.bar(
        x=x_pos,
        height=time_df["mean"],
        yerr=time_df["stdev"],
        align="center",
        alpha=0.7,
        ecolor="black",
        capsize=10,
    )

    plt.title(title)

    plt.xticks(x_pos, time_df["name"])
    plt.xlabel("")

    plt.ylabel("Time (ms)")
    plt.tight_layout()

    plt.savefig(f"{test_file_name}.png")

    time_df["commit"] = COMMIT_ID
    time_df["run_num"] = RUN_NUM

    file_path = f"{test_file_name}_history.csv"
    if os.path.exists(file_path):
        past_results = pd.read_csv(file_path)
    else:
        past_results = pd.DataFrame(columns=time_df.columns)
        past_results.to_csv(file_path, index=False)

    updated_results = pd.concat([past_results, time_df], ignore_index=True)
    updated_results.to_csv(file_path, index=False)

    last_n_results = updated_results.tail(NUM_LAST_BUILDS)

    _, ax_1 = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT))
    x_pos = range(len(last_n_results))

    ax_1.bar(
        x=x_pos,
        height=last_n_results["mean"],
        yerr=last_n_results["stdev"],
        align="center",
        alpha=0.7,
        ecolor="black",
        capsize=10,
    )

    plt.title(hisotry_title)

    plt.xticks(x_pos, last_n_results["run_num"])
    plt.xlabel("Run numbers")

    plt.ylabel("Time (ms)")
    plt.tight_layout()

    plt.savefig(f"{test_file_name}_history.png")


def ping_pong():
    time_df = pd.read_csv(f"{VT_BUILD_FOLDER}/tests/test_ping_pong_time.csv")

    # Split data by nodes
    num_nodes = time_df["node"].nunique()
    time_data = [time_df[time_df["node"] == node] for node in range(num_nodes)]

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
        bar_positions.append([x + bar_width for x in bar_positions[node - 1]])

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
    ax_1.set_yscale("log")

    # Customize y-ticks
    y_ticks = [0.03, 1, 5, 40]
    ax_1.set_yticks(y_ticks)
    ax_1.set_yticklabels([f"{y_tick:.2f} ms" for y_tick in y_ticks])
    ax_1.legend()

    plt.xticks(rotation=85)
    plt.tight_layout()

    plt.savefig("test_ping_pong_time.png")

    memory_df = pd.read_csv(f"{VT_BUILD_FOLDER}/tests/test_ping_pong_mem.csv")
    generate_memory_graph("ping_pong", memory_df)


def ping_pong_am():
    generate_bar_graph_for_single_value(
        "test_ping_pong_am_time",
        "Time for sending message (ping-pong) 1000 times",
        "Past runs of ping_pong_am",
    )


def make_runnable_micro():
    generate_bar_graph_for_single_value(
        "test_make_runnable_micro_time",
        "Time for calling makeRunnable 1000 times",
        "Past runs of make_runnable_micro",
    )


def objgroup_local_send():
    generate_bar_graph_for_single_value(
        "test_objgroup_local_send_time",
        "Time for ObjectGroup Local Send (1000 Iterations)",
        "Past runs of objgroup_local_send",
    )


def collection_local_send():
    # Read data
    time_df = pd.read_csv(
        f"{VT_BUILD_FOLDER}/tests/test_collection_local_send_time.csv"
    )
    time_prealloc_df = pd.read_csv(
        f"{VT_BUILD_FOLDER}/tests/test_collection_local_send_preallocate_time.csv"
    )

    time_df["name"] = "allocate"
    time_prealloc_df["name"] = "preallocate"

    combined_df = pd.concat([time_df, time_prealloc_df], axis=0)

    # Plot current data
    _, ax_1 = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT))
    x_pos = range(len(combined_df))

    ax_1.bar(
        x=x_pos,
        height=combined_df["mean"],
        yerr=combined_df["stdev"],
        align="center",
        alpha=0.7,
        ecolor="black",
        capsize=10,
    )
    plt.title("Time for Collection Local Send (1000 Iterations)")
    plt.xticks(x_pos, combined_df["name"])
    plt.xlabel("Type")
    plt.ylabel("Time (ms)")
    plt.tight_layout()
    plt.savefig("test_collection_local_send_time.png")

    # Create historic graph
    combined_df["commit"] = COMMIT_ID
    combined_df["run_num"] = RUN_NUM

    file_path = "test_collection_local_send_time_history.csv"
    if os.path.exists(file_path):
        past_results = pd.read_csv(file_path)
    else:
        past_results = pd.DataFrame(columns=combined_df.columns)

    # Append new results and save
    updated_results = pd.concat([past_results, combined_df], ignore_index=True)
    updated_results.to_csv(file_path, index=False)

    # Get last N results
    last_n_results = updated_results.tail(NUM_LAST_BUILDS)

    # Split data by type
    time_data = {
        "allocate": last_n_results[last_n_results["name"] == "allocate"],
        "preallocate": last_n_results[last_n_results["name"] == "preallocate"],
    }

    # Create the plot for historical data
    _, ax_1 = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT))
    ax_1.set_title("Past Runs of Collection Local Send")

    num_iter = list(range(len(time_data["allocate"])))
    bar_width = 0.4

    bar_positions = {
        "allocate": [i - bar_width / 2 for i in num_iter],
        "preallocate": [i + bar_width / 2 for i in num_iter],
    }

    for name in ["allocate", "preallocate"]:
        ax_1.bar(
            bar_positions[name],
            time_data[name]["mean"],
            yerr=time_data[name]["stdev"],
            label=f"{name}",
            width=bar_width,
            align="center",
            alpha=0.9,
            ecolor="black",
            capsize=5.0,
        )

    ax_1.grid(True, which="both", ls="--", linewidth=0.5)
    ax_1.set_xlabel("Run Number")
    ax_1.set_xticks(num_iter)
    ax_1.set_xticklabels(time_data["allocate"]["run_num"].astype(str))
    ax_1.set_ylabel("Time (ms)")
    ax_1.legend()
    plt.tight_layout()
    plt.savefig("test_collection_local_send_time_history.png")


def reduce():
    time_df = pd.read_csv(f"{VT_BUILD_FOLDER}/tests/test_reduce_time.csv")
    memory_df = pd.read_csv(f"{VT_BUILD_FOLDER}/tests/test_reduce_mem.csv")

    # Extract iteration number from 'name'
    time_df["iteration"] = time_df["name"].apply(lambda x: int(x.split()[0]))

    _, ax_1 = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT))
    for node in time_df["node"].unique():
        node_data = time_df[time_df["node"] == node]
        _, caps, bars = ax_1.errorbar(
            node_data["iteration"],
            node_data["mean"],
            yerr=node_data["stdev"],
            fmt="-",
            label=f"Node {node}",
        )

        # loop through bars and caps and set the alpha value
        for my_bar in bars:
            my_bar.set_alpha(0.3)
        for my_cap in caps:
            my_cap.set_alpha(0.3)

    ax_1.set_xlabel("Iteration")
    ax_1.set_ylabel("Time (ms)")
    ax_1.set_title("Reduce times over 100 iterations")
    ax_1.legend()
    plt.tight_layout()
    plt.savefig("test_reduce_time.png")

    generate_memory_graph("reduce", memory_df)


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

    num_nodes = memory_data["node"].max() + 1

    for node in range(num_nodes):
        node_data = memory_data[memory_data["node"] == node]
        num_iter = list(
            range(len(node_data))
        )  # Ensure num_iter matches the length of node_data

        ax1.plot(
            num_iter, node_data["mem"] / 1024 / 1024, label=f"Node {node}", linewidth=4
        )

    ax1.xaxis.get_major_locator().set_params(integer=True)
    ax1.legend()
    ax1.grid(True)

    plt.tight_layout()
    plt.savefig(f"test_{test_name}_mem.png")


if __name__ == "__main__":
    set_graph_properties()

    reduce()
    collection_local_send()
    objgroup_local_send()
    make_runnable_micro()
    ping_pong_am()
    ping_pong()
