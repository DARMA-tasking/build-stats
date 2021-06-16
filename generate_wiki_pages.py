import matplotlib.pyplot as plt
import argparse
import os
import requests
from datetime import date
import pandas as pd
import numpy as np

OUTPUT_DIR = os.getenv('INPUT_BUILD_STATS_OUTPUT')
CLANG_BUILD_REPORT = f"{OUTPUT_DIR}/{os.getenv('INPUT_BUILD_RESULT_FILENAME')}"

EXP_TEMPLATE_INST_DIR = f"{OUTPUT_DIR}/most_expensive_templates.png"
EXP_TEMPLATE_SET_DIR = f"{OUTPUT_DIR}/most_expensive_templates_sets.png"
EXP_HEADERS_DIR = f"{OUTPUT_DIR}/most_expensive_headers.png"
GRAPH_FILENAME = f"{OUTPUT_DIR}/{os.getenv('INPUT_GRAPH_FILENAME')}"
BADGE_FILENAME = f"{OUTPUT_DIR}/{os.getenv('INPUT_BADGE_FILENAME')}"

NUM_TOP_RESULTS = 25
REPO_NAME = os.getenv('GITHUB_REPOSITORY')


def get_name_times_avg(lines):
    """
    Example input:
    26549 ms: some<template> (306 times, avg 86 ms)
    25000 ms: some<other_template> (500 times, avg 50 ms)

    Output:
    total_times = [26549, 25000]
    name_times_avg = {0: (some<template>, 306, 86), 1: (some<other_template>, 500, 50)}
    """
    AVG_MS_THRESHOLD = 20

    total_times = []
    name_times_avg = dict()

    index = 0

    for line in lines:
        # Stop if we parsed all lines for given action or we've reached the limit
        if not line.endswith("ms)") or index >= NUM_TOP_RESULTS:
            break

        avg_time = int(line[line.rfind("avg") + 3: line.rfind("ms")])

        # Don't include very cheap templates
        if avg_time < AVG_MS_THRESHOLD:
            continue

        # Total time spent for given template/function
        delimiter = line.index("ms")
        total_times.append(int(line[: delimiter]))

        # Template/function name
        tmp_text = line[delimiter + 3:]
        end_of_name = tmp_text.rfind("(")
        name = tmp_text[:end_of_name - 1]

        # Number of times given template/function was used
        times_and_avg = tmp_text[end_of_name + 1:]
        times_used = int(times_and_avg[:times_and_avg.index(" ")])

        name_times_avg[index] = (name, times_used, avg_time)
        index += 1

    return total_times, name_times_avg


def get_headers(lines):
    """
    Example input:
    26549 ms: some_header.h (included 237 times, avg 506 ms), included via:
        ... (some files)
    2400 ms: some_other_header.h (included 100 times, avg 240 ms), included via:
        ... (some files)

    Output:
    header_times = [26549, 2400]
    name_included_avg = {0: (some_header.h, 237, 506), 1: (some_other_header.h, 100, 240)}
    """

    header_times = []
    name_included_avg = dict()

    index = 0

    for line in lines:
        if line.endswith("included via:"):
            delimiter = line.index("ms: ")
            header_times.append(int(line[: delimiter]))

            tmp_text = line[delimiter + len("ms: "):]
            end_of_name = tmp_text.rfind("(included ")
            name = tmp_text[:end_of_name - 1]

            # Remove the relative path from the file names
            while name.startswith("../"):
                name = name[3:]

            times_and_avg = tmp_text[end_of_name + len("(included "):]
            times_used = int(times_and_avg[:times_and_avg.index(" ")])
            avg_time = int(times_and_avg[times_and_avg.index(
                "avg") + 3: times_and_avg.index("ms")])

            name_included_avg[index] = (name, times_used, avg_time)
            index += 1

    return header_times, name_included_avg


def generate_name_times_avg_table(templates_text):
    templates_string = "| Label | Name | Times | Avg (ms) |\n"\
        "|---|:---:|---|---|\n"
    for idx, (name, times, avg) in templates_text.items():
        # Escape '|' to not break markdown table
        name = name.replace("|", "\|")
        templates_string += f"| **{idx}** | `{name}` | **{times}** | **{avg}** |\n"

    return templates_string


