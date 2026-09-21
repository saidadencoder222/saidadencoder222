# CRM Sales Auditor

Turns a raw pipeline export into a prioritized report of "trapped" pipeline
value and ready-to-send resurrection templates.

## Setup

Export your pipeline data from GoHighLevel, HubSpot, or Airtable into a CSV
named `pipeline.csv` in this folder, matching this schema:

| Column                  | Description                                   |
|--------------------------|------------------------------------------------|
| `Lead Name`              | Full name of the lead                          |
| `Stage`                  | Current pipeline stage                         |
| `Created Date`           | Date the lead entered the pipeline             |
| `Last Interaction Date`  | Date of the most recent touchpoint             |
| `Deal Value`             | Dollar value of the deal                       |
| `Lost Reason / Notes`    | Free-text notes on why the deal stalled/lost   |

See [`pipeline.example.csv`](./pipeline.example.csv) for a sample.

## Terminal Prompt

```
claude "Analyze the data inside crm-audit/pipeline.csv. Perform the following
data audits:
1. Calculate the exact dollar value currently trapped in the 'Follow-Up
   Needed' and 'No Show' stages.
2. Group the 'Lost Reason / Notes' column into the 3 most common macro
   objections (e.g., Price/Capital, Timing, Trust).
3. Generate a Markdown report in crm-audit/insights_report.md. For each macro
   objection, write 2 highly distinct, conversion-optimized SMS follow-up
   templates and 1 high-intent email template designed to resurrect those
   cold deals. Ensure the copy feels natural, conversational, and completely
   devoid of high-pressure sales tropes."
```

## Output

`crm-audit/insights_report.md` — trapped-value breakdown, macro objection
analysis, and resurrection scripts per objection.
