# graph-build-times

The DARMA-tasking/graph-build-times is a GitHub action that generates a graph of build times for a given workflow and then pushes that graph to the project's wiki page.

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
    - name: Generate and push graph
      uses: DARMA-tasking/graph-build-times@master
      with:
        github_personal_token: ${{ secrets.GH_PAT }}
        github_token: ${{ github.token }}
        workflow: workflow_name.yml
        filename: build_times_graph.png
        num_last_build: 50
        title: Last 50 builds of {workflow_name} workflow
        graph_width: 19
        graph_height: 8
```

## Inputs

Following inputs can be used to customize the graph

| Name                    |Required| Description                        |
|-------------------------|--------|------------------------------------|
| `github_personal_token` | TRUE   | Github personal access token used to push graph to remote wiki repo |
| `github_token`          | TRUE   | Github token used for Github API requests |
| `workflow`              | TRUE   | Name of the worflow (yaml file or Github's unique workflow ID number) for which the graph will be generated |
| `filename`              | FALSE  | Filename for the generated graph that will be pushed to the wiki repo |
| `repo`                  | FALSE  | Repository name where queried workflow is being run. This should only be used when the asked workflow is being run on different repository than workflow using this action |
| `num_last_build`        | FALSE  | Number of last builds used for generating graph |
| `branch`                | FALSE  | Branch on which workflow is running |
| `title`                 | FALSE  | Title of the generated graph |
| `x_label`               | FALSE  | X axis label |
| `y_label`               | FALSE  | Y axis label |
| `graph_width`           | FALSE  | Graph width in inches |
| `graph_height`          | FALSE  | Graph height in inches |
| `commit_message`        | FALSE  | Commit message for wiki page |
