# OpenCode 200-task autonomous queue (Windows)

This is a **local, single-process supervisor**, not a ChatGPT automation. It runs consecutive
`opencode run` invocations while its PowerShell window and Windows computer stay awake.
No OpenCode plugin, paid API, Docker, Ollama, Task Scheduler job, or daemon is added.

## Initial setup (PowerShell from the repository)

Install OpenCode separately and make sure its configured provider/model already works.
Fetch or check out the supervisor feature branch (until merged):

```powershell
cd C:\Users\X1\Projects\VoiceBlueprintPro
git fetch origin
git switch feat/opencode-200-task-supervisor
opencode --version
opencode run --help
py -3 tools\opencode_queue.py init
py -3 tools\opencode_queue.py status
```

**Before running the queue, ensure OpenCode can make safe non-interactive changes with
your chosen permission settings.** The supervisor cannot bypass mandatory provider,
GitHub, OS, or security confirmations. It must not be granted destructive blanket permissions.

Start with **one supervised attempt** to verify OpenCode syntax, model access, receipts
and repository permissions without exhausting a free model quota:

```powershell
py -3 tools\opencode_queue.py run --once --model opencode-go/hy4-flash-free
py -3 tools\opencode_queue.py status
```

If your configured model identifier differs, change the `--model` argument.
Do not assume `hy4-flash-free` remains free or available; select an actual
connected model shown by OpenCode. If your default model is already configured,
omit `--model`.

Once the focused attempt succeeds, **run the ongoing loop**:

```powershell
py -3 tools\opencode_queue.py run --model opencode-go/hy4-flash-free
```

Each task may take up to 7200 seconds by default; override with `--timeout 3600`
if needed. An OpenCode nonzero exit or missing evidence receipt is not considered success.
The supervisor re-invokes OpenCode for the next ready task without another user prompt.

## Queue structure and anti-overlap behavior

- The queue contains exactly **200 unique steps**: 20 project-specific workstreams ×
  10 nonoverlapping phases (audit, reproduce, requirements, implementation, tests,
  recovery, integration, documentation, acceptance).
- These are **candidate engineering steps**, not claims that 200 bugs exist.
  For a healthy module, a step may conclude with a verified no-op. Existing PR #6
  (archives and identity), PR #7 (Android stamping and packaging), PR #9
  (model asset integrity), and other PRs must be reconciled before editing.
- Inside each workstream, the ten phases have explicit dependencies. An unrelated
  workstream can proceed when another becomes blocked. **Only one OpenCode
  process/task runs at any instant**, so concurrent file overlap is impossible
  within this supervisor. Do not run another OpenCode editor against the same
  checkout concurrently.
- A global exclusive local lock rejects a second supervisor. Failed tasks get
  at most **two invocations**, then become blocked; downstream dependent steps
  remain waiting while independent tracks continue.
- The supervisor checkpoints state to `.opencode-queue/queue.json` via atomic
  file replacement. This directory is ignored by Git. It contains task receipts
  and must be retained locally across sessions; do not delete it or commit it.
- Evidence receipts are **agent reported**, not an independent verification of
  CI or runtime success. Review GitHub checks and real hardware before merging.

## Recover after a stop

Reopen the PowerShell window, confirm no other supervisor/OpenCode run is active,
and use the same `run` command again. If the supervisor died during an active
task, that invocation remains charged; it is retried only if attempts remain.

If `supervisor.lock` remains after an abnormal shutdown, check Task Manager
and the process ID written to the lock before removing it manually. **Never
delete a live supervisor lock.** Closing the terminal or sleeping Windows
stops progress. This tool does not automatically start itself after reboot.

The roadmap source of truth remains `docs/ROADMAP.md`; the local queue is
an **execution schedule**, not a competing business roadmap.

## Acceptance and diagnosis

Run focused tests locally:

```powershell
py -3 -m pytest -q tests\test_opencode_queue.py
```

Expected behavior: unique IDs, valid acyclic dependency graph, idempotent
initialization, lock exclusion, valid receipts, two-attempt policy, crash
recovery and serial progression.

Current branch may be a **draft PR**: source changes are not equivalent to
Windows acceptance. Confirm the test exit code and CI before landing the branch.

## Known limitations

- The queue is a 200-step fixed bounded plan; it does not invent new tasks or
  replenish itself after completion. Refresh only by an intentional reviewed
  update, preserving task identifiers and existing progress.
- The process must remain running; it cannot keep coding when Windows shuts
  down or the model provider is unavailable.
- Existing OpenCode CLI flags may differ by installed version: inspect
  `opencode run --help` if invocation fails.
- No automatic privileged GitHub merges, release/publish actions, security bypass,
  or deletion of user work. The AI may require mandatory approvals.
- The task receipts are lightweight and should not be mistaken for trusted test
  attestations. CI and PR review remain required.
