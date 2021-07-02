import os
from collections import defaultdict
import argparse
from datetime import date
import matplotlib.pyplot as plt
import pandas as pd


GRAPH_WIDTH = 20
GRAPH_HEIGHT = 10
NUM_LAST_BUILDS = int(os.getenv("INPUT_NUM_LAST_BUILD", "30")) - 1


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

    num_nodes = memory_df["node"].max() + 1

    memory_data = list()
    time_data = list()
    for node in range(num_nodes):
        memory_data.append(memory_df.loc[memory_df["node"] == node])
        time_data.append(time_df.tail(-num_nodes).loc[time_df["node"] == node])

    print(f"Memory: {memory_data}")

    new_run_num = parser.parse_args().run_num
    new_date = date.today().strftime("%d %B %Y")
    commit_id = os.getenv("GITHUB_SHA", "")

    test_name = time_df["name"].loc[1]
    out_dir = f"{path_to_wiki}/perf_tests"
    file_name = f"{out_dir}/{test_name}_times.csv"

    if os.path.isfile(file_name):
        total_df = pd.read_csv(file_name)
        total_df = total_df.tail(NUM_LAST_BUILDS)
        current = time_df.head(num_nodes)

        if new_run_num == 0:
            new_run_num = total_df["run_num"].iloc[-1] + 1

        current["run_num"] = [new_run_num for node in range(num_nodes)]
        current["date"] = [new_date for node in range(num_nodes)]
        current["commit"] = [commit_id for node in range(num_nodes)]
        current = total_df.append(current)
    else:
        current = time_df.head(num_nodes)
        current["run_num"] = [new_run_num for node in range(num_nodes)]
        current["date"] = [new_date for node in range(num_nodes)]
        current["commit"] = [commit_id for node in range(num_nodes)]

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


def generate_time_graph(main_test_name, time_data):
    num_nodes = len(time_data)

    all_names = time_data[0]["name"].tolist()
    test_names = {name[name.find(" ") + 1 :] for name in all_names}

    per_test_dict = defaultdict(dict)
    for test_name in test_names:
        for node in range(num_nodes):
            per_test_dict.setdefault(test_name, []).append(
                time_data[node][time_data[node]["name"].str.endswith(test_name)]
            )

    for key, value in per_test_dict.items():
        _, ax_1 = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT), nrows=1, ncols=1)
        ax_1.set_title(f"{key} time results")

        num_iter = list(range(len(value[0])))
        bar_width = 1.0 / (2 * num_nodes)

        bar_positions = [
            [i - bar_width * (num_nodes / 2) + bar_width / 2 for i in num_iter]
        ]

        for node in range(num_nodes - 1):
            bar_positions.append([x + bar_width for x in bar_positions[node]])

        for node in range(num_nodes):
            ax_1.bar(
                bar_positions[node],
                value[node]["mean"],
                yerr=value[node]["stdev"],
                label=f"node {node}",
                width=bar_width,
                align="center",
                alpha=0.9,
                ecolor="black",
                capsize=5.0,
            )

        if len(num_iter) == 1:
            ax_1.set_xticks([])
        else:
            ax_1.set_xticks(num_iter)

        if len(value[0]) > 1:
            name_list = value[0]["name"].tolist()
            ax_1.set_xticklabels([i[: i.rfind(key)] for i in name_list])
            ax_1.set_xlabel(key)

        ax_1.set_xlabel(key)
        ax_1.set_ylabel("Time (ms)")
        ax_1.legend()

        plt.xticks(rotation=85)

        plt.tight_layout()

        plt.savefig(f"{main_test_name}_{key}_time.png")


def generate_memory_graph(test_name, memory_data):
    _, ax1 = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT), nrows=1, ncols=1)

    ax1.set_title(f"{test_name} memory usage")
    plt.xlabel("Iteration")

    num_nodes = len(memory_data)
    num_iter = list(range(len(memory_data[0])))

    for node in range(num_nodes):
        ax1.plot(
            num_iter,
            memory_data[node]["mem"] / 1024 / 1024,
            label=f"node {node}",
            linewidth=4,
        )

    ax1.xaxis.get_major_locator().set_params(integer=True)
    ax1.legend()
    ax1.grid(True)
    ax1.set_ylabel("Size (MiB)")

    plt.tight_layout()

    plt.savefig(f"{test_name}_memory.png")


def generate_historic_graph(test_name, num_nodes, dataframe):
    _, ax1 = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT), nrows=1, ncols=1)

    ax1.set_title(f"{test_name} run history")
    plt.xlabel("Run number")

    run_nums = pd.unique(dataframe["run_num"]).tolist()
    times = list()
    errors = list()
    for node in range(num_nodes):
        times.append(dataframe["mean"].loc[dataframe["node"] == node].tolist())
        errors.append(dataframe["stdev"].loc[dataframe["node"] == node].tolist())

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
            yerr=errors,
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
    test_name_in, time_data_in, memory_data_in = prepare_data()
    generate_memory_graph(test_name_in, memory_data_in)
    generate_time_graph(test_name_in, time_data_in)
