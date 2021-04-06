import matplotlib.pyplot as plt
import argparse
import os
import requests
from datetime import date
import pandas as pd

# Convert the 'real' time duration from time command output to seconds
def extract_build_time(in_time):
    time_in_min = int(in_time[0: in_time.index("m")])
    time_in_seconds = int(in_time[in_time.index("m") + 1: in_time.index(".")])
    total_time_seconds = time_in_seconds + time_in_min * 60

    print(f"Build time is {in_time}\n\
        Build time minutes {time_in_min} in seconds is {time_in_seconds}")

    return total_time_seconds

def prepare_data():
    parser = argparse.ArgumentParser()
    parser.add_argument('-vt', '--vt_time', help='VT lib build time', required=True)
    parser.add_argument('-te', '--tests_examples_time', help='Tests&Examples build time', required=True)
    parser.add_argument('-r', '--run_num', help='Run number', required=True)

    vt_build_time = parser.parse_args().vt_time
    tests_and_examples_build_time = parser.parse_args().tests_examples_time
    new_run_num = int(parser.parse_args().run_num)
    new_date = date.today().strftime("%d %B %Y")

    vt_total_time_seconds = extract_build_time(vt_build_time)
    tests_total_time_seconds = extract_build_time(tests_and_examples_build_time)

    PREVIOUS_BUILDS_FILENAME = os.getenv('INPUT_BUILD_TIMES_FILENAME')
    df = pd.read_csv(PREVIOUS_BUILDS_FILENAME)
    last_builds = df.tail(int(os.getenv('INPUT_NUM_LAST_BUILD')) - 1)
    updated = last_builds.append(pd.DataFrame(
        [[vt_total_time_seconds, tests_total_time_seconds, new_run_num, new_date]], columns=['vt', 'tests', 'run_num', 'date']))

    # Data to be plotted
    vt_timings = updated['vt'].tolist()
    tests_timings = updated['tests'].tolist()
    run_nums = updated['run_num'].tolist()
    dates = updated['date'].tolist()

    print(f"VT build times = {vt_timings}")
    print(f"Tests and examples build times = {tests_timings}")
    print(f"run nums = {run_nums}")

    last_n_runs = updated.shape[0]

    updated.to_csv(PREVIOUS_BUILDS_FILENAME, index=False)

    return vt_timings, tests_timings, run_nums, dates

def set_common_axis_data(iterable_axis):
    for ax in iterable_axis:
        ax.xaxis.get_major_locator().set_params(integer=True)
        ax.legend()
        ax.grid(True)
        ax.set_ylabel(os.getenv('INPUT_Y_LABEL'))

def generate_graph(vt, tests, run_nums, dates):
    SMALL_SIZE = 15
    MEDIUM_SIZE = 25
    BIGGER_SIZE = 35

    plt.rc('font', size=MEDIUM_SIZE, family='serif')
    plt.rc('axes', titlesize=MEDIUM_SIZE, labelsize=SMALL_SIZE)
    plt.rc('xtick', labelsize=SMALL_SIZE)
    plt.rc('ytick', labelsize=SMALL_SIZE)
    plt.rc('legend', fontsize=SMALL_SIZE)
    plt.rc('figure', titlesize=BIGGER_SIZE)

    GRAPH_WIDTH = float(os.getenv('INPUT_GRAPH_WIDTH'))
    GRAPH_HEIGHT = float(os.getenv('INPUT_GRAPH_HEIGHT'))

    # Times in CSV are stored in seconds, transform them to minutes for graph
    vt_timings = [x / 60 for x in vt]
    tests_timings = [x / 60 for x in tests]
    total_timings = [sum(x) for x in zip(vt_timings, tests_timings)]

    # plot
    fig, (ax1, ax2, ax3) = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT), nrows=3, ncols=1)

    ax1.set_title(f"{os.getenv('INPUT_TITLE')} ({dates[0]} - {dates[-1]})")
    plt.xlabel(os.getenv('INPUT_X_LABEL'))

    ax1.plot(run_nums, total_timings, color='b', marker='o', label='total')
    ax2.plot(run_nums, vt_timings, color='r', marker='s', label='vt-lib')
    ax3.plot(run_nums, tests_timings, color='g', marker='d', label='tests')

    set_common_axis_data([ax1, ax2, ax3])

    plt.savefig(os.getenv('INPUT_GRAPH_FILENAME'))


def generate_badge(vt, tests):
    average_time = (sum(vt) + sum(tests)) / len(vt)

    BUILD_TIME = vt[-1] + tests[-1]
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
    [vt, tests, run_nums, dates] = prepare_data()
    generate_graph(vt, tests, run_nums, dates)
    generate_badge(vt, tests)
