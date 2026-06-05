# Cases

Cases are small, reusable YAML templates for real research or forecast-data collection tasks.

The example cases in this folder are adapted from the OracleProto forecasting dataset:

https://huggingface.co/datasets/MaYiding/OracleProto

They keep the original forecast event, options, and deadline, but do not include the answer. AnyViking's role is to collect and organize evidence for the question.

They do not replace free-form commands such as `anyviking sync`. They simply make one workflow reproducible:

```bash
anyviking run-case cases/oracleproto_deepseek_v4.yaml
```

You can copy any case file, change the question, queries, output directory, and target `viking://` URI, then run it as your own collection task.

Runtime outputs are written under `data/` and are ignored by Git.
