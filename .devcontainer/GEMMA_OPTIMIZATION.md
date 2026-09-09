# Gemma tutor optimization — 2026-09-09

The default remains **Gemma 4 E4B QAT, the existing three-example policy, and
temperature 1.0**. Neither a new four-example prompt nor temperatures 0.2/0.6
demonstrated a consistent enough teaching improvement to replace it. The new
application behavior buffers Gemma replies, checks specific problems, and makes
at most one targeted repair. This improves control over detected failures;
it does **not** make this small model a reliably compliant tutor.

## What is configured

- Tutor/Direct is selected by the application. The visible Continue picker and
  public first-line override remain available. Returning to Tutor retains history;
  it does not erase earlier answers or tool results.
- Current mode and current-turn tool-result information are added to the system
  instructions. Proposed actions are distinguished from observed tool results.
- Context is **16,384**, output budget **2,048**, temperature **1**, top-p **0.95**,
  top-k **64**, presence penalty **0**, and thinking **off**.
- Gemma stays loaded for **900 seconds**, subject to replacement by another model.
  The optional **Ollama: Warm up Gemma tutor** task loads without generating an
  answer or downloading a missing model. Startup does not preload a model.
- The adapter buffers the draft and any replacement. It releases only an accepted
  reply, with native tool calls once, followed by the Ollama terminal event.
  Non-streaming Chat and legacy completion/Edit responses are supported too.
- A detected problem permits **one** repair, with the selected mode unchanged.
  Failure after that returns an error. There is no third generation, generic
  self-review, judge, automatic Direct switch, or execution of rejected tools.
- The total deadline is **270 seconds per incoming Gemma request**; Continue allows
  300 seconds. Each tool follow-up has its own request budget. Cancellation closes
  the upstream connection. Logs contain timings/check codes, not student prompts,
  drafts, or tool arguments.

The checks cover completion status/truncation, empty and exact reminder-only
replies, malformed or unknown native tools, supplied JSON schemas, syntax in
recognized whole-file Python tools, and narrow first-person edit/test claims
without corresponding current-turn evidence. Local schema references work;
remote references are not fetched. Invalid client schemas fail before inference.

Only the synthetic `edit_file(path, content)` and Continue's
`create_new_file(filepath, contents)` are interpreted as whole files. Continue's
`edit_existing_file` accepts changes with placeholders, and find/replace tools
accept fragments; these are **not** parsed as complete Python files. Code examples
and unfinished fragments in explanations are also legitimate. Python syntax is
checked with `ast.parse`, never by running generated code.

After the first holdout run exposed full code introduced by reminder repairs,
that repair was narrowed to a verbal hint: code blocks and proposed tools in
that replacement are rejected. Inline variable/function names remain allowed. The named-tool claim “I used edit_file to create…”
was also added to the narrow claim check. Other repairs can still propose tools.

These are structural and heuristic checks. Passive claims such as “The function
has been saved” can escape them. Tool-name/result matching does not establish
that the intended action succeeded. Complete algorithms in prose can still be
provided, and a syntactically valid file can still contain a whole assignment
solution or incorrect code. “Accepted” means only that the implemented checks
passed. Apply and autocomplete bypass this adapter; Qwen retains its previous
streaming path without Gemma's checks.

## Comparison and decision

The model digest was checked against the running Ollama server:
`ee665637121887cf3befff38abbb1be4ee117c7db867d97a67e29049ecd7e15f`.
Ollama was **0.33.3**. Settings and model were held constant except for the stated
prompt/temperature/facts/check changes. Experiments used native Ollama requests
and synthetic fixtures; they did not run Continue's full UI/system prompt.

1. **Screen:** 13 original scenarios, 17 turns per seed, seeds 42–44. Seven
   configurations: frozen baseline, existing prompt with facts at 0.2/0.6/1.0,
   and the compact four-example prompt with facts at 0.2/0.6/1.0. All were single
   generation, without repairs: **357 incoming requests**.
