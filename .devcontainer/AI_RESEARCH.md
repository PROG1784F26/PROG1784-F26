# Small local models for course tutoring — 2026-09-08

The useful target is a correct, helpful teaching response delivered quickly,
including any proposed file edits. General coding scores and instruction-following
benchmarks do not measure this particular boundary. These are exploratory local
experiments, not evidence of student learning gains or a universal model ranking.

## Application-controlled assistance

Continue's visible model picker can present **Tutor** and **Direct** entries for
the same underlying model. A small loopback adapter inside the Python container
uses the selected endpoint to add only that mode's policy to the Ollama request.
This adds no extra inference call and needs no third service. It preserves
Continue's tool definitions, conversation, sampling settings, and streaming.

The application decides which policy is active; the model still has to follow
it. This distinction matters: even an unambiguous Tutor request elicited complete
solutions from Qwen 3.5 4B in our tests. Gemma did better in conversation but leaked
a solution through an edit tool. Neither the picker nor a prompt is an enforcement
boundary. Review proposed changes, and keep ordinary tool approval controls.

A literal first-line override can also be recognized by the adapter, applying
only to the latest user turn and its tool loop. This is simpler to verify than
asking a model to infer whether an override is quoted, which exercise is current,
or when a task has ended. A persistent Direct picker selection must be switched
back explicitly. Starting a fresh conversation also prevents old solutions from
biasing the next exercise, but does not itself change the picker selection.

