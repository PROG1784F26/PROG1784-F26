# PROG1784-F26

Python course workspace with two services: a Python 3.13 development container
and an Ollama container. VS Code installs Python, Pylance, the debugger, Ruff,
and Continue automatically. pytest and Ruff are installed in `/home/vscode/.venv`;
the terminal, debugger, and editor use that environment.

## Setup walkthrough

Follow steps 1–8 for your first setup. Commands marked **Host terminal** run on
your computer before entering the container. Commands marked **Container terminal**
run in VS Code after reopening the project in its devcontainer. Start terminal
commands from the `PROG1784-F26` repository folder unless a step says otherwise.

[Setup](#setup-walkthrough) · [Tutor and Direct](#learning-with-continue) ·
[Speed](#expected-speed) · [Daily use](#starting-and-ending-a-work-session) ·
[Models and settings](#models-and-continue) ·
[Engine details and GPU](#docker-and-podman-on-linux-macos-and-windows) ·
[Troubleshooting](#troubleshooting-and-stopping)

### 1. Check your computer

You need an internet connection for the first image, extension, and model
downloads. Once everything is installed, local Python development and model
inference do not need a cloud AI account or API key. Fetching new packages or
working with a remote Git repository still requires network access.

Allow roughly **17 GB for model downloads**, plus images and working files:
budget **at least 35 GB free disk**. Start with **16 GB RAM or more**; when using
a container VM, allocate **12 GB or more** for the 8B model if your computer has
sufficient memory. Leave memory for your host OS and VS Code. These are practical
starting points, not guarantees for every workload.

The default runs on **CPU** with Linux `amd64` or `arm64` containers. You do not
need a GPU. The same course configuration targets Linux, macOS, and Windows with
Linux containers. Platform verification limits are listed under [Validation](#validation).

### 2. Install and start a container engine

Choose one engine and make it available to VS Code through the **`docker`
executable**. Installing both engines is unnecessary.

| Your computer | Docker route | Podman route |
| --- | --- | --- |
| Linux | Install Docker Engine and Compose v2 for your distribution; allow your user to run Docker without `sudo` | Install Podman 5+, a Compose provider, and Docker CLI compatibility; distribution packages commonly include `podman-docker` and `podman-compose` |
| macOS, Intel or Apple Silicon | Install the matching Docker Desktop build and start it | Install Podman Desktop, create/start its Linux machine, configure Compose and Docker compatibility |
| Windows | Install Docker Desktop with the WSL2 backend, use Linux containers, and enable integration for your WSL distribution if using one | Install Podman Desktop, create/start its Linux machine, configure Compose and Docker compatibility |

Use the official [Docker installation instructions](https://docs.docker.com/get-started/get-docker/)
or [Podman Desktop installation instructions](https://podman-desktop.io/docs/installation).
For Podman Desktop, also follow its [Compose setup](https://podman-desktop.io/docs/compose/setting-up-compose)
and [Docker compatibility setup](https://podman-desktop.io/docs/migrating-from-docker/managing-docker-compatibility).
Podman alone is not enough for this Compose-based devcontainer. A shell alias such
as `alias docker=podman` is insufficient because VS Code launches an executable.

On Windows, keeping the checkout in your WSL Linux home gives better filesystem
performance. Open that folder with VS Code's WSL extension, then reopen it in the
devcontainer. Check engine access from that same WSL environment. If working
from a Windows folder instead, ensure the engine can share that folder. On
macOS, allow the container VM access to the checkout when prompted.

**Host terminal, from any folder** — check the engine before continuing:

```text
docker info
docker compose version
```

Both commands must succeed. `docker info` must reach the running engine; seeing
only a Docker client version is not enough. A Podman compatibility notice is
normal. If either command fails, start the engine/machine and finish its CLI or
Compose setup before opening the devcontainer. In VS Code, leave **Dev Containers:
Docker Path** set to `docker`.

### 3. Install VS Code and get the course repository

#### Install the VS Code desktop application

1. Open the [VS Code download page](https://code.visualstudio.com/download).
2. Choose your operating system and computer architecture (x64 or ARM64).
3. Install and launch the application using the appropriate route below.

| Operating system | Installation |
| --- | --- |
| Windows | Run the downloaded installer and follow its prompts. For the WSL workflow, install the VS Code desktop application on Windows. |
| macOS | Open the downloaded installer/archive, move Visual Studio Code into Applications, and launch it from there. |
| Linux | Install the package appropriate for your distribution, such as `.deb` for Ubuntu/Debian or `.rpm` for Fedora/RHEL, then launch VS Code. |

See Microsoft's [VS Code installation guide](https://code.visualstudio.com/docs/getstarted/overview#install-vs-code)
for platform-specific details. To use `code .` from a macOS terminal, open the
Command Palette and run **Shell Command: Install 'code' command in PATH**.
Reopen the terminal after changing PATH. Opening the folder through VS Code's
File menu also works.

#### Install the required VS Code extensions

VS Code calls its plugins **extensions**. Install these host extensions before
reopening the repository in its container:

1. In VS Code, open **View → Extensions**, or press **Ctrl+Shift+X** on
   Linux/Windows or **Cmd+Shift+X** on macOS.
2. Search for `ms-vscode-remote.remote-containers`.
3. Select **Dev Containers** by **Microsoft** and click **Install**.
4. If using a WSL checkout on Windows, also search for
   `ms-vscode-remote.remote-wsl` and install **WSL** by **Microsoft** in the
   Windows VS Code application. Follow the [VS Code WSL guide](https://code.visualstudio.com/docs/remote/wsl)
   to open your Linux folder before reopening it in the devcontainer.
5. Reload VS Code if prompted. In the Command Palette, confirm
   **Dev Containers: Reopen in Container** is available once the course folder
   is open.

For more detail, see [installing VS Code extensions](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace).

When you reopen this repository in its devcontainer, the project automatically
requests these additional extensions **inside the container**:

| Extension | Extension ID | Purpose |
| --- | --- | --- |
| Python | `ms-python.python` | Interpreter selection, running Python, and test integration |
| Pylance | `ms-python.vscode-pylance` | Python completion and type analysis |
| Python Debugger | `ms-python.debugpy` | The configured F5 debugger |
| Ruff | `charliermarsh.ruff` | Python linting and formatting |
| Continue | `Continue.continue` | Local Tutor/Direct chat, editing, and agent tools |

After step 4 below, return to **Extensions** and check the installed extensions
for the **Dev Container**. If an automatic installation failed, search for the
exact ID above and choose **Install in Dev Container** while connected. A copy
installed only under **Local** does not confirm the container copy is installed.
For Continue, use **Developer: Show Running Extensions** after opening its panel
to confirm it runs in the remote/container extension host.

#### Install Git and open the repository

Install [Git](https://git-scm.com/downloads) in the environment where you will
clone; for the WSL workflow, Git must also be available inside that WSL distribution.

The course repository is [PROG1784F26/PROG1784-F26](https://github.com/PROG1784F26/PROG1784-F26).
Run the clone command from the directory where you keep your course folders.
If your instructor assigns a personal fork or a different repository, substitute
that repository URL.

**Host terminal:**

```text
git --version
git clone https://github.com/PROG1784F26/PROG1784-F26.git PROG1784-F26
cd PROG1784-F26
code .
```

If you already have this checkout, open it rather than cloning again. If `code`
is not on your PATH, use **File: Open Folder** in VS Code and select
`PROG1784-F26`. Open the repository root containing `.devcontainer`, `.continue`,
and `examples`, not just its parent or `examples` folder.

Keep the visible course folder named **PROG1784-F26**. Internal container/project
names use lowercase for engine compatibility; there is nothing to rename there.
No host Python, host Ollama, or host Node.js installation is required for this setup.

### 4. Reopen the folder in its devcontainer

Open the Command Palette with **F1**, or **Ctrl+Shift+P** on Linux/Windows and
**Cmd+Shift+P** on macOS. Run **Dev Containers: Reopen in Container**. Use the
existing repository configuration if prompted. See the official
[VS Code devcontainer guide](https://code.visualstudio.com/docs/devcontainers/containers)
for the editor workflow.

During first startup, VS Code will:

1. Download/build the Python image and prepare the engine-specific permissions.
2. Start the Python and Ollama services.
3. Install the Python tools and remote editor extensions.
4. Install the course Continue configuration and begin downloading missing models.

The first setup can take a while because model downloads total about 17 GB;
it depends on your connection and disk speed. Watch the lifecycle terminal or
**Dev Containers: Show Container Log** for progress. Python becomes usable before
all models finish downloading. Do not send an AI request until its model is ready.

When connected, VS Code's lower-left remote indicator should identify the
**PROG1784-F26 Python + Ollama** devcontainer. The project is mounted at
`/workspaces/PROG1784-F26` inside it. That is a container path, not a host folder
you need to create. Edits in the project are saved to your host checkout.

### 5. Check Python and the model downloads

Open **Terminal: New Terminal** in the connected VS Code window. This is now the
**Container terminal**. Run:

```bash
python --version
python -c "import sys; print(sys.executable)"
python examples/hello.py
```

Expect Python **3.13.x**, the interpreter `/home/vscode/.venv/bin/python`, and:

```text
Welcome to PROG1784-F26!
```

Open `examples/hello.py` in the editor and press **F5** to try the configured
Python debugger. If the interpreter is wrong, use **Python: Select Interpreter**
and choose `/home/vscode/.venv/bin/python`.

Check model availability in the **Container terminal**:

```bash
python .devcontainer/setup.py check
```

Once downloads finish, all four tags should say `ready`:

```text
gemma4:e4b-it-qat: ready
qwen3.5:4b: ready
qwen3-vl:8b-instruct: ready
qwen2.5-coder:1.5b: ready
```

`MISSING` during the initial download means setup is not finished yet. Watch that
existing download process. If it failed or was interrupted, run **Terminal: Run
Task → Ollama: Download missing models** to resume. The task skips installed
models and reuses partial downloads. The equivalent container command is:

```bash
python .devcontainer/setup.py pull
```

Finally, check the environment and service connection:

```bash
python .devcontainer/smoke.py
```

The last line should end in `OK`. This checks the Python environment, workspace
writes, installed Continue config, adapter routes, and Ollama networking; model
availability is checked separately by the command above.

### 6. Try Continue as a tutor

Open Continue from the VS Code sidebar. Select the local **PROG1784-F26 Local
Python** configuration if prompted, then select **Tutor - Gemma 4 E4B (default)**
in its model picker. Make sure Continue is installed in the devcontainer, not
only on your host; the course config requests this automatically.

Try a small conceptual question first:

```text
What does return do in Python? Explain it briefly with a small example.
```

Then try guided help:

```text
I am new to loops. Help me start an exercise that counts negative numbers in a list.
Give me one useful next step and leave the counting logic for me to write.
```

The tutor can explain, debug your code, and propose file changes. Use Continue's
Agent mode when you want it to use tools; review tool requests and proposed diffs.
A response that merely prints code or tool-shaped JSON has not edited a file.
Check the actual file and the tool result before assuming an edit happened.

Gemma replies are checked before they appear, so you may see a wait followed by
the complete reply instead of text arriving token by token. See
[Expected speed](#expected-speed) below. AI autocomplete is deliberately off;
normal Python language completion remains available.

### 7. Choose complete assistance when you want it

Select **Direct - Gemma 4 E4B** for complete answers and requested edits. The
**Direct - Qwen 3.5 4B** and **Direct - Qwen 3 VL 8B** entries are alternatives.
Select **Tutor - Gemma 4 E4B (default)** again to return to guided learning.
The model-picker selection persists across follow-ups and new chats.

For a single Direct request while Tutor is selected, put this public phrase on
the first line of your message and your request below it:

```text
Override tutor mode: give me the complete solution

Write a complete greet(name) function that returns "Hello, " plus the name.
```

The shortcut applies to that user turn and its tool calls. The next user message
returns to the mode selected in the picker. If attached context prevents the
shortcut from being recognized, use the visible Direct picker. See
[Learning with Continue](#learning-with-continue) for the full behavior and limits.

### 8. Optionally enable GPU acceleration

Finish the CPU setup first. A GPU being present in your computer does not mean
the container can access it. Follow the [GPU setup guide](.devcontainer/GPU.md)
for the matching host drivers, device access, and override file.

For example, after configuring Docker/NVIDIA GPU support, change the
`dockerComposeFile` array in `.devcontainer/devcontainer.json` to:

```json
["compose.yaml", "compose.runtime.yaml", "compose.nvidia.yaml"]
```

For Linux Podman with configured NVIDIA CDI devices, the matching override is
`compose.nvidia-cdi.yaml`. AMD ROCm and Intel/AMD Vulkan have separate overrides.
Choose the one matching your hardware and engine; keep `compose.runtime.yaml`.
Run **Dev Containers: Rebuild Container**, then send a model request.

**Host terminal**, from the repository root:

```text
docker compose -f .devcontainer/compose.yaml exec ollama ollama ps
```

Inspect `PROCESSOR` for CPU/GPU use and `CONTEXT` for the allocated window.
An empty table means no model is currently loaded; send a request or run the
warm-up task first. To return to the portable CPU setup, remove the GPU override
from the array and rebuild.

The default Linux-container setup uses CPU on macOS, including Apple Silicon.
Apple GPU acceleration requires a separate native-host Ollama configuration,
which this walkthrough does not install. Hardware-specific instructions and
verification limits are in the linked GPU guide.

## Expected speed

The default tutor uses Gemma 4 E4B QAT with **16,384 context tokens**, up to
**2,048 output tokens**, and thinking disabled. It may make one repair before
showing a checked reply. Long conversations, larger answers, and CPU speed affect
the wait; the configured total limit is 270 seconds per incoming Gemma request.

Measured on an i9-13900H laptop with 32 GiB RAM and an optional NVIDIA RTX 5000
Ada Laptop GPU:

| Warm accepted replies | CPU | NVIDIA GPU |
| --- | ---: | ---: |
| Median wait | 12.9 seconds | 1.1 seconds |
| 95th percentile | 26.0 seconds | 4.6 seconds |

These are measurements from a small, failure-focused sample, including repairs
but excluding failed/withheld replies. They are not guaranteed timings for your
computer. See the [full evaluation](.devcontainer/GEMMA_OPTIMIZATION.md) for the
failure counts and methodology. Model-loading time can add to the first wait.

Before class, optionally use **Terminal: Run Task → Ollama: Warm up Gemma tutor**.
Gemma stays loaded for 15 minutes after use. Only one model loads at a time;
switching models may unload it. Startup does not preload models automatically.

## Starting and ending a work session

1. Start your container engine or Podman machine.
2. Open `PROG1784-F26` in VS Code and reopen it in the devcontainer if necessary.
3. Optionally warm up Gemma. Select Tutor or Direct for the help you want.
4. Write and run Python in the container terminal. Review AI changes and test
   your code. Use Git to save the work you want to keep.
5. Save your files and close the devcontainer window when finished. The configured
   shutdown action stops the two services.

Your project files live in the host checkout and survive stopping or rebuilding.
Downloaded models live in a named volume and also survive normal rebuilds.
Packages installed only with `pip install` inside the container may be lost when
it is recreated; add needed dependencies to `requirements-dev.txt` and rebuild
to preserve them. Rebuild after changing container settings or adapter code;
after changing only Continue YAML, run **Continue: Apply course config** and
reload the VS Code window if necessary.

## Learning with Continue

Continue is configured to act as a Python tutor by default. It should answer conceptual questions
directly, give useful hints and examples, and help debug your own code. It can
edit files, add scaffolding and diagnostic tests, and make focused corrections.
It should leave you meaningful work on exercises instead of writing the missing
solution for you. Routine setup, Git, formatting, and tooling receive direct help.
If setting up a tool is itself your exercise, the tutor should guide that work.

**You can choose a complete solution.** Select a **Direct** entry in Continue's
model picker. Select **Tutor - Gemma 4 E4B** to return to tutoring. The selection
stays active until you change it, including for a new exercise or chat. The
application selects the policy before calling the model; the model does not
need to decide whether you have earned or clearly requested an override.

For one request while Tutor is selected, start your message with this exact line,
and put the exercise on the following lines:

```text
Override tutor mode: give me the complete solution

Write the function for this exercise: ...
```

The public shortcut is recognized by code, ignoring capitalization and punctuation.
It covers that user turn and any associated tool calls. Your next message returns
to the picker's selected mode; select Direct for a sequence of related follow-ups.
Quoted phrases, earlier messages, urgency and the assistant's own replies do not
activate it. Continue may prepend context to a message; use the visible picker
if the shortcut is not recognized in a particular workflow. The tutor is asked
to disclose both choices when a full solution is requested. Neither choice changes
course submission requirements. To resume tutoring reliably, change the picker;
a natural-language request alone does not change the application setting.

| Request | Expected help |
| --- | --- |
| “What does `return` do?” | A direct explanation and a small example |
| “I'm new to loops; how do I start this exercise?” | A concrete first step or a different worked example, without demanding an attempt |
| “Why does my loop skip the last item?” | Feedback on your code and a focused fix when appropriate |
| “Fix my Python interpreter setup.” | Direct setup instructions or changes |
| “Write my entire exercise.” | Useful guidance and the visible Direct choice or public shortcut |
| The override phrase followed by an exercise | A complete solution with an explanation |

Ask for a shorter explanation, another example, or a slower pace as needed.
Try predicting output, running your code, and explaining why a change works.
After seeing an example or solution, trying a small variation without AI is a
useful way to check your understanding. These activities are optional, not gates
to receiving help. Run tests and question unexpected advice: the AI can be wrong.

Inline AI completion is disabled because tutor rules do not apply to autocomplete.
Its downloaded model remains available. To deliberately enable it, set
`continue.enableTabAutocomplete` to `true` in `.vscode/settings.json`; set it back
to `false` to return to the course default. This affects Continue's suggestions,
not Pylance's normal Python completions or another extension's AI suggestions.

The policy and three teaching examples live in `.devcontainer/tutor_policy.yaml`. A local adapter in the
Python container adds the selected policy to Chat/Agent requests and translates
legacy completion/Edit requests through the same policy. No third service or
host port is needed. `.continue/config.yaml` defines the visible choices. Apply
uses a separate model entry to apply an already proposed diff; autocomplete also
bypasses tutoring. Review diffs, including changes proposed by tools.

Gemma replies are checked before they appear. A reply may take longer to begin
because the adapter buffers it and can make **one targeted repair** for a detected
problem. Checks cover empty or truncated replies, reminder-only replies, tool
names and argument schemas, Python syntax in recognized whole-file tools, and
some unsupported edit/test claims. They do not execute proposed tools. If the
replacement still fails, Continue receives an error and no rejected tool calls.
A reminder-only repair is restricted to a verbal hint without code blocks or
tool calls. Retry the request or make it smaller; this never switches you to Direct.

Each incoming Gemma request has a **270-second total limit**, inside Continue's
300-second timeout. A tool follow-up is a new request with its own limit. Cancelling
closes the upstream request. Qwen, Apply, and autocomplete keep their existing
paths; the Gemma response checks do not apply to them.

Gemma stays loaded for **15 minutes after use**, subject to Ollama unloading it
when another model is selected. To avoid the initial model-loading wait, run
**Ollama: Warm up Gemma tutor** under **Terminal: Run Task** before asking a
question. This optional task uses memory; startup does not preload a model.
The one-loaded-model limit still applies. The warm-up uses the Gemma Tutor entry's
configured model and context size.

This is cooperative teaching guidance, not enforcement. In the local synthetic
tests, models sometimes provided complete solutions in Tutor mode, including
inside tool arguments despite a tutoring reply. Gemma was more promising than
Qwen for conversation, but remains fallible. See the
[research notes](.devcontainer/AI_RESEARCH.md) and
[measured CPU/GPU results](.devcontainer/AI_RESULTS.md), plus the
[Gemma optimization evaluation](.devcontainer/GEMMA_OPTIMIZATION.md).

After updating the repository's config, use **Continue: Apply course config**
under **Terminal: Run Task**, then reload VS Code if necessary. See the
[tutor evaluation guide](.devcontainer/TUTOR_EVALUATION.md) for instructor checks.

## Models and Continue

Verified against the Ollama catalog on 2026-09-08:

| Model | Purpose | Approximate download |
| --- | --- | --- |
| [`gemma4:e4b-it-qat`](https://ollama.com/library/gemma4:e4b-it-qat) | Default Tutor and optional Direct; 8B total / about 4.5B effective | 6.1 GB |
| [`qwen3.5:4b`](https://ollama.com/library/qwen3.5:4b) | Direct chat/edits and Apply; latest Qwen family with a 4B tag | 3.4 GB |
| [`qwen3-vl:8b-instruct`](https://ollama.com/library/qwen3-vl:8b-instruct) | Newest exact 8B Qwen option found in the catalog | 6.1 GB |
| [`qwen2.5-coder:1.5b`](https://ollama.com/library/qwen2.5-coder:1.5b) | Inline code completion | 986 MB |

Qwen 3.5 has a 9B model, **no 8B tag**. The 8B choice therefore uses Qwen3-VL.
For text-only Qwen3 instead, change the Qwen 8B entry to `qwen3:8b` and remove
`image_input` from its capabilities. For the newer, slightly larger family,
use `qwen3.5:9b` and update its display name.

The extra 1.5B model supports fill-in-the-middle code completion, as recommended
by [Continue's autocomplete documentation](https://docs.continue.dev/customize/model-roles/autocomplete).
All chat models explicitly use **16,384 context tokens**, with up to **2,048
output tokens** within that window. Ollama's server default matches. This leaves
more room for course instructions, code, and conversation than the previous
4,096-token setting. Autocomplete keeps its separate 2,048-token context.
Qwen uses temperature 0.2. Gemma uses its documented temperature 1.0, top-p 0.95
and top-k 64. The adapter supplies a zero presence penalty because the inspected
Continue Ollama provider does not forward that YAML option.
Thinking is disabled to keep CPU response times manageable; the 8B entry uses
the explicit Instruct variant.

The Qwen chat models advertise a 262,144-token maximum; Gemma advertises
131,072. Allocating large windows costs additional memory. The 16K course default is a practical compromise
for small Python exercises on student machines, not the model's maximum or an
ideal budget for large agent tasks. [Ollama recommends at least 64K for coding
agents and other long-context tasks](https://docs.ollama.com/context-length).
On a machine with sufficient memory, increase the chat entries' `contextLength`
to `32768` or `65536` in `.continue/config.yaml` and reapply the course config.
Set `OLLAMA_CONTEXT_LENGTH` in `.devcontainer/compose.yaml` to the same value and
use **Dev Containers: Rebuild Container** to update the server default. Continue's
per-request setting takes precedence over that server default, so changing only
the environment variable does not enlarge Continue's window.

After sending a chat message, verify the allocated `CONTEXT` on the host:

```bash
docker compose -f .devcontainer/compose.yaml exec ollama ollama ps
```

If memory is tight, lower the chat context to `8192` and use the 4B model. Start a
new conversation for a new exercise and attach only relevant files. A larger
window does not guarantee that a small model will follow the tutoring policy.
For optional thinking on the 4B entry, set `reasoning: true` and allow a larger
`maxTokens` budget and request timeout: thinking consumes generation tokens and
can otherwise exhaust the budget before a visible answer appears.

`.continue/config.yaml` is the source of truth. On container creation, setup
copies it to `/home/vscode/.continue/config.yaml`, the local config location
used by Continue. An existing different config is backed up before replacement.
Continue runs in the remote extension host. Chat and Edit use
`http://127.0.0.1:11435/tutor/` or `/direct/` inside the Python container; keep the
trailing slash. The adapter and model provisioning use `OLLAMA_HOST`, normally
`http://ollama:11434` on the Compose network. Apply/autocomplete connect directly
to Ollama. Neither service publishes a host port.

After editing the config, run these commands **inside the development container**:

```bash
python .devcontainer/setup.py config
python .devcontainer/setup.py pull
python .devcontainer/setup.py check
```

Reload VS Code if Continue does not notice the updated config. The same commands
are available under **Terminal: Run Task**. Model setup runs on each container
start, skips installed tags, retries interrupted downloads, and reports failures.
Downloads persist in the `prog1784-f26_ollama-models` named volume across rebuilds.
This fixed course volume is shared by checkouts using the same engine. Existing
tags are not refreshed automatically; this avoids surprise downloads during class.

The Ollama image is pinned to the tested version `0.33.3`, which supports these
models on both architectures. To update it deliberately, change the image tag
in `.devcontainer/compose.yaml`, run on the **host**, then rebuild/reopen:

```bash
docker compose -f .devcontainer/compose.yaml pull ollama
```

To refresh an already downloaded model after reopening:

```bash
docker compose -f .devcontainer/compose.yaml exec ollama ollama pull qwen3.5:4b
```

For a completely frozen semester snapshot, pin image digests and model digests
as well. Version tags, the Python base image tag, and model tags can change upstream.

## Docker and Podman on Linux, macOS, and Windows

The same devcontainer calls the **`docker` executable** for both engines:

- **Docker:** install Docker Engine with Compose v2 on Linux, or Docker Desktop
  on macOS/Windows.
- **Podman:** install Podman 5+ and a Compose provider, and expose it through a
  Docker-compatible `docker` executable. On Linux, distributions commonly provide
  a `podman-docker` package; `podman-compose` supplies the Compose provider tested
  here (version 1.5.0). On macOS/Windows, Podman Desktop manages the Podman machine;
  install its Compose tooling and configure
  [Docker compatibility](https://podman-desktop.io/docs/migrating-from-docker/managing-docker-compatibility).
  A Docker CLI connected to Podman's API also works. Follow Podman Desktop's
  platform-specific socket/connection instructions. A shell-only `alias docker=podman`
  is insufficient: VS Code launches the executable directly.

Verify `docker info` and `docker compose version` from the same environment where
VS Code runs. Keep VS Code's **Dev Containers: Docker Path** set to `docker`.
If `docker` points to Podman, no Docker daemon is required. Podman alone without
the compatible CLI and Compose provider is not sufficient for this Compose setup.

Before Compose starts, `initializeCommand` runs a short-lived probe using the
Python base image. It detects Podman from its container marker and examines the
user namespace. It generates the Git-ignored `.devcontainer/compose.runtime.yaml`,
adding `keep-id` only for rootless Podman. Docker gets an empty override. This
fixes rootless Podman checkout permissions without sending Docker an unsupported
setting. No host Python, Node, or shell script is required. The probe exits;
only the two course services remain running. Run **Rebuild Container** after
switching engines; each engine maintains its own image/model storage.

For manual startup, run the probe from the repository directory first, then use
both Compose files (the mount uses an absolute path; substitute your checkout):

```bash
docker run --rm --user 0 --volume "/absolute/path/PROG1784-F26/.devcontainer:/config:z" mcr.microsoft.com/devcontainers/python:1-3.13-bookworm python /config/configure_runtime.py
docker compose -f .devcontainer/compose.yaml -f .devcontainer/compose.runtime.yaml up -d --build
docker compose -f .devcontainer/compose.yaml exec --user vscode --workdir /workspaces/PROG1784-F26 python python .devcontainer/setup.py config
docker compose -f .devcontainer/compose.yaml exec --user vscode --workdir /workspaces/PROG1784-F26 python python .devcontainer/setup.py pull
```

VS Code supplies the correctly quoted host path automatically, including paths
with spaces and Windows drive letters. Use VS Code for the normal startup flow.
Manual Compose startup does not run Dev Containers' Linux user-ID adjustment;
use the VS Code flow on hosts where your user ID differs from the image's 1000.

The images support Linux `amd64` and `arm64`; no architecture is forced. This
covers x86-64 PCs, Intel Macs, and Apple Silicon Macs using Linux containers.
The default is CPU inference and does not require a GPU.

| Host | Container runtime | Default inference |
| --- | --- | --- |
| Linux x86-64 / ARM64 | Docker + Compose or Podman with Docker CLI compatibility + Compose | CPU |
| macOS Intel / Apple Silicon | Docker Desktop or Podman Desktop + Docker CLI compatibility | CPU |
| Windows 10/11 x86-64 with WSL2 support | Docker Desktop or Podman Desktop + Docker CLI compatibility; Linux containers | CPU |

On Windows, enable Docker Desktop's WSL integration. For best filesystem
performance, clone into your WSL Linux home (for example `~/courses/PROG1784-F26`),
then open it using VS Code's WSL extension and reopen in the devcontainer. A
Windows-hosted checkout also works when Docker Desktop can share that folder.
On Mac, allow the container VM access to the checkout if prompted. For Podman,
start the Podman machine and ensure the checkout is shared into it. On Linux,
your user must be able to run the selected engine without `sudo`.

Lifecycle commands run as Python inside Linux containers, so no host Bash,
PowerShell script, host Python, or executable-bit setup is required. Relative
bind mounts support different checkout paths; `.gitattributes` enforces LF
line endings on Windows. The mount's `z` option supports SELinux hosts.
The NVIDIA override is opt-in so missing GPU drivers do not break the default.

**Docker Desktop on macOS cannot pass the Apple GPU through to Ollama.** Both
services run on a Mac, but CPU generation may be slow, especially with the 8B
model. This limitation is documented in the
[Ollama FAQ](https://docs.ollama.com/faq#how-do-i-use-ollama-with-gpu-acceleration-in-docker).
Native macOS Ollama can use Metal, but requires a different host-based setup.

For an NVIDIA GPU on Linux or Windows/WSL2, install the
[NVIDIA Container Toolkit](https://docs.ollama.com/docker), then change
`dockerComposeFile` in `.devcontainer/devcontainer.json` to:

```json
["compose.yaml", "compose.runtime.yaml", "compose.nvidia.yaml"]
```

Rebuild the container. This override targets Docker/NVIDIA Container Toolkit.
There are also optional AMD ROCm, AMD/Intel Vulkan, and Podman NVIDIA CDI
configurations; see the [GPU setup guide](.devcontainer/GPU.md) for the matching
override, host requirements, and verification. Ollama chooses supported GPUs
once the engine exposes them. The base configuration stays CPU so absent GPU
devices or drivers do not prevent startup on another student's computer.

## Everyday Python work

```bash
python examples/hello.py
python -m pip install package-name
ruff check .
ruff format .
python -m pytest
```

Add course dependencies to `requirements-dev.txt` and rebuild to preserve them.
The starter does not include assignment tests; pytest reports no tests until you
add files such as `test_exercise.py`. Use the Testing sidebar once tests exist.

## Troubleshooting and stopping

### Moved checkout or an error mentioning an old folder

If the log shows `getxattr ... no such file or directory` for a previous checkout
location, the existing Python container still has that old host folder mounted.
A normal reopen can reuse it with `--no-recreate`; building the image alone does
not update an existing container's mount. This can also happen when switching
between clones because the default Compose project name is `prog1784f26`.
Use one active course checkout per engine with this default configuration.

Close the failed devcontainer window. In a **host terminal**, change to the
current repository folder and remove the old course containers:

```text
docker compose -f .devcontainer/compose.yaml down
```

This stops/removes the two course containers and their network. It preserves your
host checkout and the downloaded models in the named volume; do **not** add
`--volumes`. Container-only changes, such as packages installed without adding
them to `requirements-dev.txt`, are removed with the containers.

Open the current folder in VS Code and run **Dev Containers: Reopen in Container**.
It will recreate the containers with the current mount. The generated build-file
warnings in a stale container's labels do not mean you need to recreate those
old temporary files. Keep the uppercase course folder name; it is not the cause.

### Other problems

- **`docker` or `docker compose` not found:** finish the engine's CLI/Compose
  setup, reopen the host terminal, and verify both commands from the environment
  where VS Code runs. A Podman shell alias does not configure VS Code.
- **Cannot connect to the engine:** start Docker Desktop, Docker Engine, or the
  Podman machine. Re-run `docker info` before reopening the folder in a container.
- **Permission denied writing project files:** rebuild through VS Code so the
  runtime probe regenerates the appropriate permissions for the current engine.
  On macOS/Windows, also check that the VM can access the checkout folder.
- **“Could not produce a checked answer”:** Gemma's draft and one repair failed
  the configured checks. No rejected tool call was released. Try a smaller or
  more focused request; the error does not change Tutor/Direct mode. See the
  [evaluation](.devcontainer/GEMMA_OPTIMIZATION.md) for known limitations.
- **An empty `ollama ps` table:** no model is loaded right now. Installed models
  may still be ready; run the warm-up task or send a request, then check again.
- **Download interrupted:** run the `Ollama: Download missing models` task.
- **Model missing:** run `Ollama: Check models`. Python development still works.
- **Continue cannot connect:** confirm VS Code shows the devcontainer in its
  lower-left corner and Continue is installed in the container. In
  **Developer: Show Running Extensions**, Continue should run remotely.
  Its chat endpoint is the adapter at `http://127.0.0.1:11435/` **inside the
  Python container**. Check both service logs; rebuild after updating adapter code.
- **Continue shows another configuration:** choose the course local config;
  run `Continue: Apply course config`, then **Developer: Reload Window**.
- **Out of memory or timeout:** increase Docker's memory allocation, choose 4B,
  or reduce `contextLength` and `maxTokens` in the Continue config and reapply it.
- **Inspect service logs (host):**
  `docker compose -f .devcontainer/compose.yaml logs --tail=100 ollama`.
- Closing the devcontainer stops both services. To stop manually on the host:
  `docker compose -f .devcontainer/compose.yaml stop`.
- `docker compose -f .devcontainer/compose.yaml down` removes containers while
  preserving models. Adding `--volumes` deletes downloaded models.

Configuration format: [Continue YAML reference](https://docs.continue.dev/reference).

## Validation

`.github/workflows/devcontainer.yml` runs setup tests on Linux, macOS, and Windows,
and builds/starts the two services using Docker on Linux. These checks run after pushing to
GitHub. They check config backup and repeatability, paths containing spaces,
download failure handling, model provisioning over HTTP, and container networking.
CI does not download the 17 GB model set or run the VS Code UI.

To run setup tests locally with the development tools installed:

```bash
python -m unittest discover -s .devcontainer/tests -v
```

Inside the devcontainer, `python .devcontainer/smoke.py` also checks the actual
Python interpreter, non-root workspace writes, virtual environment permissions,
installed Continue config, both adapter routes, and the live Ollama connection.

Locally verified on Linux x86-64 with Podman 5.8.2 exposed as `docker` and
podman-compose 1.5.0: full Dev Containers CLI startup, setup and adapter integration tests,
lint/format checks, non-root file and package writes, and live Ollama networking.
The native AMD64 and ARM64 image manifests were also checked. Docker Engine,
macOS, and Windows have not been exercised interactively on this machine; the
GitHub checks are configured but have not run until this repository is pushed.

A separate fresh copy of the final files in a path containing spaces also passed first startup
(with no generated runtime file present beforehand) and the environment smoke
check, including the adapter routes. Continue's official config parser (`@continuedev/config-yaml` 1.42.0)
accepts the configuration, and CI now runs that schema check. Download tests
include truncated HTTP responses and connection resets. Chat request timeouts
are 300 seconds; autocomplete's separate timeout is 60000 milliseconds.

Platform support is based on native multi-architecture images and portable
configuration. The automated host tests do not replace an end-to-end VS Code
and Docker Desktop check on each student operating system.