2. **Holdout:** 20 new scenarios, 21 turns per seed, seeds 100–104. Compare the
   raw frozen baseline with the existing prompt plus facts/checks at 1.0 and 0.6:
   **315 incoming requests**, plus 25 repairs. This compares configurations as
   packages; it does not isolate the causal effect of each component.
3. **Final confirmation:** after narrowing repairs, six failure-sensitive
   scenarios at seeds 200–202 on GPU, then CPU, without concurrent inference.
   This is a small repeated-scenario confirmation, not another independent
   holdout or an estimate of classroom failure rates. An initial CPU/GPU run
   exposed a harmless inline-name rejection; its fix is unit tested and the
   complete confirmation was repeated. Both runs are retained in the archive.

Screening found that the compact prompt supplied more whole exercise solutions
and sometimes imitated tool syntax in plain text. It was excluded. Temperature
1.0 with the existing prompt had fewer initial screening flags than 0.2/0.6,
so 1.0 and 0.6 advanced. Flags were inspected: a scaffold containing a placeholder
return is not a full solution, even when the simple AST indicator flags it.

| Holdout observation (105 replies each) | Frozen baseline | Facts/checks v1, temp 1.0 | Facts/checks v1, temp 0.6 |
| --- | ---: | ---: | ---: |
| Reminder-only replies displayed | 10 | 0 | 0 |
| Replies withheld after a failed repair | 0 | 2 | 3 |
| Repair attempts | 0 | 11 | 14 |
| Confirmed complete code among flagged Tutor replies | 2 | 4 | 4 |
| Native scaffold proposals, out of 5 requests | 4 | 2 | 1 |
| Native Direct edit proposals, out of 5 requests | 0 | 1 | 4 |
| GPU median response/checked-answer time | 1.123 s | 1.280 s | 1.285 s |
| GPU p95 response/checked-answer time | 2.061 s | 2.413 s | 2.501 s |

The full-code counts are reviewed findings among screening flags, **not an
exhaustive semantic failure rate**. Baseline vowel counting at seed 101 was an
incomplete scaffold, not a solution; the same applies to the 1.0 mode-transition
seed 100/vowel seed 104 and 0.6 mode-transition seed 101 outputs. The other listed
full-code flags were real exercise solutions. In each checked configuration,
two were introduced during reminder repair. This motivated the final restricted
repair rather than promotion of the original checked implementation unchanged.

Further review found false passive save claims after cancellation, missing native
calls despite code shown in Direct mode, and explanations inventing a missing
colon in an already colon-terminated fragment. Lower temperature improved one
Direct tool fixture but regressed scaffold use and did not reduce full-code
findings. Withholding is counted as failure to provide help. These tradeoffs do
not justify calling either prompt/temperature candidate a teaching-quality win;
the original prompt and temperature are retained. No student-learning outcomes
were measured.

## Final CPU/GPU confirmation

See `gemma_optimization_results.json` for exact latency, repair, and failure
counts and the recorded loaded context/VRAM. The machine is an Intel Core
i9-13900H with 32 GiB RAM; NVIDIA RTX 5000 Ada Laptop GPU, 16 GiB VRAM. CPU and GPU
were tested sequentially using the same fixtures, seeds, and final checks.
The first request follows an unload (OS disk cache is not cleared); subsequent
requests are warm. Timings include repairs and the wait before an accepted
answer is available, but exclude Continue rendering. An error response is
included in the all-request timing statistics and counted separately.

| Final confirmation metric | CPU | NVIDIA GPU |
| --- | ---: | ---: |
| Requests | 18 | 18 |
| Repair attempts | 9 | 8 |
| Replies withheld | 4 | 3 |
| Warm median, accepted answers only | 12.918 s | 1.102 s |
| Warm p95, accepted answers only | 25.984 s | 4.559 s |
| Cold first request, including error outcome | 20.139 s | 7.149 s |
| Loaded context | 16,384 | 16,384 |

