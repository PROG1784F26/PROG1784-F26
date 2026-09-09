# Local model results — 2026-09-08

Subsequent Gemma prompt, temperature, and bounded-repair experiments are recorded
in [GEMMA_OPTIMIZATION.md](GEMMA_OPTIMIZATION.md). The measurements below remain
the earlier model/quantization comparison.

Measurements: Intel Core i9-13900H, 32 GiB RAM, NVIDIA RTX 5000 Ada Laptop GPU
with 16 GiB VRAM, Linux x86-64, Podman 5.8.2 through `docker`, Ollama 0.33.3.
CPU and NVIDIA measurements ran sequentially after model downloads completed.

All requests allocated 16,384 context tokens. A fixed short explanatory prompt,
256-token output cap and identical sampling were used for timing. Cold means
unloaded from Ollama, with OS disk cache retained. Warm columns are the median
of two repeated requests; throughput is their mean generation rate. Answers
differ in length/tokenization, so wall time and throughput answer different questions.

| Model / artifact | CPU cold / warm seconds | CPU tokens/s | NVIDIA cold / warm seconds | NVIDIA tokens/s |
| --- | ---: | ---: | ---: | ---: |
| qwen3.5:4b | 12.5 / 7.9 | 14.0 | 6.0 / 1.3 | 103.5 |
| qwen3.5:4b-q8_0 | 16.4 / 10.6 | 10.6 | 9.6 / 1.6 | 75.1 |
| gemma4:e4b-it-qat | 17.0 / 9.9 | 14.2 | 8.5 / 1.3 | 97.1 |
| gemma4:e4b-it-q8_0 | 20.5 / 13.5 | 9.6 | 9.0 / 2.0 | 66.2 |
| qwen3-vl:8b-instruct | 23.6 / 15.0 | 8.4 | 11.5 / 2.2 | 66.4 |
| qwen3:8b | 20.6 / 13.0 | 8.2 | 7.5 / 1.6 | 65.3 |
| ministral-3:8b | 45.1 / 17.5 | 7.7 | 9.3 / 2.2 | 62.5 |
| mistral:7b | 21.9 / 15.2 | 9.2 | 6.6 / 1.8 | 74.5 |
| llama3.1:8b | 24.6 / 17.2 | 8.6 | 7.4 / 2.3 | 69.0 |
| lfm2.5:8b | 13.2 / 7.3 | 35.4 | 6.8 / 1.2 | 221.2 |
| granite4.2:8b | 27.4 / 20.0 | 7.7 | 7.9 / 2.3 | 60.9 |
| phi4-mini:3.8b | 12.1 / 8.2 | 16.7 | 9.7 / 1.2 | 115.6 |

LFM reached the 256-token cap in these measurements; its high throughput is not
a time-to-complete-answer result. In quality tests it emitted literal thinking
tags despite `think:false`. No other model hit this timing prompt’s output cap.

NVIDIA `/api/ps` confirmed GPU allocation and 16K context for each model. Model
digests, quantization metadata, first-content timing, output counts and GPU memory
are retained in [benchmark_results.json](benchmark_results.json). These short
prompts do not measure a full 16K history, VM resource limits, classroom load or
the slowest student machine. Longer CPU tutor responses in the exploratory
runs took tens of seconds; thinking responses exceeded 160 seconds.

## Quantization decision

Qwen Q8 reduced CPU throughput from about 14 to 10–11 tokens/s and NVIDIA
throughput from about 104 to 75. Gemma Q8 reduced CPU throughput from about 14
to 9.6 and NVIDIA from about 97 to 66. Q8 therefore has a measurable latency
and storage cost. Gemma QAT and Q8 are not a clean bit-width-only experiment:
the catalog reports different parameter metadata (7.5B versus 8.0B), and QAT
changes quantization preparation. Quality comparisons are reported separately.

## Intel integrated GPU

The Intel Iris Xe RPL-P was detected through Vulkan only after enabling
`OLLAMA_IGPU_ENABLE=1`. Actual GPU allocation was verified in `/api/ps`.
Qwen 4B measured 15.6 seconds cold / 9.6 warm at 13.4 tokens/s; Gemma QAT
measured 21.3 seconds cold / 12.6 warm at 11.6 tokens/s. Both were slower than
this CPU baseline. GPU availability does not guarantee an improvement; measure
before keeping an integrated-GPU override enabled. NVIDIA was much faster here.

AMD ROCm, Apple Metal, Docker Desktop GPU passthrough and Windows WSL GPU
integration have not been hardware-tested on this machine.

## Instruction-following findings

