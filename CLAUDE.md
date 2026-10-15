# CLAUDE.md · Claude Impact Lab Berlin (17 Oct 2026)

You are helping a mixed team (not all developers) build a working demo in ONE day.
Hard deadline: **16:00**. Shipping a working demo beats perfect code.

## How to work
- Ask 1–2 short questions first if the goal is unclear, then build.
- Build the **smallest thing that demos well**. Suggest cutting scope early.
- Prefer simple stacks: a single HTML file, Python, or Next.js. No complex infra.
- Explain what you did in plain language. Some teammates are not engineers.
- Make small commits with clear messages so the team can follow along.
- After each step, tell the team how to run or see it.

## Hard rules
- **Never put API keys or secrets in code or commits.** Read them from `.env` (`ANTHROPIC_API_KEY`).
- Never commit `.env`, `node_modules`, or large data files.
- Only use data the team is allowed to use. No real personal data. Use fake or sample data.
- Credit open-source libraries and assets in the README.
- Don't delete files the team created without asking.

## Using Claude in the product
- Use the Anthropic API with a current model (check docs.claude.com for model names).
- Keep prompts in one clear place (e.g. `prompts/`) so they're easy to tweak.
- Handle errors simply: show a friendly message if the API call fails.

## Before 16:00
- Keep `README.md` updated: what it does, who it's for, how to run it, screenshots.
- Around 15:00, remind the team to record a 2-minute demo and fill in their submission file
  (`submissions/_TEMPLATE.md` in the event repo).
