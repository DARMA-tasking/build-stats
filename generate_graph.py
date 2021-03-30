import matplotlib.pyplot as plt
import argparse
import os
import requests
from datetime import date
import pandas as pd

def prepare_data():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--time', help='Build time', required=True)
    parser.add_argument('-r', '--run_num', help='Run number', required=True)

    new_build_time = parser.parse_args().time
    new_run_num = int(parser.parse_args().run_num)
    new_date = date.today().strftime("%d %B %Y")

    time_in_min = int(new_build_time[0: new_build_time.index("m")])
    time_in_seconds = int(new_build_time[new_build_time.index("m") + 1: new_build_time.index(".")])
    total_time_seconds = time_in_seconds + time_in_min * 60

    print(f"Build time is {new_build_time} RUN_NUM is {new_run_num}\n\
        Build time minutes {time_in_min} in seconds is {time_in_seconds}")

    PREVIOUS_BUILDS_FILENAME = os.getenv('INPUT_BUILD_TIMES_FILENAME')
    df = pd.read_csv(PREVIOUS_BUILDS_FILENAME)
    last_builds = df.tail(int(os.getenv('INPUT_NUM_LAST_BUILD')) - 1)
    updated = last_builds.append(pd.DataFrame([[total_time_seconds, new_run_num, new_date]], columns=['time','run_num','date']))

    # Data to be plotted
    timings = updated['time'].tolist()
    run_nums = updated['run_num'].tolist()
    dates = updated['date'].tolist()

    print(f"build times = {timings}")
    print(f"run nums = {run_nums}")

    total_run_time = sum(timings)
    last_n_runs = updated.shape[0]

    updated.to_csv(PREVIOUS_BUILDS_FILENAME, index=False)

    return timings, run_nums, dates


def generate_graph(timings, run_nums, dates):
    SMALL_SIZE = 15
    MEDIUM_SIZE = 25
    BIGGER_SIZE = 35

    plt.rc('font', size=MEDIUM_SIZE, family='serif')
    plt.rc('axes', titlesize=BIGGER_SIZE, labelsize=MEDIUM_SIZE)
    plt.rc('xtick', labelsize=SMALL_SIZE)
    plt.rc('ytick', labelsize=SMALL_SIZE)
    plt.rc('legend', fontsize=SMALL_SIZE)
    plt.rc('figure', titlesize=BIGGER_SIZE)

    GRAPH_WIDTH = float(os.getenv('INPUT_GRAPH_WIDTH'))
    GRAPH_HEIGHT = float(os.getenv('INPUT_GRAPH_HEIGHT'))

    # Times in CSV are stored in seconds, transform them to minutes for graph
    timings = [x / 60 for x in timings]

    # plot
    fig, ax = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT))
    plt.plot(run_nums, timings, color='b', marker='o')
    plt.grid(True)

    fig.text(0.05,0.02, dates[0])
    fig.text(0.95,0.02, dates[-1], horizontalalignment='right')

    plt.title(os.getenv('INPUT_TITLE'))
    plt.xlabel(os.getenv('INPUT_X_LABEL'))
    plt.ylabel(os.getenv('INPUT_Y_LABEL'))

    plt.savefig(os.getenv('INPUT_GRAPH_FILENAME'))


def generate_badge(timings):
    average_time = sum(timings) / len(timings)

    BUILD_TIME = timings[-1]
    BADGE_COLOR = "brightgreen" if BUILD_TIME <= average_time else "red"
    title = os.getenv('INPUT_BADGE_TITLE').replace(" ", "%20")

    print(f"Last build time = {BUILD_TIME}seconds average build = {average_time}seconds color = {BADGE_COLOR}")
    url = f"https://img.shields.io/badge/{title}-{BUILD_TIME//60}%20min%20{BUILD_TIME%60}%20sec-{BADGE_COLOR}.svg"

    BADGE_LOGO = os.getenv('INPUT_BADGE_LOGO')
    if(len(BADGE_LOGO) > 0):
        url += f"?logo={BADGE_LOGO}"

    print(f"Downloading badge with URL = {url}")
    r = requests.get(url)

    open(os.getenv('INPUT_BADGE_FILENAME'), 'wb').write(r.content)

if __name__ == "__main__":
    [timings, run_nums, dates] = prepare_data()
    generate_graph(timings, run_nums, dates)
    generate_badge(timings)
