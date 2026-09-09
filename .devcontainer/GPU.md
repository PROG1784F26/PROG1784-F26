# Optional GPU acceleration

Ollama automatically chooses supported GPUs **after the engine exposes them to
the container**. There is no universal Docker/Podman device request that works
on every host. Missing device paths or drivers can prevent a container from
starting, before Ollama can fall back to CPU. The course default therefore uses
CPU; enable an appropriate override on machines with GPU support.

| GPU and host | Override | Prerequisite |
| --- | --- | --- |
| NVIDIA, Linux or Docker Desktop with Windows WSL2 | `compose.nvidia.yaml` | Supported GPU/driver and Docker GPU integration |
| NVIDIA, Linux Podman | `compose.nvidia-cdi.yaml` | NVIDIA Container Toolkit and working CDI devices |
| AMD, supported Linux x86-64 hardware | `compose.rocm.yaml` | ROCm-compatible driver, `/dev/kfd` and `/dev/dri` |
| Intel or AMD, Linux | `compose.vulkan.yaml` | Vulkan-compatible GPU/driver and `/dev/dri` |
| Apple GPU, macOS | Native Ollama on the host | Metal cannot be used by this Linux container |

Check [Ollama's hardware support](https://docs.ollama.com/gpu) for your exact GPU
and drivers. The [container instructions](https://docs.ollama.com/docker) describe
NVIDIA, ROCm, and Vulkan setup. For Podman NVIDIA, follow
[NVIDIA's CDI guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/cdi-support.html)
and verify `nvidia-ctk cdi list` on the engine host. A Podman VM must itself have
GPU access; installing a host GPU driver alone is insufficient.

## Enable one backend

Append **one** GPU override to `dockerComposeFile` in `devcontainer.json`, for
example for Intel/AMD Vulkan:

```json
["compose.yaml", "compose.runtime.yaml", "compose.vulkan.yaml"]
```

Use **Dev Containers: Rebuild Container**. Keep `compose.runtime.yaml`: it contains
the engine-specific workspace permission settings. To return to portable CPU
startup, remove the GPU override and rebuild. Do not commit a machine-specific
selection as the course default.

The ROCm image is pinned to `0.33.3-rocm`; its published manifest is Linux AMD64
only. The Vulkan override uses the standard pinned image, maps only `/dev/dri`,
and explicitly enables Vulkan and integrated GPUs (`OLLAMA_IGPU_ENABLE=1`).
The latter is needed in Ollama 0.33.3: discovery otherwise logs that it is dropping
the integrated GPU. See [Ollama discovery code](https://github.com/ollama/ollama/blob/v0.33.3/discover/runner.go). It does not require AMD's `/dev/kfd` on Intel.
Windows AMD/Intel support in native Ollama does not imply that Docker Desktop
passes those GPUs through: the overrides above target Linux device access.

For rootless Podman, the host user needs permission to access the selected GPU
devices. If access comes through supplementary groups, use the `crun` runtime
and append `compose.podman-groups.yaml` after the GPU override. That supplement
preserves the user's host groups. Do not select it with Docker. SELinux may
also require a host-specific device policy; follow the vendor/runtime guidance
instead of running the course container privileged.

On the tested SELinux host, NVIDIA CDI could see the devices but reported
insufficient permissions until the Ollama container used `label=disable`.
If you encounter that same label-policy failure, append
`compose.gpu-selinux.yaml` after the selected GPU override and rebuild. This
disables SELinux container labeling for Ollama only; it is an explicit host-specific
exception, not a portable default. An administrator-provided device policy can
avoid that exception.

## Verify actual use

Send a model request first, then run on the host:

```bash
docker compose -f .devcontainer/compose.yaml exec ollama ollama ps
docker compose -f .devcontainer/compose.yaml logs --tail=100 ollama
```

`PROCESSOR` reports CPU, GPU, or a split, and `CONTEXT` reports the allocated
window. A running server alone does not prove GPU use. Limited VRAM may cause
partial CPU offload; reduce context or select a smaller model if needed.

For Apple Silicon acceleration, a separate native-host Ollama setup would be
needed, including changing both provisioning and Continue's endpoint and making
the host service reachable from the Python container. The default two-container
setup remains CPU on macOS. See the
[Ollama macOS container limitation](https://docs.ollama.com/faq#how-do-i-use-ollama-with-gpu-acceleration-in-docker).

The override files have Compose configuration checks. NVIDIA CUDA inference was
verified on Linux with an RTX 5000 Ada Laptop GPU (16 GB), Podman 5.8.2 through
`docker`, and a temporary CDI specification. The host needed a container-specific
SELinux label exception for that experiment; it is not enabled in the portable
course configuration. No privileged container or host driver installation was used.
AMD ROCm and native Apple Metal have not been hardware-tested here. Intel Iris Xe Vulkan inference was also verified after enabling integrated GPUs;
it was slower than this host’s CPU for the two tested models. See the
[measured results](AI_RESULTS.md).
