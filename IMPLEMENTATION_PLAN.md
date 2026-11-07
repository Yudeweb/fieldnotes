# Teaching portal implementation plan

The current narrowed specification is [Physics 1 prototype plan](PHYSICS1_PROTOTYPE_PLAN.md). This document remains the broader product background.

Planning baseline: 7 November 2026. This is a proposed implementation, not an existing system or a fixed delivery commitment.

## 1. Product goal and pilot assumptions

Build a faculty-governed AI learning portal where a whole cohort shares a reliable course knowledge base while each student receives private, adaptive tutoring. Turn official material into an approved learning map with short lessons, practice checkpoints, and exam-style level bosses. Use cohort feedback to improve teaching resources and reveal unclear course material.

Start with one course, one teaching team, and approximately 50–150 students. Assume a web application, faculty-authorized uploads, formative assessments rather than official grading, and text/PDF/slide content with some equations and diagrams. Validate these assumptions during discovery. Rights, institutional privacy requirements, course subject, document quality, and available faculty review time affect scope.

The core distinction: share course evidence and reviewed teaching resources; personalize explanations and assessment using a private student model. A shared cohort does not require a shared conversation or shared model context.

## 2. Roles, authority, and privacy

| Role | Responsibilities and access |
|---|---|
| Platform administrator | Institutions, enrollment, configuration, audit and operations. Does not automatically act as the academic approver or gain routine access to private chats. |
| Professor / academic approver | Approves curriculum, explanations, assessment rubrics, external resources, and official clarifications; sees permitted learning analytics. |
| Teaching assistant / content editor | Prepares and reviews drafts, handles escalations, proposes corrections. Publication depends on delegated course permissions. |
| Student | Uses published course content, private tutoring, practice, challenges, progress and reminder preferences. |

Faculty may need named checkpoint results for teaching support, under an explicit course access policy. That is separate from private tutoring conversations. Default dashboards show aggregated difficulties, not identifiable chat transcripts. Students should see clearly who can access assessed work and what remains private.

### Three knowledge layers

| Layer | Contents | Use and promotion rules |
|---|---|---|
| Official course knowledge | Published lecture materials, permitted book excerpts, syllabus, approved questions, rubrics, signed faculty clarifications | Primary evidence for course claims. Preserve exact document version and page/slide references. |
| Reviewed collective knowledge | Generalized explanations, FAQs, misconceptions, approved external resources, evidence about resource usefulness | Supplementary teaching material. Label its status; link to relevant official concepts. Student popularity cannot make it authoritative. |
| Private learner knowledge | Conversations, diagnostic evidence, attempts, inferred misconceptions, preferences and accessibility settings | Available only within the student's authorized context. Never retrieved for another student. |

Treat raw feedback as untrusted analytics input, not as a fourth source of course truth. Official documents can conflict: show the conflict and ask faculty rather than assuming the latest file is automatically correct. Record explicit supersession and clarification decisions.

Every knowledge item needs institution, course, course edition, source class, author, permission scope, approval state, version, provenance, and validity metadata. Confidential future exams and answer keys belong in a restricted assessment store, outside ordinary student retrieval.

## 3. Faculty workflow

1. **Create a course and enroll users.** Set academic approvers, document access, supported assessment types, release dates and notification policies.
2. **Upload official material.** Parse files asynchronously, scan uploads, extract text and visual content, preserve page/slide references and file checksums, and flag extraction problems. Unreadable equations or diagrams need correction before approval.
3. **Generate a draft learning map.** AI proposes concepts, prerequisites, learning objectives, levels, short lessons, checkpoint locations and boss coverage. Each proposal points to supporting official pages. Highlight uncovered syllabus objectives and missing prerequisites.
4. **Approve the structure.** Faculty edit ordering, merge/split levels, identify examinable topics and approve the blueprint. Approval authorizes drafting content, not immediate publication.
5. **Generate level content.** Produce theory explanations, worked examples, checkpoint questions, hints, rubrics, misconception tags and exam-like challenges from the approved blueprint.
6. **Review each level before publication.** Check accuracy, citations, scope, difficulty, question ambiguity, accepted solutions, accessibility and solution visibility. Preview the level as a student.
7. **Publish an immutable version.** Release immediately or on a schedule. Track exactly which content and question versions each student encounters.

