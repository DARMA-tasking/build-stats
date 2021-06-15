import matplotlib.pyplot as plt
import argparse
import os
from datetime import date
import pandas as pd

GRAPH_WIDTH = float(os.getenv('INPUT_GRAPH_WIDTH'))
GRAPH_HEIGHT = float(os.getenv('INPUT_GRAPH_HEIGHT'))

def prepare_data():
    """ Parse the input data, read CSV file and append it with the new results """

    parser = argparse.ArgumentParser()
    parser.add_argument('-time', '--time_test', help='Time-based results', required=True)
    parser.add_argument('-mem', '--memory_test', help='Memory usage', required=True)
    parser.add_argument('-r', '--run_num', help='Run number', required=True)

    time_test_file = parser.parse_args().time_test
    memory_test_file = parser.parse_args().memory_test

    time_df = pd.read_csv(time_test_file)
    memory_df = pd.read_csv(memory_test_file)

    num_nodes = memory_df["node"].max() + 1

    memory_data = list()
    time_data = list()
    for node in range(num_nodes):
        memory_data.append(memory_df.loc[memory_df["node"]==node])
        time_data.append(time_df.tail(-num_nodes).loc[time_df["node"]==node])

    new_run_num = int(parser.parse_args().run_num)
    new_date = date.today().strftime("%d %B %Y")
    commit_id = os.getenv('GITHUB_SHA')

    test_name = time_df["name"].loc[1]
    file_name = f'{test_name}_times.csv'
    if os.path.isfile(file_name):
        total_df = pd.read_csv(file_name)
        total_df = total_df.tail(int(os.getenv('INPUT_NUM_LAST_BUILD')) - 1)
        current = time_df.head(num_nodes)
        current['run_num'] = [new_run_num for node in range(num_nodes)]
        current['date'] = [new_date for node in range(num_nodes)]
        current['commit'] = [commit_id for node in range(num_nodes)]
        current = total_df.append(current)
    else:
        current = time_df.head(num_nodes)
        current['run_num'] = [new_run_num for node in range(num_nodes)]
        current['date'] = [new_date for node in range(num_nodes)]
        current['commit'] = [commit_id for node in range(num_nodes)]

    current.to_csv(file_name, index=False, float_format='%.3f')
    generate_historic_graph(test_name, num_nodes, current)

    return test_name, time_data, memory_data

def set_graph_properties():
    SMALL_SIZE = 15
    MEDIUM_SIZE = 25
    BIG_SIZE = 35

    plt.rc('font', size=MEDIUM_SIZE, family='serif')
    plt.rc('axes', titlesize=MEDIUM_SIZE, labelsize=MEDIUM_SIZE)
    plt.rc('xtick', labelsize=SMALL_SIZE)
    plt.rc('ytick', labelsize=MEDIUM_SIZE)
    plt.rc('legend', fontsize=SMALL_SIZE)
    plt.rc('figure', titlesize=BIG_SIZE)

def generate_time_graph(test_name, time_data):
    fig, ax1 = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT), nrows=1, ncols=1)
    ax1.set_title(f'{test_name} time results')

    num_nodes = len(time_data)

    num_iter = [i for i in range(len(time_data[0]))]
    barWidth = 1.0 / (2 * num_nodes)

    bar_positions = [[i - barWidth * (num_nodes / 2) + barWidth / 2 for i in num_iter]]

    for node in range(num_nodes - 1):
        bar_positions.append([x + barWidth for x in bar_positions[node]])

    for node in range(num_nodes):
        ax1.bar(bar_positions[node], time_data[node]["mean"], label=f'node {node}', width = barWidth)

    ax1.set_xticks(num_iter)

    time_list = time_data[0]["name"].tolist()
    off = time_list[0].rfind(" ") + 1

    ax1.set_xticklabels([i[:off] for i in time_list], rotation=85)
    ax1.set_xlabel(time_list[0][off:])
    ax1.set_ylabel("Time (ms)")
    ax1.legend()

    plt.tight_layout()

    plt.savefig(f'{test_name}_time.png')

def generate_memory_graph(test_name, memory_data):
    fig, ax1 = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT), nrows=1, ncols=1)

    ax1.set_title(f'{test_name} memory usage')
    plt.xlabel("Iteration")

    num_nodes = len(memory_data)
    num_iter = [i for i in range(len(memory_data[0]))]

    for node in range(num_nodes):
        ax1.plot(num_iter, memory_data[node]["mem"] / 1024 / 1024, label=f'node {node}', linewidth=4)

    ax1.xaxis.get_major_locator().set_params(integer=True)
    ax1.legend()
    ax1.grid(True)
    ax1.set_ylabel("Size (MiB)")

    plt.tight_layout()

    plt.savefig(f'{test_name}_memory.png')

def generate_historic_graph(test_name, num_nodes, dataframe):
    fig, ax1 = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT), nrows=1, ncols=1)

    ax1.set_title(f'{test_name} times')
    plt.xlabel("Run number")

    run_nums = pd.unique(dataframe["run_num"]).tolist()
    times = list()
    for node in range(num_nodes):
        times.append(dataframe["mean"].loc[dataframe["node"]==node].tolist())

    print(run_nums)
    print(times)
    for node in range(len(times)):
        ax1.plot(run_nums, times[node], linewidth=4)

    ax1.xaxis.get_major_locator().set_params(integer=True)
    ax1.legend()
    ax1.grid(True)
    ax1.set_ylabel("Time (ms)")

    plt.tight_layout()

    plt.savefig(f'{test_name}_past_runs.png')

if __name__ == "__main__":
    set_graph_properties()
    test_name, time_data, memory_data = prepare_data()
    generate_memory_graph(test_name, memory_data)
    generate_time_graph(test_name, time_data)
