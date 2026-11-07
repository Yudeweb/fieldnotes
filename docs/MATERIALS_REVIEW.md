# Physics 1 materials review

Inspected on 7 November 2026. Source folder: `/Users/yusufdenizcelik/Downloads/Material (5)`. Original files were read, not modified. No course content was sent to an AI provider.

This is a structural/content triage, not academic approval of every question or formula. The user is the demonstration reviewer. See [machine-readable manifest](materials-manifest.json) and [prototype implementation plan](../PHYSICS1_PROTOTYPE_PLAN.md).

## Inventory

65 files, 327,295,780 bytes (about 312 MiB): 57 PDFs with 1,697 pages, six PowerPoint presentations with 41 slides, one spreadsheet and one video. PDF and PowerPoint text extraction completed without parser errors. Spreadsheet cells and video contents were not analyzed.

| Folder | Files | PDF pages | PowerPoint slides | Treatment |
|---|---:|---:|---:|---|
| Lessons | 22 PDFs | 1,301 | — | Primary lecture-source candidates, pending review |
| Exercises | 21 PDFs + 6 PPTX | 281 | 41 | Practice sources; separate questions and worked solutions |
| Mock_mcqs | 3 PDFs | 62 | — | Mixed questions/solutions; do not release original PDFs in simulation mode |
| Past_exams | 2 PDFs | 10 | — | Exam candidates; provenance/date and question boundaries need review |
| Exams_solutions | 5 PDFs | 20 | — | Reference solutions, some with prompts on the same page |
| Notes_for_exam | 1 PDF | 4 | — | Compact formula reference; not evidence of permission to use it in an exam |
| Laboratory | 3 PDFs + 1 XLSX | 19 | — | Deferred laboratory extension |
| Root video | 1 MP4 | — | — | Deferred transcription; do not interpret its filename as proof of content |

## What the files change in the implementation

### 1. Support native PowerPoint question imports

Exercises 1, 2, 3, 10, 11 and 12 include `.pptx` sources. Extract text, slide relationships and diagrams while preserving slide numbers. Render/import image-based slide content rather than relying solely on XML text. The Lesson 12 deck has only 20 extracted text characters across three slides and two embedded media files, so it needs visual inspection before question extraction.

Examples:

- [Lesson 1 questions](</Users/yusufdenizcelik/Downloads/Material (5)/Exercises/Lesson 1/Esercitazione 1.pptx>) include linear motion, braking and projectile exercises.
- [Lesson 2 questions](</Users/yusufdenizcelik/Downloads/Material (5)/Exercises/Lesson 2/Lesson 2.pptx>) cover multidimensional/projectile motion and circular motion.

Some solution pages contain Italian even though the main course language is English. Preserve original wording and label translations rather than assuming every source page is English.

### 2. Vision is essential for existing course solutions, not only student submissions

160 of the 1,697 PDF pages contain fewer than 80 extracted characters, including 136 exercise pages. This threshold identifies pages to inspect, not necessarily scans: some are title pages or sparse diagrams. Visual samples confirm handwritten derivations and scanned worked solutions.

- [Lesson 2 solutions](</Users/yusufdenizcelik/Downloads/Material (5)/Exercises/Lesson 2/Lesson 2 solutions.pdf>): 20 pages, with 15 flagged as low text; page 3 visibly contains handwritten equations.
- [Lesson 12 solutions](</Users/yusufdenizcelik/Downloads/Material (5)/Exercises/Lesson 12/12 solved.pdf>): both pages have essentially no extracted text; a rendered sample contains scanned handwritten force diagrams and working.

Add a source-ingestion transcription workflow with reviewer confirmation. Keep it distinct from student-answer transcription: source material requires reviewer confirmation, student work requires the student's confirmation. Neither pipeline may silently fix the author's mathematics.

### 3. Solution separation requires regions, not only pages

The three mock-question PDFs interleave questions and solutions. The May 26 mock has a highlighted correct option and a worked solution on the same page. Removing only pages headed “Solution” would fail.

For an assessment candidate, reconstruct the question and choices in an editable question record, attach a separately reviewed question-only diagram, and keep the reference answer in restricted storage. Do not offer the original mixed PDF through the student source viewer during an attempt. Avoid redaction that merely paints over recoverable text or annotations.

