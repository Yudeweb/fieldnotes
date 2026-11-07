# Physics I teaching portal

A local web application with one playable **Kinematics** level, a game-style learning map, six checkpoints, a practice/simulation boss, a course creator and six connected agent roles. Other Physics I levels remain outlines.

```sh
python3 kinematics/server.py
```

Open [the local app](http://127.0.0.1:8765/). **Paid calls are disabled.** The saved API key stays private in `.env`. Offline previews, local file extraction and numeric checks work without API spending.

- **Course studio**: create a course and upload lecture, practice, exam and solution files.
- **Agent studio**: choose the local reviewer, extract and confirm source pages, draft a Kinematics structure, review lessons/checkpoints, and publish a reviewed learning pack. Review rubrics, cohort proposals and outside resources here.
- **My working**: upload handwritten images/PDFs or type working, read/edit a transcription, confirm and lock it, then request formative feedback.
- **Ask your tutor**: page-aware chat with private memory and scoped evidence. Offline mode returns labeled course-note previews. Live mode supports multilingual explanations.

All six roles have workflow implementations: Reader, Builder, Tutor, Evaluator, Curator and Scout. Live model quality is not established by offline tests; handwriting recognition and AI reasoning require deliberately enabling paid mode later.

[Setup and limits](kinematics/README.md) · [Agent architecture and endpoints](docs/AGENT_WORKFLOWS.md) · [Original agent plan](docs/AI_AGENTS_IMPLEMENTATION_PLAN.md)

This is a loopback-only, single-device prototype. Local reviewer bootstrap and browser-session ownership are not institutional authentication. Generated content and model feedback are not official course grades. No new academic content has been approved on your behalf in the main workspace.