Use explicit states: `draft → in_review → changes_requested / approved → published → superseded / withdrawn`. Keep blueprint approval separate from level publication. Faculty clarifications use the same controlled publication process.

When a source changes, find dependent lessons, FAQs, questions and cached answers and mark them for review. Retain historical attempts against their original versions; do not silently reinterpret old results. Show a warning or withdraw material affected by a significant known error. Require review before publishing the replacement.

## 4. Student workflow and adaptive tutoring

On first entry, ask for the student's goal, prior experience and preferred route. Offer a short diagnostic or a direct checkpoint attempt. Do not make confident students complete an introductory questionnaire or theory sequence to access useful practice.

Each level offers three routes:

- **Learn from scratch:** prerequisite repair, small theory units, worked examples and frequent checks.
- **Target a gap:** answer a personal question, explain a misconception, or practice a specific concept.
- **Demonstrate readiness:** go directly to checkpoints or the level boss when released and allowed by course policy.

The tutor loop is: identify intent → retrieve evidence → estimate the relevant knowledge gap → teach or provide a hint → collect an answer → evaluate → update concept evidence → recommend the next action.

The tutor should answer a clear personal question directly, asking diagnostic follow-ups only when they materially help. Initial uncertainty is acceptable. Estimate knowledge per concept rather than labeling a student globally as a beginner or advanced learner.

Start with a transparent learner model: concept status, confidence in that estimate, recent independent attempts, hint use, recurring error tags and review due date. Separate self-reported confidence from demonstrated evidence. A student can inspect and correct preferences or tell the tutor that an inference is wrong. More sophisticated knowledge tracing comes after the pilot supplies adequate data.

Personalization changes pace, examples, depth and scaffolding; it does not change course facts or passing standards. Keep a compact private summary with links to supporting attempts instead of replaying the whole conversation on every turn.

## 5. Checkpoints, bosses and gamification

For the pilot, use question types that the teaching team can validate: multiple choice, numeric answers with tolerances, and short explanations against a rubric. Add symbolic math or code execution only when required by the course; execution must be sandboxed.

Every question has a concept mapping, difficulty, source references, version, answer/rubric, partial-credit rules, hints and known misconceptions. Keep student-facing question content separate from solutions. The server decides when hints, feedback or full worked solutions are available.

Use deterministic checking where possible and rubric-based AI feedback for open responses. Ambiguous or low-confidence evaluation can produce formative feedback but must not confidently mark mastery. Provide a dispute/report button and a faculty review queue. AI feedback does not become official course grading in the pilot.

Checkpoint feedback should explain the error, link to the relevant source, offer the smallest useful hint and provide a fresh practice opportunity. Track assisted practice separately from independent evidence.

The **boss** is a past-exam or faculty-approved exam-like set covering the level's objectives, optionally timed. Clearly label authentic past questions and generated questions. A student can attempt it directly; an unsuccessful attempt recommends specific remediation rather than forcing a full restart. Use alternative forms to reduce memorization and prevent repeated exposure from inflating mastery.

Keep two separate systems:

- **XP and engagement:** meaningful practice, completed reviews and achievements. Cap repetitive rewards; do not reward chat volume or time spent stuck.
- **Mastery and readiness:** sufficient independent evidence across required concepts, followed by later retention checks. Initial thresholds are faculty-configurable and calibrated during the pilot.

Offer progress maps, optional streaks, flexible reminders, quiet hours and timezone-aware scheduling. Leaderboards should be optional and avoid exposing academic standing. An accessibility-friendly list view should work alongside the game map.

## 6. RAG for the whole course

Index the entire authorized course, but retrieve a bounded evidence set for each request. Increasing the context window is not a substitute for retrieval quality, permissions or source versioning.

### Ingestion

Store original files in object storage. Extract structured text, sections, equations, tables and diagrams with their locations. Chunk by semantic boundaries and preserve parent sections; avoid separating a formula from its definition. Save concise document and concept summaries, but never treat generated summaries as higher authority than the source.

