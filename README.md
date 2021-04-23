# build-stats

The DARMA-tasking/build-stats is a GitHub action that builds DARMA-tasking/vt project and generates a Markdown file which contains a bunch of build statistics, such as graphs of last build times, badge with the most recent build time and information about most expensive templates and headers (this data is generated using [ClangBuildAnalyzer tool](https://github.com/aras-p/ClangBuildAnalyzer)). All generated data is stored on project's wiki repository (inside `build_stats_output` directory).

The data of the last builds is stored in CSV file, which is located in repository's wiki page. Example:

```csv
vt,tests,run_num,date,commit
561,2290,2,16 April 2021,971fa98f10b94df4057e589808063beb8e94c43e
```

- `vt` build time of vt-lib (in seconds)
- `tests` time of tests and examples (in seconds)
- `run_num` run_ID for that particular workflow run
- `date` when it run
- `commit` commit SHA which triggered the run


## Workflow example

```yml
name: Generate build stats

on:
  push:
    branches:
      - develop

jobs:
  graph:
    runs-on: ubuntu-latest
    steps:
    - name: Generate build stats
      uses: DARMA-tasking/build-stats@master
      with:
        github_personal_token: ${{ secrets.GH_PAT }}
        num_last_build: 50
        title: Last 50 builds of {workflow_name} workflow
```

## Inputs

| Name                    |Required| Description                        |
|-------------------------|--------|------------------------------------|
| `github_personal_token` | TRUE   | Github personal access token used to push graph to remote wiki repo |
| `build_stats_output`    | FALSE  | Wiki repo directory for generated build data. Defaults to root directory |
| `build_times_filename`  | FALSE  | Filename where the previous build times are stored. File format should be CSV. Defaults to `build_times.csv` |
| `build_result_filename` | FALSE  | Path to ClangBuildAnalyzer file (txt format). Defaults to `build_result.txt` |
| `graph_filename`        | FALSE  | Filename for the generated graph that will be pushed to the wiki repo. Defaults to `graph.png` |
| `badge_filename`        | FALSE  | Filename for generated badge which displays most recent build time. Note that this file is SVG type. Defaults to `build_status_badge.svg` |
| `badge_title`           | FALSE  | Title that will be displayed on the badge |
| `badge_logo`            | FALSE  | Logo which will be displayed on the badge. For the list of logos see https://shields.io/
| `num_last_build`        | FALSE  | Number of last builds used for generating graph |
| `title`                 | FALSE  | Title of the generated graph |
| `x_label`               | FALSE  | X axis label |
| `y_label`               | FALSE  | Y axis label |
| `graph_width`           | FALSE  | Graph width in inches |
| `graph_height`          | FALSE  | Graph height in inches |
| `commit_message`        | FALSE  | Commit message for wiki page |
