# Implementation evidence

## Revisions and scope

- Adapter implementation revision: `not_committed` on current branch `main`.
- Working-tree baseline HEAD: `7c38ab42c6b490e4ffd1eb2c31646c5357e04002`.
- Consumed portable core implementation: `1d4b860b48e15f678d78a71bf2c38557ab9c2951`.
- Observed Multica source revision: `5fa65bd12585e29c2b52c44007ba3046a06c246b`.
- Observed `uni-architecture` revision: `c93270735ee71fcef065570f8d03d55a43608310`.
- The implementation changed only this repository's adapter source, OpenSpec artifacts, minimal normalized contract fixtures/test, and README. It did not modify `architecture-design-workflow`, Multica, `uni-architecture`, a real Runtime HOME, or a Multica workspace.
- Per the implementation-stage user decision, fake `multica` CLI, dual-Runtime behavior evidence, an adapter safety runner, and additional regression tests are outside this change.

## Observed Multica capability matrix

The actual `multica` executable was unavailable on `PATH`; no binary was built or installed. Bounded source/Cobra declarations at the observed revision support:

- Issue comment add/reply with actual `--parent`, repeatable `--attachment`, and JSON output;
- comment thread JSON with comment, parent, author, attachment, timestamp, and revision data;
- attachment identity read/download with durable `markdown_url` separated from transient `download_url`;
- scalar Issue metadata with a 64-character key limit, 50-key limit, and 8 KiB total object limit;
- mobile attachment cards/opening behavior;
- local `.skill`/`.zip` import;
- additive `agent skills add` and read-only `agent skills list`.

These are static observations, not authenticated live-platform conformance evidence. Every real delivery must still pass the adapter capability preflight.

## Validation results

| Validation | Result |
| --- | --- |
| Adapter quick validation | PASS |
| Core quick smoke validation | PASS |
| Minimal normalized adapter contract | PASS, 4/4 |
| Isolated temporary-HOME four-link and conflict check | PASS |
| Temporary `.skill`/`.zip` contents, frontmatter, secret and absolute-path scan | PASS |
| `openspec validate add-multica-architecture-approval-adapter --strict` | PASS |
| `git diff --check` | PASS |

No package was left in the repository and no validation command invoked a real Multica profile or network.

## GitNexus and repository boundary evidence

Final `detect_changes(scope=all)` was attempted and failed without mutation because the local LadybugDB index is storage version 43 while the available reader is version 42. The index was not rebuilt. Impact confidence therefore comes from bounded Git/source review: the only tracked diff is the README addition; all other implementation files are new adapter/OpenSpec/test artifacts, and no existing function, class, or method was modified.

Multica and `uni-architecture` both had pre-existing dirty worktrees and were inspected read-only. Their observed HEADs remain the revisions above; no command in this implementation wrote to either repository.

## Activation and remaining acceptance

```text
activation=not_run
sandbox_acceptance=not_run
workspace=n/a
agent=n/a
```

Before production use, a separately authorized operator must run the documented import/additive binding procedure and sandbox acceptance. Live CLI/profile compatibility, target-member mobile access, concurrent metadata fencing, real retry behavior, and short-token reply handling remain `not_run`; a failed capability preflight must close as `review_packet_unavailable` or motivate a separate general Multica platform change.
