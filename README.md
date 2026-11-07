# Physics I teaching portal

A local web application with one playable **Kinematics** level, a game-style learning map, six checkpoints, a practice/simulation boss, a course creator and six connected agent roles. Other Physics I levels remain outlines.

```sh
python3 kinematics/server.py
```

On the first run, open your private single-use administrator setup link:

```sh
python3 kinematics/account_setup.py
```

Choose your admin email and password on that screen. You are the only administrator; the public `/register` page always creates a student. Students cannot access Course studio, Agent studio, their APIs, uploads, rubrics or review/publishing actions. `/profile` saves each account’s name and tutor language; private progress, notes, working and chat persist across logins. The admin profile lists registered students. The setup credential lives only in the ignored, owner-readable runtime folder and is removed after use.

Open [the local app](http://127.0.0.1:8765/). **Paid calls are enabled in the owner’s local `.env`.** All six roles use GPT-6 Luna with low reasoning effort through one shared server-side key. Limits remain $0.10 per account, $0.25 per UTC day and $2 per UTC month across the application. Calls run only on explicit requests; native extraction and numeric checks remain local. `.env.example` keeps paid execution disabled for fresh checkouts.

- **Course studio**: create a course and upload lecture, practice, exam and solution files.
- **Agent studio**: choose the local reviewer, extract and confirm source pages, draft a Kinematics structure, review lessons/checkpoints, and publish a reviewed learning pack. Review rubrics, cohort proposals and outside resources here.
- **My working**: upload handwritten images/PDFs or type working, read/edit a transcription, confirm and lock it, then request formative feedback.
- **Ask your tutor**: page-aware chat with private memory and scoped evidence. Offline mode returns labeled course-note previews. Live mode supports multilingual explanations.

All six roles have workflow implementations: Reader, Builder, Tutor, Evaluator, Curator and Scout. Live model quality is not established by offline tests; handwriting recognition and AI reasoning require deliberately enabling paid mode later.

[Setup and limits](kinematics/README.md) · [Agent architecture and endpoints](docs/AGENT_WORKFLOWS.md) · [Original agent plan](docs/AI_AGENTS_IMPLEMENTATION_PLAN.md)

This is a loopback-only, single-device prototype. Accounts use local password authentication, not university SSO. Email verification and password recovery are not connected. Generated content and model feedback are not official course grades. No new academic content has been approved on your behalf in the main workspace.
