# Forecast User Template

Question type: {question_type}
Question: {question}
Cutoff date: {cutoff_date}

Options:
{options}

Evidence:
{evidence}

Return JSON with exactly these keys:

- predicted_answer: one of the options
- probabilities: object whose keys are the options and whose values sum to 1
- rationale: short explanation grounded in the evidence
