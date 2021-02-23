import matplotlib.pyplot as plt
import argparse
from github import Github
import os

# Get file name from user
parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', help='Output file name', required=True)
graph_file_name = parser.parse_args().output

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

print(f'Repo={REPO_NAME} Workflow={WORKFLOW_NAME}')

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
workflow = repo.get_workflow(id_or_name=WORKFLOW_NAME)

# Data to be plotted
timings = []
run_nums = []

workflow_runs = workflow.get_runs(status="success", branch=BRANCH_NAME)

print(f'workflow_runs.totalCount={workflow_runs.totalCount} and requested_last_runs={REQUESTED_N_LAST_BUILDS}')

last_n_runs = min(REQUESTED_N_LAST_BUILDS, workflow_runs.totalCount)

print(f'last_n_runs={last_n_runs}')

for run in workflow_runs[:last_n_runs]:
    run_timing = run.timing()
    print(f"workflow_run:{run.workflow_id} with ID:{run.id} took:{run_timing.run_duration_ms}ms")

    # Convert ms to min
    timings.append(run_timing.run_duration_ms / 60000.0)
    run_nums.append(run.run_number)

SMALL_SIZE = 15
MEDIUM_SIZE = 25
BIGGER_SIZE = 35

plt.rc('font', size=SMALL_SIZE, family='serif')
plt.rc('axes', titlesize=BIGGER_SIZE, labelsize=MEDIUM_SIZE)
plt.rc('xtick', labelsize=SMALL_SIZE)
plt.rc('ytick', labelsize=SMALL_SIZE)
plt.rc('legend', fontsize=SMALL_SIZE)
plt.rc('figure', titlesize=BIGGER_SIZE)

# plot
plt.figure(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT))
plt.plot(run_nums, timings, color='b', marker='o')
plt.grid(True)

plt.title(GRAPH_TITLE)
plt.xlabel(X_LABEL)
plt.ylabel(Y_LABEL)

plt.savefig(graph_file_name)
