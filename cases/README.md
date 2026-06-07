# Cases

Cases are small, reusable YAML templates for real research or forecast-data collection tasks.

The example cases in this folder are adapted from the OracleProto forecasting dataset:

https://huggingface.co/datasets/MaYiding/OracleProto

They keep the original forecast event, options, and deadline, but do not include the answer. AnyViking's role is to collect and organize evidence for the question.

Cases are split into:

```text
oracleproto/train/  # used for workflow improvement
oracleproto/eval/   # used for validation only
```

They do not replace free-form commands such as `anyviking sync`. They simply make one workflow reproducible:

```bash
anyviking run-case cases/oracleproto/train/deepseek_v4.yaml
```

To score a forecast case, use `forecast`. The answer is read from the matching `.answer.json` file at scoring time only:

```bash
anyviking forecast cases/oracleproto/train/deepseek_v4.yaml --skip-import
```

You can copy any case file, change the question, queries, output directory, and target `viking://` URI, then run it as your own collection task.

Runtime outputs are written under `data/` and are ignored by Git.
