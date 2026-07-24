---
name: entrega-ai-eng
description: Use when working on AI Engineering entrega projects, LangChain/LCEL pipelines, structured LLM output, Pydantic schemas, CLI demos, README documentation, or hardening validation and error handling.
---

# Entrega AI Engineering

Use this skill for AI Engineering delivery work where the project must be understandable, verifiable, and robust. Prefer general architecture and quality rules over one-off implementation details.

## Delivery Principles

- Build the smallest complete pipeline that satisfies the requirements end to end.
- Keep domain contracts explicit with Pydantic `BaseModel` input and output schemas.
- Keep model/provider details behind an abstraction so the rest of the app does not depend on LangChain internals.
- Prefer async APIs for LLM execution and expose sync wrappers only when they are safe.
- Make validation and retry behavior observable through logs.
- Treat malformed input, provider failures, and invalid model output as separate failure modes.
- Keep examples runnable from the CLI with realistic sample text.
- Run static checks before reporting completion.

## Expected Project Shape

- `schemas.py`: Pydantic input and output models, field descriptions, and constrained values where useful.
- `clients.py`: abstract client interface plus concrete LLM/LCEL implementation.
- `chain.py`: thin public facade for the extraction pipeline, not the place for provider-specific complexity.
- `main.py`: user-facing CLI/menu that handles errors without dumping tracebacks.
- `example.py`: minimal non-interactive example script.
- `README.md`: setup, environment variables, architecture, usage, verification, and troubleshooting.

## Abstractions

- Define an abstract client interface for the core task, for example `extract(input_data: BaseModel) -> TechnicalExtraction`.
- The abstract interface should return domain models, not raw LangChain messages or dictionaries.
- Concrete clients may use ChatOpenAI, ChatAnthropic, LCEL, retries, and prompt templates internally.
- Keep environment-variable handling inside the concrete client or initialization layer.
- Avoid leaking provider-specific exceptions from public functions; wrap them in project-level exceptions.

## Structured Output

- Use `ChatPromptTemplate` for instructions and input interpolation.
- Compose chains with LCEL, for example `prompt | model.with_structured_output(Schema)`.
- Add `.with_retry()` around the runnable chain for transient provider failures or malformed structured responses.
- Validate the final result explicitly with the Pydantic output model even when using structured output.
- Log successful validation with useful summary metadata, not the full input text.

## Error Handling

- Separate errors into input validation, provider/model failure, and output validation.
- Raise project-level exceptions with short user-safe messages.
- Preserve original exceptions with `raise ... from exc` for debugging.
- Log detailed tracebacks only at debug level or in developer-oriented paths.
- CLI tools should catch project-level exceptions and print concise errors.
- Handle `KeyboardInterrupt` cleanly in interactive scripts.
- Guard sync wrappers against being called inside an active event loop.

## Logging

- Configure logging in entrypoints, not in library modules.
- Library modules should use `logging.getLogger(__name__)`.
- Log pipeline start, retry/attempt configuration, validation success, and controlled failure categories.
- Reduce noisy third-party loggers in CLI demos unless debugging is requested.

## README Checklist

- State what the project does in one short paragraph.
- List requirements and environment variables.
- Explain installation and execution commands using the project toolchain.
- Document the file architecture and data flow.
- Include expected JSON output shape.
- Include verification commands such as `uv run pyright` and example runs.
- Add troubleshooting notes for missing API keys, provider errors, invalid output, and type-checking issues.

## Review Checklist

- `uv run pyright` passes.
- The CLI example runs successfully or fails with a controlled message.
- Pydantic models are used for both input and output.
- Provider logic is behind a client abstraction.
- Public functions return domain models.
- Errors are categorized and wrapped.
- Logs are informative but do not expose secrets.
- README instructions match the actual commands and files.
