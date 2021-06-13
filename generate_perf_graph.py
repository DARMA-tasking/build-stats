import matplotlib.pyplot as plt
import argparse
import os
from datetime import date
import pandas as pd

OUTPUT_DIR = os.getenv('INPUT_BUILD_STATS_OUTPUT')

def prepare_data():
    """ Parse the input data, read CSV file and append it with the new results """

    parser = argparse.ArgumentParser()
    parser.add_argument('-time', '--time_test', help='Time-based results', required=True)
    parser.add_argument('-mem', '--memory_test', help='Memory usage', required=True)

    time_test_file = parser.parse_args().time_test
    memory_test_file = parser.parse_args().memory_test

    time_df = pd.read_csv(time_test_file)
    memory_df = pd.read_csv(memory_test_file)

    num_nodes = memory_df["node"].max() + 1

    memory_data = list()
    time_data = list()
    for node in range(num_nodes):
        memory_data.append(memory_df.loc[memory_df["node"]==node])
        time_data.append(time_df.loc[time_df["node"]==node])

    return time_data, memory_data

def generate_time_graph(time_data):
    SMALL_SIZE = 15
    MEDIUM_SIZE = 25
    BIGGER_SIZE = 35

    plt.rc('font', size=MEDIUM_SIZE, family='serif')
    plt.rc('axes', titlesize=MEDIUM_SIZE, labelsize=MEDIUM_SIZE)
    plt.rc('xtick', labelsize=MEDIUM_SIZE)
    plt.rc('ytick', labelsize=MEDIUM_SIZE)
    plt.rc('legend', fontsize=MEDIUM_SIZE)
    plt.rc('figure', titlesize=BIGGER_SIZE)

    GRAPH_WIDTH = float(os.getenv('INPUT_GRAPH_WIDTH'))
    GRAPH_HEIGHT = float(os.getenv('INPUT_GRAPH_HEIGHT'))

    # plot
    fig, (ax1) = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT), nrows=1, ncols=1)

    num_nodes = len(time_data)

    num_iter = [i for i in range(len(time_data[0][1:]))]
    barWidth = 1.0 / (2 * num_nodes)
    bar_positions = [[i - barWidth * (num_nodes / 2) + barWidth / 2 for i in num_iter]]

    for node in range(num_nodes - 1):
        bar_positions.append([x + barWidth for x in bar_positions[node]])

    for node in range(num_nodes):
        ax1.bar(bar_positions[node], time_data[node]["mean"][1:], label=f'node {node}', width = barWidth)

    plt.xticks(num_iter, time_data[0]["name"][1:])

    ax1.legend()
    ax1.grid(True)
    ax1.set_ylabel("Time (ms)")
    plt.xticks(rotation=85)

    plt.tight_layout()

    plt.savefig(f'{memory_data[0]["name"].any()}_time.png')

def generate_memory_graph(memory_data):
    SMALL_SIZE = 15
    MEDIUM_SIZE = 25
    BIGGER_SIZE = 35

    plt.rc('font', size=MEDIUM_SIZE, family='serif')
    plt.rc('axes', titlesize=MEDIUM_SIZE, labelsize=MEDIUM_SIZE)
    plt.rc('xtick', labelsize=MEDIUM_SIZE)
    plt.rc('ytick', labelsize=MEDIUM_SIZE)
    plt.rc('legend', fontsize=MEDIUM_SIZE)
    plt.rc('figure', titlesize=BIGGER_SIZE)

    GRAPH_WIDTH = float(os.getenv('INPUT_GRAPH_WIDTH'))
    GRAPH_HEIGHT = float(os.getenv('INPUT_GRAPH_HEIGHT'))

    # plot
    fig, (ax1) = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT), nrows=1, ncols=1)

    ax1.set_title(f'{memory_data[0]["name"].any()} memory usage')
    plt.xlabel("Iteration")

    num_nodes = len(memory_data)
    num_iter = [i for i in range(len(memory_data[0]))]

    barWidth = 1.0 / (2 * num_nodes)
    bar_positions = [[i - barWidth * (num_nodes / 2) + barWidth / 2 for i in num_iter]]

    for node in range(num_nodes - 1):
        bar_positions.append([x + barWidth for x in bar_positions[node]])

    for node in range(num_nodes):
        ax1.bar(bar_positions[node], memory_data[node]["mem"], label=f'node {node}', width = barWidth)

    ax1.legend()
    ax1.grid(True)
    ax1.set_ylabel("Size (KiB)")

    plt.tight_layout()

    plt.savefig(f'{memory_data[0]["name"].any()}_memory.png')

if __name__ == "__main__":
    time_data, memory_data = prepare_data()
    generate_memory_graph(memory_data)
    generate_time_graph(time_data)
