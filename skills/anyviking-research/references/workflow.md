# Workflow Guide

Use the smallest command that satisfies the user request.

## Search Only

```text
search-web
```

Use this when the user only wants fresh web results.

## Save For Inspection

```text
fetch-web
```

Use this when the user wants markdown files before indexing.

## Save And Index

```text
sync
```

Use this when the user wants public web material available through OpenViking.

## Existing Local Corpus

```text
import-local -> search
```

Use this when the user already has markdown or text files.

## Read From OpenViking

```text
search
```

Use this when the user or their Agent already knows the `viking://` scope.

## Important Point

`viking://` is a virtual OpenViking URI. An Agent needs a tool such as `ar search` or another OpenViking adapter to read it.
