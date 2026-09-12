# AGENTS.md

## General Engineering Principles

When writing, modifying, or refactoring code in this project:

- Prefer simple, readable, and maintainable solutions.
- Do not over-engineer.
- Follow the existing coding style, naming conventions, file organization,
  and architectural patterns already present in the project.
- Prefer modifying existing code over introducing new abstractions.
- Keep changes as small and localized as reasonably possible.
- Do not refactor unrelated code unless it is necessary for the requested change.
- Do not introduce new dependencies unless they provide a clear and necessary benefit.
- Avoid unnecessary design patterns, wrappers, factories, registries,
  inheritance hierarchies, or abstraction layers.
- Do not create helper functions or classes for logic that is only used once
  unless doing so significantly improves readability.
- Prefer explicit code over clever or overly compact code.
- Avoid premature optimization.
- Do not add configurability for hypothetical future requirements.

## Project Consistency

Before implementing a change:

- Inspect nearby and related files to understand how the project currently
  implements similar functionality.
- Reuse existing utilities, models, configuration structures, and conventions
  whenever possible.
- Match existing naming conventions and function/class structure.
- Preserve the current project architecture unless the requested task
  specifically requires changing it.
- Do not rename existing public functions, classes, configuration keys,
  directories, or files without a clear reason.

If multiple implementations are possible, prefer the one that looks most like
the existing codebase.

## Code Quality

Code should be:

- Easy to read without extensive explanation.
- Explicit about inputs, outputs, and important state changes.
- Broken into functions only when there is a meaningful logical boundary.
- Free of duplicated logic when the duplication is significant enough to
  justify extraction.
- Commented only where the intent or reasoning is not obvious from the code.

Do not add comments that merely restate what the code does.

## Scope Control

Implement only what is required by the task.

Do not:

- Add unrelated features.
- Perform large-scale refactors while fixing a small issue.
- Rewrite working modules solely to make them "cleaner."
- Add speculative handling for situations the project does not currently need.
- Create infrastructure for possible future features unless explicitly requested.

When fixing a bug, prefer fixing the root cause with the smallest reasonable
change.

## Machine Learning Code

For training, evaluation, preprocessing, and inference code:

- Keep the training pipeline explicit and easy to trace.
- Do not hide important ML operations behind unnecessary abstractions.
- Keep tensor shapes and data flow understandable from the code.
- Reuse the project's existing dataset, vocabulary, tokenizer, model,
  training, and evaluation interfaces.
- Avoid changing model behavior while performing a code-only refactor.
- Do not silently change hyperparameters, preprocessing behavior,
  tokenization, loss computation, or evaluation metrics.
- Maintain reproducibility where the project already provides seeds or
  deterministic behavior.

## Configuration

- Prefer existing configuration files and configuration structures.
- Do not hard-code values that already belong in configuration.
- Do not move every constant into configuration unnecessarily.
- Add a configuration option only when the value is reasonably expected to
  vary between runs or models.

## AI-Generated Changes

For every meaningful block of AI-generated or AI-modified code, include:

    # AI Amended: <brief reason or description>

The comment should explain why the code was introduced or changed rather than
simply describing the syntax.

Do not add the comment repeatedly to every individual line.

## Validation

After modifying code:

- Check that imports and existing interfaces still work.
- Run the smallest relevant test or validation command when available.
- Do not claim something works unless it was actually tested.
- If testing was not possible, explicitly state what was not verified.
