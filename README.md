# graph-build-times

The DARMA-tasking/graph-build-times is a GitHub action that generates a graph of build times together with the badge of the last build. To obtain the data of the last builds, it uses the file `build_times_filename` located in repository's wiki page. This is CSV file which contains time, number and the date for past builds, represented by the columns `time`, `run_num` and `date`.

The file specified with `last_build_time_file` input variable, has to contain the output of [time](https://man7.org/linux/man-pages/man1/time.1.html) command.

## Workflow example

```yml
name: Graph VT build times

on:
  push:
    branches:
      - develop

jobs:
  graph:
    runs-on: ubuntu-latest
    steps:
    - name: Generate graph and badge
      uses: DARMA-tasking/graph-build-times@master
      with:
        github_personal_token: ${{ secrets.GH_PAT }}
        last_build_time: 50m20.00s
        build_times_filename: build_times.csv
        graph_filename: build_times_graph.png
        badge_filename: build_time_badge.svg
        badge_title: {workflow_name} build time
        num_last_build: 50
        title: Last 50 builds of {workflow_name} workflow
        graph_width: 19
        graph_height: 8
```

## Inputs

| Name                    |Required| Description                        |
|-------------------------|--------|------------------------------------|
| `github_personal_token` | TRUE   | Github personal access token used to push graph to remote wiki repo |
| `last_build_time`       | TRUE   | Last build time. Format example 20m40.00s ([time](https://man7.org/linux/man-pages/man1/time.1.html) command output) |
| `graph_filename`        | FALSE  | Filename for the generated graph that will be pushed to the wiki repo |
| `badge_filename`        | FALSE  | Filename for generated badge which displays most recent build time. Note that this file is SVG type |
| `badge_title`           | FALSE  | Title that will be displayed on the badge |
| `badge_logo`            | FALSE  | Logo which will be displayed on the badge. For the list of logos see https://shields.io/
| `num_last_build`        | FALSE  | Number of last builds used for generating graph |
| `title`                 | FALSE  | Title of the generated graph |
| `x_label`               | FALSE  | X axis label |
| `y_label`               | FALSE  | Y axis label |
| `graph_width`           | FALSE  | Graph width in inches |
| `graph_height`          | FALSE  | Graph height in inches |
| `commit_message`        | FALSE  | Commit message for wiki page |