def prepare_data():
    # Expensive template instantiations
    templates_total_times = []
    templates = dict()

    # Expensive template sets
    template_sets_times = []
    template_sets = dict()

    # Expensive headers
    headers_times = []
    headers = dict()

    with open(CLANG_BUILD_REPORT) as f:
        lines = f.read().splitlines()

        for idx, line in enumerate(lines):
            if line.startswith("**** Templates that took longest to instantiate:"):
                templates_total_times, templates = get_name_times_avg(
                    lines[idx + 1:])

            if line.startswith("**** Template sets that took longest to instantiate:"):
                template_sets_times, template_sets = get_name_times_avg(
                    lines[idx + 1:])

            if line.startswith("*** Expensive headers:"):
                headers_times, headers = get_headers(lines[idx + 1:])

    return templates, template_sets, headers, templates_total_times, template_sets_times, headers_times


def generate_graph(name, templates_total_times):

    SMALL_SIZE = 15
    MEDIUM_SIZE = 25
    BIGGER_SIZE = 35

    plt.rc('font', size=MEDIUM_SIZE, family='serif')
    plt.rc('axes', titlesize=MEDIUM_SIZE, labelsize=MEDIUM_SIZE)
    plt.rc('xtick', labelsize=MEDIUM_SIZE)
    plt.rc('ytick', labelsize=BIGGER_SIZE)
    plt.rc('legend', fontsize=BIGGER_SIZE)
    plt.rc('figure', titlesize=BIGGER_SIZE)

    barWidth = 0.50
    fig, ax = plt.subplots(figsize=(19, 14))

    templates_total_times = [t//1000 for t in templates_total_times]
    TTT = templates_total_times

    # Add x, y gridlines
    ax.grid(b=True, color='grey',
            linestyle='-.', linewidth=0.5,
            alpha=0.8)

    # Remove x, y Ticks
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')

    # Add padding between axes and labels
    ax.xaxis.set_tick_params(pad=5)
    ax.yaxis.set_tick_params(pad=10)

    ax.invert_yaxis()

    yAxies = range(len(TTT))

    ax.barh(yAxies, TTT, height=barWidth, label='total time (sec)')

    for idx, i in enumerate(ax.patches):
        plt.text(i.get_width()+0.2, i.get_y()+0.5,
                 str(round((i.get_width()), 2)), fontsize=BIGGER_SIZE, color='black')

    yTicks = range(len(TTT))
    plt.yticks([r for r in yTicks], yTicks)

    plt.legend()
    plt.tight_layout()

    plt.savefig(name)


def convert_time(time_in_sec):
    return f"{time_in_sec//60}min {time_in_sec%60}sec"


def generate_last_build_table():
    PREVIOUS_BUILDS_FILENAME = f"{OUTPUT_DIR}/{os.getenv('INPUT_BUILD_TIMES_FILENAME')}"
    df = pd.read_csv(PREVIOUS_BUILDS_FILENAME)
    last_builds = df.tail(int(os.getenv('INPUT_NUM_LAST_BUILD')) - 1)

    run_nums = last_builds['run_num'].tolist()
    vt_timings = last_builds['vt'].tolist()
    tests_timings = last_builds['tests'].tolist()
    total_timings = [sum(x) for x in zip(vt_timings, tests_timings)]
    dates = last_builds['date'].tolist()
    commits = last_builds['commit'].tolist()

    last_builds_table = "<details> <summary> <b> CLICK HERE TO SEE PAST BUILDS </b> </summary>"\
        "<table style=\"width:100%\">"\
        "<tr>"\
        "<th>Run</th>"\
        "<th>Date</th>"\
        "<th>Total time</th>"\
        "<th>vt-lib time</th>"\
        "<th>Tests and Examples</th>"\
        "<th>Commit SHA</th>"\
        "</tr>"

    for i in range(-1, -last_builds.shape[0], -1):
        last_builds_table += f"<tr><td><b>{run_nums[i]}</b></td>"\
            f"<td>{dates[i]}</td>"\
            f"<td>{convert_time(total_timings[i])}</td>"\
            f"<td>{convert_time(vt_timings[i])}</td>"\
            f"<td>{convert_time(tests_timings[i])}</td>"\
            f"<td><a href='https://github.com/{REPO_NAME}/commit/{commits[i]}'>Commit</a></td></tr>"\

    last_builds_table += "</table></details>\n"

    return last_builds_table


def generate_last_runs_table():
    PREVIOUS_BUILDS_FILENAME = f"{OUTPUT_DIR}/{os.getenv('INPUT_BUILD_TIMES_FILENAME')}"
    df = pd.read_csv(PREVIOUS_BUILDS_FILENAME)
    last_builds = df.tail(int(os.getenv('INPUT_NUM_LAST_BUILD')) - 1)

    run_nums = last_builds['run_num'].tolist()
    vt_timings = last_builds['vt'].tolist()
    tests_timings = last_builds['tests'].tolist()
    total_timings = [sum(x) for x in zip(vt_timings, tests_timings)]
    dates = last_builds['date'].tolist()
    commits = last_builds['commit'].tolist()

    last_builds_table = "<details> <summary> <b> CLICK HERE TO SEE PAST BUILDS </b> </summary>"\
        "<table style=\"width:100%\">"\
        "<tr>"\
        "<th>Run</th>"\
        "<th>Date</th>"\
        "<th>Total time</th>"\
        "<th>vt-lib time</th>"\
        "<th>Tests and Examples</th>"\
        "<th>Commit SHA</th>"\
        "</tr>"

    for i in range(-1, -last_builds.shape[0], -1):
        last_builds_table += f"<tr><td><b>{run_nums[i]}</b></td>"\
            f"<td>{dates[i]}</td>"\
            f"<td>{convert_time(total_timings[i])}</td>"\
            f"<td>{convert_time(vt_timings[i])}</td>"\
            f"<td>{convert_time(tests_timings[i])}</td>"\
            f"<td><a href='https://github.com/{REPO_NAME}/commit/{commits[i]}'>Commit</a></td></tr>"\

    last_builds_table += "</table></details>\n"

    return last_builds_table


def create_image_hyperlink(image_link):
    return f"[![]({image_link})]({image_link})"


def get_runner_info():
    return f"**NOTE. The following builds were run on GitHub Action runners that use [2-core CPU and 7 GB RAM]"\
        "(https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#supported-runners-and-hardware-resources)** <br><br> \n"\
        "Configuration:\n"\
        "- Compiler: **Clang-10**\n"\
        "- Linux: **Ubuntu 20.04**\n"\
        "- Build Type: **Release**\n"\
        "- Unity Build: **OFF**\n"\
        "- Production Mode: **OFF**\n"


def create_md_page(last_builds, exp_temp_inst, exp_temp_sets, exp_headers):

    exp_templates_inst_string = generate_name_times_avg_table(exp_temp_inst)
    exp_templates_sets_string = generate_name_times_avg_table(exp_temp_sets)
    exp_headers_string = generate_name_times_avg_table(exp_headers)

    PAGE_NAME = "Build-Stats"
    with open(f"{PAGE_NAME}.md", "w") as f:
        WIKI_PAGE = f"https://github.com/{REPO_NAME}/wiki/{PAGE_NAME}"
        f.write(f""
                f"- [Build History]({WIKI_PAGE}#build-history)\n"
                f"- [Past Builds]({WIKI_PAGE}#past-builds)\n"
                f"- [Templates that took longest to instantiate]({WIKI_PAGE}#templates-that-took-longest-to-instantiate)\n"
                f"- [Template sets that took longest to instantiate]({WIKI_PAGE}#template-sets-that-took-longest-to-instantiate)\n"
                f"- [Most expensive headers]({WIKI_PAGE}#Most-expensive-headers)\n"
                f"- [ClangBuildAnalyzer full report]({CLANG_BUILD_REPORT})\n"
                "***\n"
                f"# Build History\n"
                f"{get_runner_info()}"
                "<br><br>\n"
                f"[![](https://github.com/{REPO_NAME}/wiki/{GRAPH_FILENAME})](https://github.com/{REPO_NAME}/wiki/{GRAPH_FILENAME})\n"
                "## Past Builds\n"
                f"{last_builds} \n"
                "*** \n"
                "# Build Stats\n"
                f"Following graphs were generated using data created by [ClangBuildAnalyzer](https://github.com/aras-p/ClangBuildAnalyzer) \n"
                "## Templates that took longest to instantiate \n"
                f"{create_image_hyperlink(f'https://github.com/{REPO_NAME}/wiki/{EXP_TEMPLATE_INST_DIR}')}\n"
                f"{exp_templates_inst_string}"
                "*** \n"
                "## Template sets that took longest to instantiate \n"
                f"{create_image_hyperlink(f'https://github.com/{REPO_NAME}/wiki/{EXP_TEMPLATE_SET_DIR}')}\n"
                f"{exp_templates_sets_string}"
                "*** \n"
                "## Most expensive headers \n"
                f"{create_image_hyperlink(f'https://github.com/{REPO_NAME}/wiki/{EXP_HEADERS_DIR}')}\n"
                f"{exp_headers_string}"
                "*** \n"
                )


def create_md_perf_page():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tests_names', help='Perf tests names',
                        nargs='+', default=[], required=True)

    test_names = parser.parse_args().tests_names

    PERF_TESTS_URL = f"https://github.com/{REPO_NAME}/wiki/perf_tests/"
    content_with_all_tests = "# Test Results\n"

    for test_name in test_names:
        content_with_all_tests += f""\
            f"## {test_name}\n"\
            f"{create_image_hyperlink(f'{PERF_TESTS_URL}{test_name}_past_runs.png')}\n"\
            f"{create_image_hyperlink(f'{PERF_TESTS_URL}{test_name}_time.png')}\n"\
            f"{create_image_hyperlink(f'{PERF_TESTS_URL}{test_name}_memory.png')}\n"\
            "*** \n"

    PAGE_NAME = "Perf-Tests"
    with open(f"{PAGE_NAME}.md", "w") as f:
        f.write(f""
                f"# Performance Tests\n"
                f"{get_runner_info()}"
                f"{content_with_all_tests}\n"
                "# Heaptrack result\n"
                "Following flamegraphs were generated using [Heaptrack](https://github.com/KDE/heaptrack) and [Flamegraph](https://github.com/brendangregg/FlameGraph)\n"
                "## jacobi2d_vt node: 0\n"
                f"{create_image_hyperlink(f'{PERF_TESTS_URL}flame_heaptrack_jacobi_alloc_count_0.svg')}\n"
                f"{create_image_hyperlink(f'{PERF_TESTS_URL}flame_heaptrack_jacobi_alloc_size_0.svg')}\n"
                f"{create_image_hyperlink(f'{PERF_TESTS_URL}flame_heaptrack_jacobi_leaked_0.svg')}\n"
                "## jacobi2d_vt node: 1\n"
                f"{create_image_hyperlink(f'{PERF_TESTS_URL}flame_heaptrack_jacobi_alloc_count_1.svg')}\n"
                f"{create_image_hyperlink(f'{PERF_TESTS_URL}flame_heaptrack_jacobi_alloc_size_1.svg')}\n"
                f"{create_image_hyperlink(f'{PERF_TESTS_URL}flame_heaptrack_jacobi_leaked_1.svg')}\n"
                )


if __name__ == "__main__":
    # templates, template_sets, headers, templates_total_times, template_sets_times, headers_times = prepare_data()
    # generate_graph(EXP_TEMPLATE_INST_DIR, templates_total_times)
    # generate_graph(EXP_TEMPLATE_SET_DIR, template_sets_times)
    # generate_graph(EXP_HEADERS_DIR, headers_times)

    # last_builds = generate_last_build_table()
    # create_md_page(last_builds, templates, template_sets, headers)
    create_md_perf_page()
