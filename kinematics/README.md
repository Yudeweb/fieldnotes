# Kinematics local prototype

A Physics I course overview, one playable kinematics learning level, and a local professor/admin course-creation workspace. No other playable course levels or cloud deployment are included. An optional, budget-limited OpenAI tutor is connected. This is a local draft preview, not the planned cohort platform.

## Run

From the repository root:

```sh
python3 kinematics/server.py
```

Open `http://127.0.0.1:8765`. The server uses only Python's standard library. Choose a different loopback port with `--port 8766` if needed.

## Accounts and permissions

On the first start, run `python3 kinematics/account_setup.py` and open the printed **private, single-use** link. Choose the sole administrator’s email and password there. Do not share that link with students. Setup uses a random credential stored as a hash in SQLite; its plaintext file is owner-readable and gitignored, and is removed on successful setup. Registration never provisions an administrator, including the first registration. A unique database index prevents a second admin.

Students use `/register`; all registrations are students regardless of submitted role fields. Sign in at `/login`. The administrator alone can open `/studio`, `/agents`, all authoring/review APIs, and the student account roster. Permissions are enforced by HTTP handlers and the course/reviewer services. `/work`, the tutor, released course material and personal progress remain available to students. Private data is keyed to the account, not the current browser cookie.

`/profile` edits the name and explanation language, shows personal progress, and supports password changes with the current password. Passwords require 12–128 characters and are stored as salted scrypt hashes (N=32768, r=8, p=1). Random session cookies are HttpOnly, SameSite=Strict and expire after 14 days; only their hashes are stored. Sign-in rotates the cookie, logout revokes it, and a password change revokes other sessions. Authentication attempts are rate-limited in SQLite. The app remains HTTP loopback-only; HTTPS cookies, university SSO, email verification and account recovery are not implemented.

Initial admin setup adopts pre-account authoring drafts and reviewer records. Only the setup browser’s previous personal progress/history transfers to the owner. Other old browser data stays private and is not adopted by student registrations. A private SQLite backup is recommended before migration; never commit runtime files.

Pages:

- `/login` and `/register`: sign in and student-only registration.
- `/profile`: your profile and password; registered students are shown only to the admin.

- `/` or `/course/physics-1`: visible course-level cards with saved checkpoint progress. Only Kinematics is playable; the other eight cards are proposed outlines, with Fluids marked as a source gap.
- `/levels/kinematics`: lessons, checkpoints, original source pages and the boss.
- `/studio`: professor/admin course creator. Set the course title, code, source language and description; upload PDF/PPTX files or save an empty draft first.
- `/studio/<draft-id>`: persistent draft document library, editable categories/solution flags and additional uploads.

The visual design includes illustrated course worlds and a Kinematics journey map: purple theory nodes, amber checkpoint nodes, a gold boss encounter, progress rings and gentle animation. Reduced-motion preferences disable animation.

## Course uploads

Each file can be up to 25 MB. Choose Lecture, Practice, Past/proposed exam, Solutions, or Supplementary material, and flag mixed files containing solutions. Filename-based solution detection is only a suggestion; review the classification. Exact duplicate uploads within a draft are rejected.

Course drafts and metadata persist in SQLite. Original uploaded bytes are stored privately under `var/private/kinematics/uploads/` using server-generated names. Upload checks validate extensions and file signatures/container markers; this is not full document parsing or malware scanning. Uploaded files have no public serving route and are not added to student retrieval automatically.

Draft ownership uses the sole administrator’s account. Students cannot list, change or upload to course drafts. Sign in to the same admin account from another browser to continue authoring. Agent studio now connects local extraction, page confirmation, Kinematics structure drafts, lesson drafts, version-specific review and publication of a learning pack. These packs appear inside the existing Kinematics level; no other levels are created.

Source previews are prepared separately using `pypdfium2` (the Codex bundled Python runtime already includes it):

```sh
python3 kinematics/prepare_sources.py --materials '/Users/yusufdenizcelik/Downloads/Material (5)'
```

If running outside the bundled runtime, install `pypdfium2` into a local virtual environment first. The app itself still starts without this dependency; only missing source previews need preparation. Generated PNGs and the SQLite database live under gitignored `var/private/kinematics/`.

## Included

