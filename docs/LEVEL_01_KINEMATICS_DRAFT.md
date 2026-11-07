# First prototype unit: linear motion and projectile motion

State: draft, not academically approved or published. Reviewer: the user for the demonstration. This is an import/content specification, not an AI-generated official lesson or a running application.

Implementation update: a runnable kinematics-only draft now exists in [kinematics/](../kinematics/README.md). It expands this original linear/projectile import specification to six core kinematics units and an optional unscored coordinate extension. [content.py](../kinematics/content.py) is the current authored lesson/checkpoint/boss definition. Live AI and handwritten assessment remain unimplemented.

## Scope and source anchors

This unit spans early kinematics objectives rather than replacing the full course structure. Prerequisites: SI units, elementary algebra, vector components and basic differentiation/integration. Offer prerequisite repair rather than block direct checkpoint/boss access.

Theory anchors use physical PDF page numbers, starting at 1:

- [March 3 kinematics lecture](</Users/yusufdenizcelik/Downloads/Material (5)/Lessons/20260303_Physics_I_Kinematics.pdf>): pages 21–22 for position from velocity/uniform motion; 23–26 for acceleration; 29–33 for integration and constant acceleration.
- [March 5 kinematics lecture](</Users/yusufdenizcelik/Downloads/Material (5)/Lessons/20260305_Physics_I_Kinematics.pdf>): pages 26–38 for projectile models, components, trajectory, range, height and flight time.

Keep the original slide images available beside extracted formulas. Page selection establishes relevance, not verification of every algebraic step or expression on those slides.

## Learning path

1. **Describe motion:** position, velocity, acceleration, units and axis conventions.
2. **Solve constant-acceleration motion:** choose equations, carry units, distinguish displacement from total distance and inspect turning points.
3. **Resolve projectile motion:** set axes, split horizontal/vertical motion and state the no-drag/constant-gravity model.
4. **Connect equations and trajectories:** eliminate time, interpret slopes/launch angle and find physical intersections/ranges.
5. **Attempt the boss:** choose practice or simulation mode; evidence is recorded separately by assistance and prior exposure.

For each step, offer a short explanation, cited source, example, personal-question entry point and checkpoint. The student may skip instruction and attempt the checkpoint directly.

## Candidate checkpoints

### CP1: constant acceleration, units and sign

Source: [Lesson 1 exercise deck](</Users/yusufdenizcelik/Downloads/Material (5)/Exercises/Lesson 1/Esercitazione 1.pptx>), slide 3, with [paired solution PDF](</Users/yusufdenizcelik/Downloads/Material (5)/Exercises/Lesson 1/Exercise 1 solutions '.pdf>), question on page 3 and worked pages requiring visual review.

Import Exercise 1's initial-speed/constant-acceleration question. The direction-reversal part needs reviewer confirmation of wording and a rubric that distinguishes signed displacement from distance travelled. Do not substitute displacement for distance merely because the final velocity is negative.

Check setup, time interval, unit compatibility, final velocity and distance. Question/rubric state remains `needs_review` until the worked solution is transcribed and checked.

### CP2: projectile components

Source: [Lesson 2 deck](</Users/yusufdenizcelik/Downloads/Material (5)/Exercises/Lesson 2/Lesson 2.pptx>), slide 2, with [paired solution PDF](</Users/yusufdenizcelik/Downloads/Material (5)/Exercises/Lesson 2/Lesson 2 solutions.pdf>).

Import the two horizontal projectiles launched from different heights, asking for the initial-speed ratio for equal ranges. Accept equivalent symbolic forms under positive-height assumptions. Require reasoning that connects flight time to vertical motion and range to horizontal speed; a swapped ratio is a specific misconception tag.

This is also the first source-handwriting ingestion test because the worked reference contains handwritten mathematical steps.

### CP3: connecting projectile equations and a physical condition

Source: the same Lesson 2 deck, slide 3. Import the football pass with a specified launch angle and an interception-height condition. Separate the initial-speed part from the height-check part. Preserve the stated distances, coordinate assumptions and diagram if present. Declare the gravity value in the reviewed question rather than penalizing students for choosing 9.8 versus 9.81 without instruction.

## Boss candidate

Source: [imported past-exam exercise/solution set](</Users/yusufdenizcelik/Downloads/Material (5)/Past_exams/20260915/20250915_exercises_solutions.pdf>), page 1, Exercise 1A.

The task connects two parabolic trajectories with angles, a shared positive-height point, ranges and an initial speed. Import the prompt as a separate editable record; its worked solution is on the same page and must remain outside the student prompt/source viewer during an attempt.

Before publication:

- Confirm that the requested angles mean **initial launch angles**, as assumed by the supplied solution. Preserve and label any prompt adaptation.
- Confirm axis directions, SI-unit interpretation of polynomial coefficients, gravity and accepted rounding.
- Describe a common point on the paths without implying both projectiles arrive there simultaneously.
- Preserve the source's range-difference ordering or explicitly use a nonnegative difference.
- Keep the actual exam date unverified because folder and filenames disagree.
- Review the four-part rubric and symbolic/numeric references before allowing mastery updates.

Practice mode reveals staged hints and feedback. Simulation mode releases evaluation only at final submission and records a locked question/rubric version. Neither mode claims to proctor the student.

## Agent and application behavior for this unit

- Course Builder drafts short teaching units only from the selected source anchors and maps questions to objectives.
- Physics Tutor adapts language/depth, retains English technical terms and cites authorized original pages.
- Handwriting Reader first supports source references confirmed by the reviewer, then student submissions confirmed by the student; it does not correct wrong work.
- Assessment Evaluator receives the confirmed submission, approved rubric and deterministic check results.
- Backend records independent/assisted evidence and awards idempotent XP; it does not mark a concept mastered solely from tutor conversation.
- Cohort Curator groups safe signals such as axis confusion, distance/displacement errors and missing physical assumptions. A draft clarification enters the review queue rather than changing the question automatically.

## Demonstration acceptance

The reviewer can publish this unit from a draft, a student can ask a cited question in a chosen language, submit handwritten work, correct transcription and receive reviewed-rubric feedback. A second student cannot access the first student's conversation or upload. Repeated ambiguity becomes a review ticket. The mixed original solution PDF cannot leak through citations or downloads. All of this remains implementation work; only source triage and this draft have been prepared.