These are manually inspected synthetic transcripts, not an overall benchmark
score. Earlier exploratory runs used several prompt revisions and sometimes ran
alongside downloads, so their wall times should not be compared as controlled
performance measurements. The timing table above is a separate controlled run.

| Candidate or change | Observed outcome |
| --- | --- |
| Qwen 3.5 4B, Qwen3-VL 8B Instruct, Qwen3 8B | Repeated complete-solution leakage; adding context and disabling thinking did not solve the tutor boundary |
| Ministral 3 8B and Mistral 7B v0.3 | Completed the exercise while calling it a scaffold; sometimes described an override and then acted as if the student had used it |
| Llama 3.1 8B | Complete answers under pressure and after a new exercise; one invalid scaffold |
| Granite 4.2 8B | Complete solutions in text and proposed edits despite tutor instructions |
| LFM2.5 8B | Fast throughput, but literal thinking tags, solution leakage and malformed proposed file content |
| Phi-4 Mini 3.8B | Fast, but complete-solution leakage, agreement with a false premise and incorrect Git guidance |
| Qwen 4B Q8 | A better initial scaffold in one sample, followed by a full solution under pressure and a full-solution tool call |
| Gemma E4B Q8 | Conversational tutoring often worked, but a full solution appeared in an edit and in the unseen palindrome exercise |
| Gemma E4B QAT | Most promising conversational tutor among these configurations; still had false edit claims, weak replies and boundary failures |

The Q8 samples do not show a reliable tutoring improvement that justifies their
cost here. Keep the smaller artifacts as defaults and retain Q8 in the optional
matrix. This is a narrow decision for these prompts, not a claim that quantization
never affects model quality.

## Extra inference is not automatically better

Three examples with Gemma QAT avoided complete solutions in the two sampled
untouched-file requests, whereas the earlier policy leaked through an edit tool.
However, one of two conversations still gave a full new-exercise solution after
switching back to Tutor. Several replies merely repeated the Direct reminder.
One Direct reply claimed an edit had occurred without issuing a tool call.

A two-pass review experiment made one formerly incomplete file-edit response
worse: the rewrite supplied the complete missing function. The other sample
retained a valid scaffold. On an authorized edit, review did sometimes improve
tool use, so the effect depended on the case.

Best-of-two plus a same-model judge produced a valid scaffold tool call in one
sample. But the judge also selected a reply claiming a completed edit, and its explanation treated the
false claim as a virtue. Both candidates in that comparison claimed edits without
issuing a tool call, so the candidate pool itself was also defective. A formatted JSON decision is not a trustworthy decision.

These experiments used seeds 42/43 with a second candidate at seed +1000; review
used two model calls per turn, best-of-two used three. They were GPU experiments
with four scenarios (five turns) repeated twice. They do not establish a benefit
on an independent test set, and they multiply work on CPU. Neither is enabled in
the default adapter. Instructor-authored hints and deterministic checks remain
more promising next steps than unconditional self-judging.

## Selected default

Use application-controlled Tutor/Direct routing with **Gemma E4B QAT**, the
three-example policy, 16K context, a 2K output budget and one generation. Keep
Qwen 4B and Qwen3-VL 8B Instruct available for Direct assistance.

In the matched short-policy versus three-example comparison (same model,
settings, seeds 42/43, thirteen scenarios per seed), both short-policy file-edit
samples supplied complete missing logic; neither three-example sample did.
The short policy also supplied a complete palindrome solution in one sample;
the example policy did not in those two samples. Both policies still failed one
new-exercise reset and one authorized edit claim. Some example-policy responses
were too terse to teach effectively. This supports a provisional preference,
not a claim that the tutor is reliable or that the differences generalize.

Selected transcripts, including the defective drafts and judge decisions, are
preserved in [quality_examples.json](quality_examples.json). Annotations are the
coding assistant’s manual review, not instructor grading. Full local raw reports
remain Git-ignored and can be regenerated with the evaluation tooling.

## Final running configuration on CPU

After rebuilding, requests through the actual local adapter completed in 30.7
seconds for the first conceptual reply (including loading/prompt processing),
7.4 seconds for a beginner hint, 4.1 seconds for the untouched-file request, and
16.2 seconds for Direct assistance. Ollama reported **100% CPU, CONTEXT 16384**.
The Tutor file-edit reply was too limited to be good teaching, and the Direct
reply again claimed a file change without issuing a tool call. Completion of
these requests verifies the integration, not their educational quality.

The remaining classroom check is Continue's real UI and actual tool execution;
the synthetic adapter test does not replace it. Native Docker Engine, macOS and
Windows are supported by configuration but have not been exercised interactively
on this host. CI is configured for host portability and Linux Docker startup.
