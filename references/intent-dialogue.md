# Intent Dialogue

Use a short intent dialogue before deep authoring so the first version of the skill is anchored in the real job rather than in a guessed prompt shape.

## Why This Step Exists

- raw workflow material is often incomplete, mixed, or ambiguous
- the wrong boundary chosen early is expensive to repair later
- good trigger design depends on knowing what should not route here
- execution assets should follow confirmed outputs, not assumptions

## What To Capture

Ask only the questions that change the package design.

1. What recurring job should this skill own?
2. What inputs will people actually hand to it?
3. What outputs should it produce every time?
4. What near-neighbor requests should stay out of scope?
5. What quality bar matters most: speed, consistency, auditability, portability, or governance?
6. What assets already exist: docs, scripts, templates, examples, or prior prompts?
7. What constraints matter: privacy, naming, local library fit, or target environments?

## Interview Rule

- prefer `5-7` sharp questions over a long discovery questionnaire
- ask boundary questions early
- ask output questions before architecture questions
- stop once the skill can be described clearly in one sentence

## Output

The dialogue should produce:

- one clear capability sentence
- a list of real inputs
- a list of required outputs
- a short exclusion list
- one recommended archetype
- one recommended first evaluation target

## Failure Pattern

Do not continue into full authoring when the dialogue still leaves these unresolved:

- whether the request is really reusable
- which near-neighbor requests should not trigger
- what concrete deliverable the skill must return