[Continue slash prompts](https://docs.continue.dev/customize/deep-dives/prompts)
are another convenient UI affordance. They become user messages, however, so a
slash prompt alone does not make mode selection independent of the model. The
endpoint choice does. Continue's provider resolves relative API paths, so these
adapter URLs require their trailing slash. See the
[provider source](https://raw.githubusercontent.com/continuedev/continue/main/core/llm/llms/Ollama.ts).

## Strategies worth comparing

| Technique | Inference cost | Use here |
| --- | --- | --- |
| Explicit Tutor/Direct routing | One generation | Removes conditional mode reasoning; keeps the choice visible |
| Short coherent policy | One generation; less prompt processing | Avoid redundant or contradictory requirements |
| Two or three diverse teaching examples | One generation; more prompt processing | Include an edit example and an allowed small bug fix; test unseen exercises |
| Keep the same model warm | One generation; avoids reload cost | The default keeps one model for five minutes; longer keep-alive trades memory for fewer cold starts |
| Focused context | One generation; less prompt processing | Attach relevant code and course requirements; start a chat per exercise |
| Review then rewrite | Two generations | Optional experiment; must judge code and tool arguments, not just prose |
| Best-of-two plus a judge | Three generations | Experimental; two weak candidates and a weak judge may still select a bad answer |
| Deterministic checks | No extra model call | Verify schema, Python syntax, requested constraints and actual tool results where applicable |
| Retrieval of instructor-approved hints | Retrieval plus one generation | Promising future option; retrieve hints by exercise ID and learning step, not reference solutions |
| Prepared misconception feedback | Often no model call | Useful for known errors such as `=+` versus `+=`; teacher-authored feedback is predictable |

A 2026 preprint found instruction following degraded as constraints accumulated,
and that compiling the instructions helped some weaker models. It tested other
models, so applying the idea here is an inference, not a reproduced result.
[Instruction Stacking Collapse](https://arxiv.org/abs/2608.02639).

Few-shot examples can demonstrate the desired boundary more concretely than
another list of prohibitions. Many-shot research reports benefits in other
settings, but large example banks add prompt cost and do not establish benefits
for these local tutors. Start small and retain held-out exercises.
[Many-Shot In-Context Learning](https://arxiv.org/abs/2404.11018).

DeCRIM uses constraint decomposition, critique and refinement, with improvements
on instruction-following benchmarks including Mistral. That motivates a selective
review experiment, not unconditional multi-pass processing of every student turn.
[DeCRIM](https://arxiv.org/abs/2410.06458). Self-correction without reliable feedback
can also fail or make an answer worse; do not treat the model's self-assessment
as ground truth. [Self-correction limitations](https://arxiv.org/abs/2310.01798).

Apple's January 2026 AdaBoN work allocates best-of-N computation adaptively using
a reward model. It supports spending extra compute selectively, but is not proof
that simply generating two tutor replies and asking the same small model to
choose will help. Its selector and evaluation setup are different.
[AdaBoN](https://machinelearning.apple.com/research/best-of-n).

For correctness in Direct mode, syntax checks and assignment tests provide more
concrete feedback than a generic “check your answer” prompt. Passing tests does
not establish teaching quality or prevent a Tutor answer from giving too much
away. Our evaluation captures tool calls without executing generated code.

## Candidate selection

The optional matrix retains the requested Qwen 4B and 8B choices and adds:

- [Gemma 4 E4B](https://ai.google.dev/gemma/docs/core/model_card_4): approximately
  8B total parameters, 4.5B effective; explicit system and tool support. The QAT
  artifact is substantially smaller than its ordinary higher-bit variants.
- [Ministral 3 8B](https://ollama.com/library/ministral-3) and
  [Mistral 7B Instruct v0.3](https://ollama.com/library/mistral:7b): requested
  Mistral comparisons, including the newer small family.
- [Llama 3.1 8B](https://ollama.com/library/llama3.1:8b) and
  [Phi-4 Mini 3.8B](https://huggingface.co/microsoft/Phi-4-mini-instruct): older
  instruction-tuned baselines that still fit the size budget.
- [LFM2.5 8B-A1B](https://huggingface.co/LiquidAI/LFM2.5-8B-A1B): a sparse model
  with about 1B active parameters, making throughput worth measuring. Local
  tests exposed visible thinking despite `think:false` and malformed edit text.
- [Granite 4.2 8B](https://research.ibm.com/blog/introducing-granite-4-2): released
  in August 2026, with instruction, coding and tool-use focus.

Catalog claims are screening evidence only. A smaller download, fewer active
parameters, or a higher general benchmark score does not establish course fit.
Gemma's recommended sampling differs from the other quality-test configurations;
those are practical configuration comparisons, not isolated architecture tests.

## Measurement and limits

Chat requests allocate **16,384 context tokens**, with up to **2,048 output tokens**.
See [measured results](AI_RESULTS.md) for CPU/GPU timing and quality findings.

A larger context did not fix the tested Qwen instruction failures. Thinking on
Qwen 4B produced CPU responses exceeding 160 seconds and still misinterpreted
an override. Long thinking is therefore not the default fast path.

The timing utility separately measures a fixed neutral prompt with a 256-token
output cap, fixed sampling, one cold model load and two warm repeats. “Cold” means
the Ollama model was unloaded; OS disk caches were not flushed. Repeated warm
prompts benefit from prompt caching. These short prompts do not fill the 16K
window. Longer histories, model swaps, slower CPUs, VM limits and partial GPU
offload can be much slower; measured CPU timings are this machine's unaccelerated
baseline, not a bound for every student's worst case.

The Qwen Q4_K_M/Q8_0 pair compares the same nominal model at different
quantizations; the report records the distinct artifact digests. Gemma's QAT/Q8_0 comparison also changes its quantization preparation,
so attributing every difference solely to bit width would be misleading. Record
model digests, quantization metadata, actual context and GPU memory usage along
with latency. Do not choose a bigger quantization without a measured quality gain.

Full Continue Chat/Agent/Edit tests and a classroom learning pilot remain necessary.
Synthetic transcripts do not include Continue's entire system prompt, actual
student histories, real tool execution, or evidence of retained understanding.

## Educational design and a practical next experiment

A 2025 randomized study in a Harvard physics course found better immediate
post-test learning with a purpose-built AI tutor than with the compared active
class lessons. This supports testing instructional design, pacing and feedback,
but does not establish the same outcome for small local Python models or long-term
retention. [Kestin et al., Scientific Reports](https://www.nature.com/articles/s41598-025-97652-6).

A useful next course-specific experiment is an instructor-authored hint ladder:
select an exercise and a visible help level (concept, next step, scaffold, full
solution), retrieve only that level's material, and let the model explain it in
plain language. This makes progression predictable, needs little model context,
and keeps complete solutions behind an explicit student choice. It requires the
actual course exercises and reviewed hints; those materials have not been invented
or silently added here. General chat and file editing remain available.

Keep predict-run-explain and independent variations optional in the assistant;
use instructor-designed assessment outside the chat to measure understanding.
Do not turn a tutoring preference into moralizing, repetitive questioning, or an
attempt requirement for students who need a first explanation.
