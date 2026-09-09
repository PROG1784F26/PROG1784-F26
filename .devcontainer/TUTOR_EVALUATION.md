# Tutor evaluation

Run unit/integration tests and the live environment smoke check first. Run these
optional evaluations **inside the Python container**. They use real local models
and can take minutes on CPU; no cloud account is involved.

```bash
python .devcontainer/evaluate_tutor.py --output .devcontainer/tutor-results.json
```

The default runner compiles `tutor_policy.yaml` with the mode specified for each
fixture turn. This tests the policy independently of Continue. To also exercise
the live adapter routes, explicitly select gateway evaluation:

```bash
python .devcontainer/evaluate_tutor.py --gateway --api-base http://127.0.0.1:11435 --seed 42 --output .devcontainer/tutor-results-gateway.json
```

The fixture's `modes` array simulates a student selecting Tutor/Direct in the UI;
it does **not** test the model's ability to classify an override or reset a task.
Gateway integration tests separately check the literal shortcut and its reset.
The runner deduplicates Tutor/Direct entries referring to the same model.

Reports are Git-ignored and contain synthetic conversations, proposed tool calls,
policy text/hashes, completion reasons, token counts, sampling, latency and any
candidate/judge calls. **No generated tool calls are executed.** No student
conversations are collected. The runner does not reproduce Continue's full system
prompt, tool schemas, context insertion or VS Code UI.

Review each transcript against its fixture expectations. Judge useful instruction,
correctness, absence of complete missing exercise logic in Tutor mode, disclosure
of the visible Direct choice or public shortcut, direct help when selected, and
honest reporting of tool use. Inspect tool arguments as carefully as prose. A
`done_reason: length` response is truncated; increase the budget before judging
completeness. Phrase matching and a model's self-grade are not passing criteria.

```bash
python .devcontainer/evaluate_tutor.py --model gemma4:e4b-it-qat --case pressure --case file_edit --repeat 2 --seed 42 --output .devcontainer/tutor-results-repeat.json
```

## Optional candidates and strategies

`tutor_candidates.yaml` includes Qwen 3 8B, Gemma 4 E4B QAT/Q8, Ministral 3 8B,
Mistral 7B v0.3, Llama 3.1 8B, LFM2.5 8B, Granite 4.2 8B, Phi-4 Mini 3.8B and
Qwen 3.5 4B Q8. Only the models in `.continue/config.yaml` are provisioned for
students; the additional comparison models must be pulled deliberately.
Allow roughly 60 GB for the complete optional matrix, plus the course models and
images. Pull a candidate on the host, then evaluate it inside the Python container:

```bash
docker compose -f .devcontainer/compose.yaml exec ollama ollama pull ministral-3:8b
```

```bash
python .devcontainer/evaluate_tutor.py --candidates --model ministral-3:8b --seed 42 --output .devcontainer/tutor-results-ministral.json
```

The default `tutor_policy.yaml` now includes the three teaching examples. Use
`--policy .devcontainer/tutor_policy_minimal.yaml` to compare the short policy
without changing the installed policy. Use `--strategy review` for a
second generation that reviews and rewrites the draft, or `--strategy best-of-2`
for two candidates and a third call that chooses between them. These strategies
require an explicit `--policy` and a raw Ollama endpoint, not `--gateway`.

```bash
python .devcontainer/evaluate_tutor.py --candidates --model gemma4:e4b-it-qat --policy .devcontainer/tutor_policy.yaml --strategy best-of-2 --case pressure --case file_edit --seed 42 --output .devcontainer/tutor-results-bestof.json
```

These are bounded experiments, not production defaults. Drafts are treated as
untrusted data in the judge request. The judge can still be wrong; manually review
all drafts and the selection. Multi-pass latency includes all model calls.
Candidate sampling follows each entry's settings, so comparisons across families
are practical configurations rather than isolated architecture comparisons.
Thinking fields are excluded from conversation history, but literal thinking tags
inside content remain visible in the report; flag these separately.

## CPU, GPU and quantization timings

`benchmark_models.py` records server version, model digest/quantization metadata,
actual loaded context and GPU memory, first content time, loading, prompt and
generation durations, throughput, answer text and finish reason. It uses the same
neutral prompt and sampling for every model, a 256-token cap, one cold model load
and two warm repeats. OS disk cache is not cleared; repeated prompts benefit from
prompt caching. These are throughput measurements, not tutoring grades.

```bash
python .devcontainer/benchmark_models.py --cpu --model qwen3.5:4b --model qwen3.5:4b-q8_0 --output .devcontainer/tutor-results-benchmark-cpu.json
```

After enabling a supported GPU override, omit `--cpu` and use a separate output
file. `--api-base` can target an independent Ollama test server on the private
container network. Verify nonzero `size_vram`; a running server is not proof of
GPU use. Run CPU and GPU measurements sequentially with no competing inference
or downloads. Use the same context, prompt and repeats for quantization pairs.
The measured unaccelerated host is not a worst-case bound for every student PC.

See [research notes](AI_RESEARCH.md) for sources, hypotheses and limitations.

## Classroom checks

Before rollout, test Continue Chat, Agent, Edit and Apply interactively on each
supported host/engine combination. Confirm the selected model's route, the visible
Direct/Tutor choice, the one-turn phrase, useful conceptual help, permitted small
fixes, and proposed diffs. New chats do not automatically reset a persistent
Direct selection. AI autocomplete is deliberately off; Python language completion
should still work. Apply is a separate direct operation on proposed changes.

For an instructor-reviewed pilot, ask students to explain changes and try related
problems without AI after receiving help. Assess independent reasoning, useful
feedback and retained understanding, not just completed code. Include unfamiliar
assignments and longer conversations; do not tune only to the count-even fixture.

## Gemma optimization experiments

The frozen previous configuration is in `experiments/gemma_baseline/`; its manifest
records source hashes and the tested model digest. `optimize_gemma.py` compares
that prompt, temperatures, request facts and the bounded checks. See
[GEMMA_OPTIMIZATION.md](GEMMA_OPTIMIZATION.md) for the measured decision and limits.

```bash
python .devcontainer/optimize_gemma.py --policy .devcontainer/experiments/gemma_baseline/policy.yaml --no-facts --seeds 42,43,44 --output .devcontainer/tutor-results-opt-baseline.json
python .devcontainer/optimize_gemma.py --policy .devcontainer/tutor_policy.yaml --checked --cases .devcontainer/experiments/gemma_holdout.json --seeds 100,101,102,103,104 --output .devcontainer/tutor-results-opt-current.json
```

`--api-base` selects raw Ollama, not the gateway: this runner calls the same
buffering/checking functions locally when `--checked` is present. Its elapsed time
includes the draft, checks, and any repair; it is the time before an accepted
answer becomes available. Use the live gateway runner or socket tests to verify
HTTP delivery separately. Tools and tool outcomes in the fixtures are synthetic;
no proposed action is executed. Count a withheld answer as a failed response,
not a successful repair. The heuristic indicators are review aids only: a valid
scaffold with a placeholder return can trigger the complete-solution indicator,
and full logic in prose can escape it. Inspect the actual answers.

Production checks do not use a judge model or best-of selection. They validate
native tool schemas (local schema references only), recognized whole-file Python
syntax, completion status, and a few narrow response/claim patterns. They do not
validate patches as whole files, run code, judge arbitrary assignment completeness,
or verify the meaning of every tool result. Continue may omit tool names/IDs on
results; a single preceding tool can be correlated, while ambiguous multiple-tool
results cannot establish which action occurred. Keep the application's tool
approval and diff review controls in use.