Examples: [May 26 mock, page 1](</Users/yusufdenizcelik/Downloads/Material (5)/Mock_mcqs/20260526_mcq_exe.pdf>), [September problem with solution on its first page](</Users/yusufdenizcelik/Downloads/Material (5)/Exams_solutions/20260910/Problem1.pdf>).

### 4. Deduplicate retrieval evidence without deleting source provenance

Lecture decks contain repeated recap slides. A conservative normalized-text comparison found 151 repeated-text groups and 160 redundant page occurrences among lecture pages with more than 150 non-whitespace characters. This is not proof that page images or diagrams are identical. Preserve every source location, group candidate duplicates and avoid filling a retrieval context with several copies of the same explanation.

Past exams also reuse mock questions: the bicycle/traffic-light prompt appears in both the [May 26 mock](</Users/yusufdenizcelik/Downloads/Material (5)/Mock_mcqs/20260526_mcq_exe.pdf>) and [past-exam MCQs](</Users/yusufdenizcelik/Downloads/Material (5)/Past_exams/20260915/20250915_MCQs.pdf>). Link reused questions into families. Do not treat a student who already practiced an identical prompt as demonstrating fresh independent mastery, or place the same question family on both sides of an evaluation split.

### 5. Separate administrative notices and optional depth

Lecture files contain time-specific class/laboratory notices and sections explicitly labeled optional in-depth study. Tag administrative pages separately from physics evidence, retain notice dates and mark optional material. A general tutor query must not treat an old timetable notice as current course policy or optional enrichment as compulsory checkpoint content.

### 6. Keep provenance conflicts visible

`Past_exams/20260915/` contains files whose names start with `20250915`. The inspected MCQ heading has a blank date field and does not resolve the year. Some 2026 lecture filenames also contain older academic-year footer labels. Store filename date, folder date and observed document label separately; leave the actual exam date unverified until reviewer confirmation.

Do not rename originals or silently select a year. Use neutral labels such as “Imported past-exam set — date pending review” in the prototype.

## Initial syllabus coverage

The supplied lecture text supports measurement/uncertainty, vectors and kinematics, Newtonian dynamics, oscillations, work/energy, momentum, gravitation, relative motion, rigid bodies and thermodynamics through entropy. This establishes candidate coverage, not a complete objective-by-objective audit.

**Fluid mechanics is a confirmed source gap for the prototype.** Keyword review found fluid references in introduction/syllabus pages and fluid questions in past exams, but no dedicated teaching section in the extracted lecture text. The user confirmed that these are all available materials and requested that the gap be marked for now. This is not proof that every source page is devoid of fluid content. Keep the fluids level visibly incomplete; do not invent official teaching material or assume missing lectures will arrive. Any future supplementary explanation needs explicit provenance and review before publication or scored use.

Other detailed objectives, including cylindrical-coordinate kinematics, still need a page-level coverage audit. An isolated keyword occurrence is not sufficient to mark an objective covered.

## Recommended first complete learning unit

Start with **linear motion and introductory projectile motion**, a prototype learning unit spanning the draft map's early kinematics levels.

| Purpose | Selected material |
|---|---|
| Constant-acceleration theory | March 3 lecture, PDF pages 21–33 |
| Projectile theory | March 5 lecture, PDF pages 26–38 |
| Practice | Exercise Lesson 1 slides 3–7, Lesson 2 slides 2–3 |
| Worked-reference testing | Lesson 1/2 solution PDFs; some pages need vision |
| Short assessment | Reviewed kinematics MCQs extracted from mock PDFs |
| Boss candidate | Past-exam Exercise 1A, page 1 of the mixed exercise/solution PDF |

The boss candidate asks about trajectory angles without explicitly saying at launch; its worked answer evaluates at x=0. Flag this for reviewer clarification. If the imported prompt is edited to say “initial launch angles,” label it an adaptation, retain the original wording and record the review decision.

See [first-unit draft](LEVEL_01_KINEMATICS_DRAFT.md). It remains unpublished and unapproved.

## Boundaries and next actions

- The PDF/PowerPoint inventory and representative visual checks are complete. Not every page has been visually reviewed.
- No OCR/vision transcription, API call, external upload, publishing or answer approval has occurred.
- Keep laboratory/spreadsheet analysis and lecture-video transcription outside the initial demo.
- Build ingestion around this manifest, exact source locations, mixed question/solution regions and reviewer-confirmed visual transcriptions.
- The fluid-mechanics gap is recorded per user instruction. Keep the past-exam date unverified pending clarification; use the proposed kinematics unit as the initial draft.
