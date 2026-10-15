# ⚡ Claude Impact Lab Berlin · 17 Oct 2026

> We started with a conversation. Now we build.

A full-day build sprint in Berlin. ~100 curated people, mixed teams, Claude API credits, judges, and gifts for the winning team. Top builds get shared with Anthropic.

🔗 Event page: https://luma.com/claude-oofc

**Not just for developers.** Engineers, designers, researchers, founders, creatives, product people and domain experts all build here. If you can describe a problem, you can build with Claude.

---

## 🗓️ Schedule

| Time | What |
|---|---|
| 09:30 | Check-in + icebreaker |
| 10:00 | Opening: partner, problem, repo, rules, judging |
| 10:30 | Teams form, **build starts** |
| 13:00 | Lunch |
| 15:00 | Reminder: submission format. Record your demo now! |
| **16:00** | **⛔ Hard submission deadline** |
| 16:05 | Judges review and pick finalists |
| 16:40 | Final presentations (5 teams · 6 min + 4 min Q&A) |
| 17:30 | Judges grade |
| 17:45 | Winners announced + closing |
| 18:00 | End |

---

## 🚀 Get started (5 minutes)

1. **One person per team** clicks **Use this template** → *Create a new repository* (public).
2. Add your teammates as collaborators.
3. Set your API key (from your credits) locally. Never commit it:
   ```bash
   cp .env.example .env    # then paste your key into .env
   ```
4. Open the repo in Claude Code (`claude`) or Claude.ai. Claude reads `CLAUDE.md` automatically and follows the rules.
5. Build. 🛠️

**No terminal?** Build in [Claude.ai](https://claude.ai) with artifacts, then paste your link and screenshots into your submission. That counts.

---

## 📏 Rules

1. **Build today.** Ideas and research can come from before; the build happens on the day.
2. **Use Claude.** Claude must be part of the solution, not just the tool that wrote it.
3. **Teams of 3–5**, mixed backgrounds.
4. **Public repo** with a README anyone can follow.
5. **No secrets in Git.** API keys go in `.env`, which is git-ignored.
6. **Open-source libraries, APIs and assets are fine.** Credit them in your README.
7. **Be kind.** Help other teams and respect the venue.
8. **16:00 is final.** Late submissions are not judged.

---

## 📤 How to submit (before 16:00)

### Option A: Issue form (easiest, no git needed)

1. Go to **Issues → New issue → 🚀 Team submission**
2. Fill in the form and click *Submit new issue*
3. A bot creates `submissions/<your-team-name>.md` and opens a Pull Request linked to your issue ✅

Need to change something? Edit your issue and the PR updates automatically.

### Option B: Pull Request by hand

Open a Pull Request **to this repo** that adds one file: `submissions/<your-team-name>.md`

1. Copy [`submissions/_TEMPLATE.md`](submissions/_TEMPLATE.md)
2. Rename it to your team name, e.g. `submissions/team-kiez-builders.md`
3. Fill it in: repo link, one-line pitch, team, optional 2-minute demo video
4. Open the PR. Done ✅

**Tip:** Record the 2-minute demo at 15:00, not 15:55. Loom, a phone, or a screen recording all work.

---

## 🏆 Judging

| Criteria | Question the judges ask |
|---|---|
| **Impact** | Does it solve a real problem from the themes? Who benefits? |
| **Use of Claude** | Is Claude used in a smart, meaningful way? |
| **Execution** | Does it work? Can we see it working? |
| **Creativity** | Is the idea or approach fresh? |
| **Presentation** | Is it clear in 6 minutes? |

Finalists: 5 teams · 6 min demo + 4 min Q&A.

---

## 🆘 Help

Stuck? Find an Claude ambassadors or mentor in the room. 

Useful links:
- Claude docs: https://docs.claude.com
- Claude Code: https://docs.claude.com/en/docs/claude-code/overview
- Prompting guide: https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview

Have fun. Build something that matters. 🧡
