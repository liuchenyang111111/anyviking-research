# Cases

Cases are small, reusable YAML templates for real research or forecast-data collection tasks.

They do not replace free-form commands such as `anyviking sync`. They simply make one workflow reproducible:

```bash
anyviking run-case cases/ai_coding_agents.yaml
```

You can copy any case file, change the question, queries, output directory, and target `viking://` URI, then run it as your own collection task.

Runtime outputs are written under `data/` and are ignored by Git.