- Six core teaching units plus an optional coordinate extension.
- Six checkpoints with numeric feedback, staged hints and worked explanations.
- A two-task, seven-value boss with practice and 25-minute simulation modes.
- Session-scoped, persistent progress, notes, review issues and limited XP.
- An interactive no-drag projectile plot.
- Eighteen selected original lecture-page previews, served through an exact allowlist.
- Explicit draft/provenance labels and no answer keys in the initial public content payload.

Sessions resolve to authenticated accounts. Clearing a cookie signs you out; signing back in restores account data. This is not suitable for public deployment without HTTPS, identity verification and recovery. Bind remains loopback-only. Original solution PDFs, credentials and arbitrary filesystem paths are never served. The printed loopback URL is for this Mac only.

Hints and feedback are withheld within a simulation until submission. This does not prevent consulting another tab or external resources and is not proctoring. Returning to the challenge overview preserves an attempt; reloading resumes the newest unfinished attempt. The deadline is checked on the server. On expiry only previously saved answers are assessed.

## Academic status

All authored explanations, adapted questions, numeric reference values and rubrics await the user's demonstration review. No academic approval or course mastery is asserted. XP records practice, not an official mark. The coordinate extension is unscored because direct polar/cylindrical source coverage is not yet established.

Student image/PDF intake, transcription confirmation, rubric-based formative evaluation, course drafting and aggregate cohort workflows are connected. Institution accounts, scheduled reminders, automatic web discovery and formal assessment validation remain future work. Offline mode does not perform handwriting recognition or AI reasoning.