The sample deliberately concentrates on earlier failure cases. The withheld
counts are not a general classroom failure rate. No request reached the
270-second deadline. Across screening, holdout, and both confirmation iterations,
**744 incoming requests** are preserved, plus their recorded repairs.

This laptop's CPU times are a useful unaccelerated reference, not a worst-case
bound for every student's computer. Identical seeds need not give identical
answers on CPU and GPU. The final small GPU sample still contained a passive
false save claim and a repaired Direct reply that printed tool-shaped JSON
instead of making a native call. Restricted verbal hints can also reveal too
much logic. These remain limitations, not passing examples.

## Reproduce and inspect

- `experiments/gemma_baseline/` freezes the previous policy, Continue config,
  gateway, and hashes. `experiments/gemma_checked_v1/` preserves the intermediate
  checked implementation used in the first holdout.
- `optimize_gemma.py` records prompts, all drafts, final replies, settings, seeds,
  policy/case hashes, timings, and screening indicators. New runs also record
  implementation hashes. It never executes generated tools.
- `benchmark_checked.py` unloads Gemma, runs the final confirmation, and records
  actual server/model/context/VRAM metadata. Run against each server sequentially:

```bash
python .devcontainer/benchmark_checked.py --api-base http://ollama:11434 --output .devcontainer/tutor-results-opt-final-cpu.json
```

The complete synthetic comparison transcripts are archived in
`experiments/gemma_transcripts.json.gz`. Python can read them with `gzip.open`
and `json.load`; the top-level keys are the original report filenames. The
summary records their SHA-256 hashes. No real student conversations are included.
Re-run with the pinned model digest to compare later changes; mutable model tags
can otherwise change the experiment.

## Validation scope

All **29 automated tests** passed, along with lint, formatting, dependency, and
Continue schema checks. The tests cover mode/shortcut/reset behavior, tool schemas and whole-file
syntax, quoting/fragment exceptions, bounded repairs, invalid responses, stream
and JSON formats, upstream/client errors, timeout, cancellation, and setup
portability. Live startup, installed config, non-root workspace access, and
Ollama networking are checked with the Dev Containers CLI and `smoke.py`.

The final build passed the full Dev Containers lifecycle both in the main
checkout and in a fresh path containing spaces. Both passed the non-root smoke
check. The optional warm-up loaded Gemma for 900 seconds. A live Direct request
returned a native Continue-schema file-creation call; a probe client wrote only
that accepted proposal to a temporary directory and returned the real success
result. The following model reply correctly acknowledged the created file but
incorrectly said calling the function would print its return value. The probe
therefore validates transport/tool integration, **not semantic correctness**.
Live Tutor Chat and legacy completion requests also returned the expected two
NDJSON events through the rebuilt adapter, with correct conceptual answers.
The temporary audit/GPU containers were removed; only the two course services
remain, with all four configured models available.

Continue's official config parser accepts the YAML. Its current Ollama provider
and native tool definitions were inspected. Interactive Continue Chat/Agent/Edit
and Apply were **not** tested here: no interactive VS Code session is available.
Linux Podman exposed through `docker` is the tested engine. Native Docker,
macOS, Windows, AMD, and Apple hardware checks remain unperformed locally; the
existing portable configuration and host CI matrix remain in place.

Sources inspected on 2026-09-09:
[Continue Ollama adapter](https://github.com/continuedev/continue/blob/main/core/llm/llms/Ollama.ts),
[create-new-file schema](https://github.com/continuedev/continue/blob/main/core/tools/definitions/createNewFile.ts),
[existing-file changes schema](https://github.com/continuedev/continue/blob/main/core/tools/definitions/editFile.ts),
[Ollama tool calling](https://docs.ollama.com/capabilities/tool-calling), and
[Ollama preload/keep-alive guidance](https://docs.ollama.com/faq).