Build keyword and vector indexes, linked to a concept/prerequisite graph stored initially as relational tables. Keep official, collective and personal stores separately addressable with enforced access policies.

### Request path

1. Authenticate the user and resolve course edition, enrollment, release rules and assessment mode on the server.
2. Classify intent: explanation, prerequisite repair, practice, solution feedback, course policy or clarification.
3. Apply authorization constraints to retrieval. Search official sources using keyword and semantic retrieval; broaden across the course when prerequisites or comparisons require it.
4. Rerank candidates, fetch relevant surrounding passages and verify that the evidence covers all parts of the question.
5. Retrieve approved collective resources separately. Attach the current student's compact private knowledge summary only for that student's request.
6. Assemble a bounded prompt with clearly labeled evidence classes, recent turns and the current objective. For broad questions, split the question and synthesize evidence from several sections rather than trusting one chunk.
7. Generate an answer with page/slide citations and distinguish course statements from supplementary examples or outside explanations.
8. Validate source permissions, version status and citation references. Citation presence alone does not establish factual support; evaluate support explicitly in testing. If evidence is missing or contradictory, acknowledge the gap and route for clarification when appropriate.

PostgreSQL with pgvector can combine vector retrieval with PostgreSQL full-text search; its documentation also describes reranking/fusion and filtered-search limitations. Start there and benchmark permission-filtered recall before adding a separate search service. [pgvector documentation](https://github.com/pgvector/pgvector)

Test contextual annotations on chunks if ordinary chunking loses necessary context. This is a candidate optimization, not an assumed benefit on the course corpus. [Contextual retrieval research](https://www.anthropic.com/research/contextual-retrieval)

### Context and cost controls

Ingest and embed each source version once, and reuse approved explanations. Start experiments with roughly 8–16 evidence passages and a configurable 12k–24k input-token ceiling; tune against actual mathematical/visual complexity and answer quality. Allow bounded retrieval expansion when evidence is insufficient.

Use a cheaper model for suitable classification and drafting tasks, and a stronger one when evaluation shows a need for complex synthesis. Select providers through a course-specific quality, privacy, latency and cost benchmark rather than committing to one model in advance.

Shared caches may hold approved explanations and eligible evidence packages. Cache keys include course/source versions, permission/release scope, language, objective and policy version. Personalized responses remain private. Recheck authorization on cache hits and invalidate affected caches after corrections or withdrawal.

The savings hypothesis is less repeated ingestion, smaller per-request context and reuse of approved resources. Each student's tutoring still requires individual inference; savings must be measured, not assumed.

## 7. Learning from cohort feedback safely

Create a controlled improvement pipeline:

`private interaction → privacy-filtered aggregate signal → candidate resource → evidence check → academic review → published collective resource → outcome monitoring`

Collect optional helpfulness feedback, resource usage, error reports and later performance on fresh questions. Segment by relevant concept and prior mastery when sample size allows. A helpfulness vote is a useful signal, not proof of correctness or learning; later checkpoint gains are also observational unless tested with a suitable comparison.

Do not copy a student's raw answer or conversation into shared retrieval. Default candidates are newly written explanations grounded in official material and aggregate misconceptions. Any intentional use of a student's contribution needs an appropriate consent/review process; removing names alone may not remove identifying details.

External resources enter as candidates with URL, author, date, concept mapping, accessibility and availability information. Check consistency with course material and permitted use before academic approval. Student suggestions and authorized web discovery can supply candidates. Popular external content must never override an official definition or rubric. Recheck links and invalidate obsolete recommendations.

Store relationships from reused explanations back to their sources, so a later correction can withdraw derived resources. Improve retrieval, content and recommendations first; fine-tuning on student conversations is outside the initial scope.

## 8. Faculty analytics and clarification loop

Provide a dashboard of frequently asked concept questions, recurrent wrong-answer patterns, hint dependence, checkpoint disputes, reported ambiguities, resource usefulness, and concepts with unusually high active study time. Show denominators and trends, not just counts. Exclude idle time where possible and treat time spent as a noisy signal, not proof of confusion.

Use configurable minimum group sizes and suppress narrow breakdowns that could identify students. Separate aggregated tutoring insights from any explicitly authorized named assessment reports.

Proposed initial escalation trigger: at least five distinct students and at least 20% of recent attempts on the affected item show the same ambiguity within seven days. Tune for cohort size. A serious correctness problem may be escalated immediately without waiting for a majority.

Deduplicate related reports into one ticket with the question/source version, aggregate evidence, representative privacy-reviewed paraphrases and a draft clarification. Send it to the in-portal faculty queue; optional digests follow configured permissions. Faculty can clarify wording, correct content, fix an answer key or explain a policy. Publish the approved clarification, update dependent resources and tell affected students. Track ticket ownership and resolution time.

## 9. Technical design and data model

Use a modular application and background workers for the pilot. Avoid a fleet of autonomous agents or microservices until a measured need appears.

| Component | Proposed responsibility |
|---|---|
| Web frontend | Student course map, tutor, checkpoints, challenges, progress; faculty authoring/review and analytics |
| Application API | Authentication, roles, course access, publication rules, tutoring orchestration, attempts, mastery and XP |
| PostgreSQL + pgvector | Structured records, full-text/vector retrieval, audit records and access policies |
| Private object storage | Original files, extracted page images and approved assets, served through authorized links |
| Background queue/workers | Parsing/OCR, indexing, draft generation, feedback clustering, cache invalidation and reminders |
| Model gateway | Provider abstraction, task policies, token limits, evidence logging, retries and evaluation hooks |
| Operations | Error monitoring, cost telemetry, backups, restore checks and deployment controls |

Choose the web/API framework according to the implementation team's skills. A TypeScript web application plus Python workers is a reasonable option if Python document-processing tools are useful; one language is also acceptable. Do not select a stack solely for AI branding.

Core entities:

- Identity: `Institution`, `User`, `Course`, `CourseEdition`, `Enrollment`, `RoleGrant`.
- Evidence: `Source`, `SourceVersion`, `Extraction`, `Chunk`, `SourceLocation`, `ResourceApproval`.
- Curriculum: `Concept`, `Prerequisite`, `BlueprintVersion`, `LevelVersion`, `LessonVersion`, `Publication`.
- Assessment: `QuestionVersion`, `RubricVersion`, `AssessmentSet`, `Attempt`, `ResponseEvaluation`.
- Personal learning: `Conversation`, `Message`, `LearnerConceptState`, `MasteryEvidence`, `ReviewSchedule`.
- Cohort improvement: `FeedbackEvent`, `AggregateSignal`, `ResourceCandidate`, `CollectiveResourceVersion`, `ClarificationTicket`.
- Governance/engagement: `ApprovalEvent`, `AuditEvent`, `ConsentPreference`, `XPEvent`, `ReminderPreference`.

Make attempts, approvals and XP events auditable and version-linked. Use idempotency keys for background jobs, assessment submissions and XP awards. A retried request must not duplicate rewards or publish twice.

Enforce permissions in server queries, storage access, search, caches, logs and exports. PostgreSQL row-level security can add database enforcement; application connections must not use roles that bypass it. [PostgreSQL row-security documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)

Treat documents, web resources and student text as untrusted input, never as instructions that can modify permissions or publish content. Keep secrets and restricted solutions out of student prompts. Review data retention, student deletion/correction workflows, model-provider handling and institution requirements before the pilot. Deletions must reach private indexes and caches as well as primary records.

## 10. Delivery roadmap

Indicative estimate: **12–16 weeks** with two experienced engineers, part-time product/design and QA support, and a committed faculty reviewer. Discovery may change this substantially, especially for scanned books, complex mathematics or institutional integration. A solo implementation should reduce scope or allow more time.

| Phase | Indicative time | Deliverable and exit gate |
|---|---|---|
| 0. Define and benchmark | Week 1 | One pilot course, source/role policy, representative corpus, 50–100 faculty-reviewed evaluation questions, workflow prototype and agreed success criteria |
| 1. Build the trusted knowledge foundation | Weeks 2–4 | Enrollment, ingestion, citations, permission enforcement, official-only retrieval and private conversations; pass isolation and retrieval tests |
| 2. Build curriculum authoring | Weeks 5–7 | Draft concept map and levels, blueprint approval, question/rubric editor, level preview and versioned publication; publish one complete reviewed level |
| 3. Complete adaptive learning | Weeks 8–10 | Diagnostics, three student routes, checkpoints, feedback, learner evidence, bosses, progress, XP and optional reminders; pass an end-to-end learner journey |
| 4. Add cohort improvement and pilot | Weeks 11–12 | Reviewed FAQs/external resources, aggregation, faculty dashboard and clarification tickets; run a supervised small-group pilot |
| 5. Harden and expand | Weeks 13–16 | Address pilot findings, load/accessibility/restore checks, source-update propagation and larger cohort release |

Build one vertical slice early: upload a small source set → generate and approve one level → student asks a cited question → answers a checkpoint → receives targeted feedback → a generalized issue appears in the faculty queue. Validate that before ingesting an entire library or adding elaborate gamification.

Defer native mobile apps, public leaderboards, cross-course personalization, automatic publication, model fine-tuning, autonomous official grading, comprehensive LMS integration and highly sophisticated knowledge tracing. Preserve hooks for later institution SSO/LMS integration without making those prerequisites for validating learning value.

## 11. Evaluation and release criteria

Agree targets with faculty before testing; the following are proposed pilot gates, not measured results:

- **Isolation:** zero observed unauthorized cross-student, cross-course, cross-institution or restricted-solution disclosures across automated and adversarial tests. A failure blocks release; passing tests is not a guarantee of perfect security.
- **Retrieval:** at least 90% evidence recall within the evaluated retrieval budget on faculty-labeled questions, including prerequisites and multi-document questions. Report by question type and course section.
- **Grounding:** at least 95% of sampled material course claims supported by their cited evidence under faculty review; unresolved critical errors block publication.
- **Abstention:** test unanswerable questions and conflicting source versions, not only questions with easy answers.
- **Assessment:** compare automated scoring to faculty scoring on a representative held-out set. Set acceptable agreement by question type; disagreements affecting mastery go to review.
- **Learning:** compare fresh pre/post questions, delayed retention, independent success and assisted success separately. Engagement and XP are secondary measures.
- **Operations:** choose a provisional p95 time-to-first-response target of eight seconds for ordinary tutoring, then verify under expected cohort concurrency. Measure full-answer latency separately; ingestion is asynchronous.
- **Governance:** every published level has an authorized approval and every shared resource has provenance; source withdrawal propagates to retrieval and caches.
- **Usability:** students can start with theory or challenge mode, inspect sources, report an issue and manage reminders; faculty can review and publish without engineering help.

Include uploaded prompt injection, malicious feedback, attempts to retrieve another student's conversation, solution leakage through hints, outdated cached answers, OCR mistakes, ambiguous rubrics and repeated XP farming in the test corpus. Faculty evaluation remains essential for subject correctness.

## 12. Cost model and decisions to settle in discovery

Do not provide a fixed monthly AI budget without a representative course workload. Track cost per active student, tutoring turn, evaluated response and generated/published level.

Estimate recurring inference cost as:

`tutoring turns × mean tutoring cost + assessment evaluations × mean evaluation cost + authoring/review-generation cost + shared-resource processing cost`

Add extraction/OCR, embeddings, storage, database/search, notifications, observability and staff review. As an example workload only, 100 students × 20 active days × 15 turns/day produces 30,000 monthly tutoring turns before assessment and authoring. Measure actual tokens and provider prices on pilot traces rather than turning this workload into an unsupported price quote.

Resolve these items in the first week:

1. Which course, languages and question formats define the pilot?
2. Which faculty roles approve content, and how much weekly review time is available?
3. What uploaded materials and past exams may be used, and which solutions are restricted?
4. What may faculty see about individual students, and which institutional privacy/accessibility requirements apply?
5. What cohort size, peak concurrency, hosting requirements and cost ceiling should the pilot support?

The pilot succeeds when students can move efficiently between explanation, practice and exam readiness; faculty can trust and revise the published material; and cohort feedback improves shared resources while private learning histories remain separate.