## Checks

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --check kinematics/web/app.js
```

Tests cover numeric edge cases, turning-point distance, session isolation, source restrictions, simulation withholding/locking and duplicate XP prevention.

They also cover course-map availability, persistent course creation/uploads, session ownership, unsafe/spoofed filenames, duplicate files, solution-category flags and direct page routes.


## AI tutor

Copy `.env.example` to `.env` if needed and save your key as `OPENAI_API_KEY`. Paid calls are currently disabled with `AI_PAID_CALLS_ENABLED=false` and `AI_EXECUTION_MODE=offline`. To deliberately enable live inference later, set both `AI_PAID_CALLS_ENABLED=true` and `AI_EXECUTION_MODE=live`. Do not overwrite a saved key with the example. Settings reload on each agent request. Queued offline tasks stay offline even if settings change later. Python standard-library HTTPS calls use the Responses API; no SDK installation is required.

Default model: `gpt-6-luna`, low reasoning effort, 1,800 total output tokens maximum for the tutor (including internal reasoning). Its availability was verified with the user's project and a short live course-citation check. [Official model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna) and [Responses API](https://developers.openai.com/api/docs/guides/text) were checked on 7 November 2026. Rates are explicitly allowlisted in `kinematics/ai.py`; an unpriced model fails closed. Recheck prices when changing models. The conservative meter includes an input premium for cache writes, and does not subtract cache-read discounts. It estimates usage rather than replacing provider billing.

Current default allowances:

- `AI_SESSION_BUDGET_USD=0.10`: lifetime of this account (the environment variable name is retained).
- `AI_DAILY_BUDGET_USD=0.25`: all sessions combined, UTC day.
- `AI_MONTHLY_BUDGET_USD=2.00`: all sessions combined, UTC calendar month.

A zero allowance disables dispatch. Requests reserve estimated maximum cost in SQLite before the network call, then reconcile usage. Ambiguous failures retain their reservation; there are no automatic retries. One generation runs at a time, with six requests per minute per session. Duplicate message IDs do not generate twice. Clearing the browser cookie does not reset global limits. Do not delete the local database to reset a meter. Page loads, course uploads, chat history and local retrieval make no paid calls. No hosted search, embeddings, vector stores or paid tools are enabled.

The tutor receives server-resolved lesson/question context, numeric checkpoint evidence, owned course-draft metadata when in the studio, up to three selected lecture excerpts and three recent private conversation turns. It does not receive working notes, student answer-entry fields, raw PDFs, other learners' conversations or unreviewed uploaded documents. Retrieval is local lexical ranking over the 18 allowlisted Kinematics lecture pages from `var/private/materials-inspection/inventory.json`; when that extraction is missing the tutor can give general guidance without official citations. This is a scoped prototype, not whole-course RAG. Document instructions are untrusted evidence.

Responses use a strict JSON schema. Citation identities/pages are checked against the retrieved allowlist, and rendered source buttons open the original page preview. AI explanations and authored lessons remain review-pending; official evidence, general guidance and private chat are labeled separately. Choose any explanation language in the chat; source and assessment terminology stays in English alongside translations.

Tutoring is blocked server-side whenever this session has an unsubmitted simulation, even from another page or after the timer expires. Submit from Level boss to resume help. Chat history is withheld during simulation. This is not proctoring. Tutor use for a selected lesson/checkpoint is recorded as assistance for subsequent numeric attempts; practice-boss help is recorded on unfinished practice attempts.

Private chat and run records persist in the ignored SQLite database. Calls use `store:false`, but this is not a claim of zero provider retention. All six roles now use connected, schema-validated workflows through the shared gateway. See [the workflow guide](../docs/AGENT_WORKFLOWS.md) for permissions, endpoints, local dependencies and test coverage.


## No-spend walkthrough

1. Use the private setup link to create your sole admin account, sign in, and open Agent studio. Your admin account is automatically the academic reviewer; students cannot claim that role.
2. Create/upload a course in Course studio. Open its agent workflow and choose **Show course documents → Extract locally**.
3. Compare an extracted page with **View original page**. Review its transcription and boundary. Confirm answer-free theory pages explicitly. Only lecture files without a solution flag can become official student evidence. Questions, mixed pages and solutions stay restricted.
4. Propose a Kinematics structure. The offline result is a template for review, not a source-coverage guarantee. Remove unsupported units, edit objectives/citations, and approve the exact version.
5. Draft one or all approved units. Review the theory, question, staged hints, candidate answer and rubric. Approve, then use the separate publish action. A published pack appears under **Reviewed additions** in the Kinematics level map. Source changes withdraw affected packs.
6. Approve a checkpoint reference rubric in Agent studio. In My working, enter typed working or upload a PNG/JPEG/WebP/PDF (8 MB, PDFs up to three pages). Reader previews preserve native/typed text; offline handwriting must be transcribed manually. Confirm uncertainty checks and lock the snapshot before evaluation. Offline evaluation gives local numeric checks and a reasoning-review placeholder. It awards no AI XP or official grade.
7. Curator runs only on eligible aggregate groups of at least five distinct student accounts. A single-user demo reports insufficient data. Resource Scout fetches only the public HTTPS page you supply; offline relevance is a labeled review template. Neither publishes shared material automatically.

Local extraction uses `pypdf`, `pypdfium2` and Pillow. PowerPoint text extraction uses the standard library. The app discovers the installed Codex Python runtime on this Mac; set `DOCUMENT_PYTHON` to another Python executable with those packages when moving the project. Extraction runs in a subprocess with a time limit, page/size limits and no OpenAI credentials.

Coarse study-time intervals and structured question-help signals stay local. Cohort display suppresses groups below five signed-in student accounts. Self-registration is not university identity verification. An explicit wrong-reference report can create a reviewer clarification ticket immediately. Private notes, chat text and handwritten work do not enter cohort model inputs. Sharing a disputed submission with the reviewer requires a separate student consent checkbox.

## Current live configuration

The owner explicitly enabled paid calls on 7 November 2026. The private `.env` now has `AI_PAID_CALLS_ENABLED=true`, `AI_EXECUTION_MODE=live`, `OPENAI_TUTOR_MODEL=gpt-6-luna`, and `AI_REASONING_EFFORT=low`. The API key is unchanged and never tracked. `.env.example` remains offline by default. Existing budget caps are unchanged.

GPT-6 Luna is the recommended starting model for this cost-sensitive Kinematics prototype: it supports text/image input, structured outputs and adjustable reasoning at $0.10 input / $0.50 output per million tokens under standard short-context pricing. See the [official model specification](https://developers.openai.com/api/docs/models/gpt-6-luna). This is a workload/cost choice, not a benchmark claim that it is the most accurate physics model. Stronger models are not selected or retried automatically.

The gateway sends low reasoning effort for all roles, reserves for the entire output allowance, and meters all reported output tokens, including reasoning. Unknown models and unsupported reasoning configurations fail before dispatch. Limits and no-auto-retry behavior remain enforced. Two tiny synthetic live checks validate API access, structured numeric output, elementary kinematics and an English/Italian explanation; they do not validate real handwriting accuracy or exam-level grading.
