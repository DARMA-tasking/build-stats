import matplotlib.pyplot as plt
import argparse
from github import Github
import os
import requests

# Input variables from Github action
GITHUB_TOKEN = os.getenv('INPUT_GITHUB_TOKEN')
REPO_NAME = os.getenv('INPUT_REPO')
WORKFLOW_NAME = os.getenv('INPUT_WORKFLOW')
BRANCH_NAME = os.getenv('INPUT_BRANCH')
REQUESTED_N_LAST_BUILDS = int(os.getenv('INPUT_NUM_LAST_BUILD'))
GRAPH_TITLE = os.getenv('INPUT_TITLE', '')
X_LABEL = os.getenv('INPUT_X_LABEL')
Y_LABEL = os.getenv('INPUT_Y_LABEL')
GRAPH_WIDTH = float(os.getenv('INPUT_GRAPH_WIDTH'))
GRAPH_HEIGHT = float(os.getenv('INPUT_GRAPH_HEIGHT'))
GRAPH_FILENAME = os.getenv('INPUT_GRAPH_FILENAME')
BADGE_FILENAME = os.getenv('INPUT_BADGE_FILENAME')
BADGE_TITLE = os.getenv('INPUT_BADGE_TITLE')

print(f'Repo={REPO_NAME} Workflow={WORKFLOW_NAME}')

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
workflow = repo.get_workflow(id_or_name=WORKFLOW_NAME)

# Data to be plotted
timings = []
run_nums = []
dates = []

workflow_runs = workflow.get_runs()

print(f'workflow_runs.totalCount={workflow_runs.totalCount} and requested_last_runs={REQUESTED_N_LAST_BUILDS}')

last_n_runs = min(REQUESTED_N_LAST_BUILDS, workflow_runs.totalCount)

print(f'last_n_runs={last_n_runs}')

run_counter = 0
total_run_time = 0
for run in workflow_runs:
    if(run.head_branch == BRANCH_NAME and run.status == 'completed'):
        run_timing = run.timing()
        print(f"workflow_run:{run.workflow_id} with ID:{run.id} took:{run_timing.run_duration_ms}ms")

        # Convert ms to min
        time_in_min = run_timing.run_duration_ms / 60000.0
        timings.append(time_in_min)
        run_nums.append(run.run_number)
        dates.append(run.created_at)

        run_counter += 1
        total_run_time += time_in_min

    if run_counter >= last_n_runs:
        break

SMALL_SIZE = 15
MEDIUM_SIZE = 25
BIGGER_SIZE = 35

plt.rc('font', size=MEDIUM_SIZE, family='serif')
plt.rc('axes', titlesize=BIGGER_SIZE, labelsize=MEDIUM_SIZE)
plt.rc('xtick', labelsize=SMALL_SIZE)
plt.rc('ytick', labelsize=SMALL_SIZE)
plt.rc('legend', fontsize=SMALL_SIZE)
plt.rc('figure', titlesize=BIGGER_SIZE)

# plot
fig, ax = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT))
plt.plot(run_nums, timings, color='b', marker='o')
plt.grid(True)

fig.text(0.05,0.02, f'{dates[-1].day} {dates[-1].strftime("%B")} {dates[-1].year }')
fig.text(0.95,0.02, f'{dates[0].day} {dates[0].strftime("%B")} {dates[0].year }', horizontalalignment='right')

plt.title(GRAPH_TITLE)
plt.xlabel(X_LABEL)
plt.ylabel(Y_LABEL)

plt.savefig(GRAPH_FILENAME)


# Generate badge with most recent build time

average_time = total_run_time / last_n_runs

BUILD_TIME = timings[0]
BADGE_COLOR = "green" if BUILD_TIME <= average_time else "red"
title = BADGE_TITLE.replace(" ", "%20")

print(f"Last build time = {BUILD_TIME} average build = {average_time} color = {BADGE_COLOR} ")
url = f"https://img.shields.io/badge/{title}-{format(BUILD_TIME,'.1f')}%20min-{BADGE_COLOR}.svg"

print(f"Downloading badge with URL = {url}")
r = requests.get(url)

open(BADGE_FILENAME, 'wb').write(r.content)
