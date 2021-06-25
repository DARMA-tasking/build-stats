import argparse
from datetime import date
import os
import matplotlib.pyplot as plt
import requests
import pandas as pd

OUTPUT_DIR = os.getenv("INPUT_BUILD_STATS_OUTPUT")


def extract_build_time(in_time):
    """
    Convert the duration from linux's time command format to seconds

    Example input: 07m44.068s
    Output: 464
    """

    time_in_min = int(in_time[0 : in_time.index("m")])
    time_in_seconds = int(in_time[in_time.index("m") + 1 : in_time.index(".")])
    total_time_seconds = time_in_seconds + time_in_min * 60

    print(
        f"Build time is {in_time}\n\
        Build time minutes {time_in_min} in seconds is {time_in_seconds}"
    )

    return total_time_seconds


def prepare_data():
    """Parse the input data, read CSV file and append the new results"""

    parser = argparse.ArgumentParser()
    parser.add_argument("-vt", "--vt_time", help="VT lib build time", required=True)
    parser.add_argument(
        "-te", "--tests_examples_time", help="Tests&Examples build time", required=True
    )
    parser.add_argument("-r", "--run_num", help="Run number", required=True)

    vt_build_time = parser.parse_args().vt_time
    tests_and_examples_build_time = parser.parse_args().tests_examples_time
    new_run_num = int(parser.parse_args().run_num)
    new_date = date.today().strftime("%d %B %Y")

    commit_id = os.getenv("GITHUB_SHA")

    vt_total_time_seconds = extract_build_time(vt_build_time)
    tests_total_time_seconds = extract_build_time(tests_and_examples_build_time)

    file_name = os.getenv("INPUT_BUILD_TIMES_FILENAME")
    previous_builds_filename = f"{OUTPUT_DIR}/{file_name}"

    data_frame = pd.read_csv(previous_builds_filename)
    last_builds = data_frame.tail(int(os.getenv("INPUT_NUM_LAST_BUILD")) - 1)
    updated = last_builds.append(
        pd.DataFrame(
            [
                [
                    vt_total_time_seconds,
                    tests_total_time_seconds,
                    new_run_num,
                    new_date,
                    commit_id,
                ]
            ],
            columns=["vt", "tests", "run_num", "date", "commit"],
        )
    )

    # Data to be plotted
    vt_timings = updated["vt"].tolist()
    tests_timings = updated["tests"].tolist()
    run_nums = updated["run_num"].tolist()
    dates = updated["date"].tolist()
    commits = updated["commit"].tolist()

    print(f"VT build times = {vt_timings}")
    print(f"Tests and examples build times = {tests_timings}")
    print(f"run nums = {run_nums}")
    print(f"commits = {commits}")

    updated.to_csv(previous_builds_filename, index=False)

    return vt_timings, tests_timings, run_nums, dates


def set_common_axis_data(iterable_axis):
    for axis in iterable_axis:
        axis.xaxis.get_major_locator().set_params(integer=True)
        axis.legend()
        axis.grid(True)
        axis.set_ylabel(os.getenv("INPUT_Y_LABEL"))


def annotate(axis, x_list, y_list):
    """Annotate build time graph with percentage change between
    current build time and the previous one."""

    avg_y = sum(y_list) / len(y_list)

    previous_value = y_list[-2]
    current_value = y_list[-1]

    percentage_diff = round(((current_value - previous_value) / previous_value) * 100.0)
    color = "red" if percentage_diff > 0 else "green"
    x_pos = x_list[-1] + (x_list[-1] / 100.0)

    y_offset = avg_y / 100.0
    if current_value > avg_y:
        y_pos = current_value - y_offset
    else:
        y_pos = current_value + y_offset

    text = f"+{percentage_diff}%" if color == "red" else f"{percentage_diff}%"
    print(
        f"Previous value = {previous_value}, Current value = "
        f"{current_value}, Percentage diff = {percentage_diff},"
        f"xy={x_pos}, {y_pos}, Color = {color}"
    )
    axis.annotate(text, xy=(x_pos, y_pos), color=color, weight="bold")


def generate_graph(vt, tests, run_nums, dates):
    MEDIUM_SIZE = 25
    BIGGER_SIZE = 35

    plt.rc("font", size=MEDIUM_SIZE, family="serif")
    plt.rc("axes", titlesize=MEDIUM_SIZE, labelsize=MEDIUM_SIZE)
    plt.rc("xtick", labelsize=MEDIUM_SIZE)
    plt.rc("ytick", labelsize=MEDIUM_SIZE)
    plt.rc("legend", fontsize=MEDIUM_SIZE)
    plt.rc("figure", titlesize=BIGGER_SIZE)

    graph_width = float(os.getenv("INPUT_GRAPH_WIDTH"))
    graph_height = float(os.getenv("INPUT_GRAPH_HEIGHT"))

    # Times in CSV are stored in seconds, transform them to minutes for graph
    vt_timings = [x / 60 for x in vt]
    tests_timings = [x / 60 for x in tests]
    total_timings = [sum(x) for x in zip(vt_timings, tests_timings)]

    # plot
    _, (ax_1, ax_2, ax_3) = plt.subplots(
        figsize=(graph_width, graph_height), nrows=3, ncols=1
    )

    ax_1.set_title(f"{os.getenv('INPUT_TITLE')} ({dates[0]} - {dates[-1]})")
    plt.xlabel(os.getenv("INPUT_X_LABEL"))

    ax_1.plot(run_nums, total_timings, color="b", marker="o", label="total", linewidth=4)
    ax_2.plot(run_nums, vt_timings, color="m", marker="s", label="vt-lib", linewidth=4)
    ax_3.plot(
        run_nums,
        tests_timings,
        color="c",
        marker="d",
        label="tests and examples",
        linewidth=4,
    )

    annotate(ax_1, run_nums, total_timings)
    annotate(ax_2, run_nums, vt_timings)
    annotate(ax_3, run_nums, tests_timings)

    set_common_axis_data([ax_1, ax_2, ax_3])
    plt.tight_layout()

    plt.savefig(f"{OUTPUT_DIR}/{os.getenv('INPUT_GRAPH_FILENAME')}")


def generate_badge(vt_times, tests_times):
    average_time = (sum(vt_times) + sum(tests_times)) / len(vt_times)

    build_time = vt_times[-1] + tests_times[-1]
    badge_color = "brightgreen" if build_time <= average_time else "red"
    title = os.getenv("INPUT_BADGE_TITLE").replace(" ", "%20")

    print(
        f"Last build time = {build_time}seconds average build = {average_time}seconds color = {badge_color}"
    )
    url = f"https://img.shields.io/badge/{title}-{build_time//60}%20min%20{build_time%60}%20sec-{badge_color}.svg"

    badge_logo = os.getenv("INPUT_BADGE_LOGO")
    if len(badge_logo) > 0:
        url += f"?logo={badge_logo}"

    print(f"Downloading badge with URL = {url}")
    r = requests.get(url)

    open(f"{OUTPUT_DIR}/{os.getenv('INPUT_BADGE_FILENAME')}", "wb").write(r.content)


if __name__ == "__main__":
    [vt_times, tests_times, ret_runs, ret_dates] = prepare_data()
    generate_graph(vt_times, tests_times, ret_runs, ret_dates)
    generate_badge(vt_times, tests_times)
