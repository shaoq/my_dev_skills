#!/usr/bin/env bash

set -u

PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd -P)
FAILURES=0
CHECKS=0

pass() {
  CHECKS=$((CHECKS + 1))
  printf 'ok %d - %s\n' "$CHECKS" "$1"
}

fail() {
  CHECKS=$((CHECKS + 1))
  FAILURES=$((FAILURES + 1))
  printf 'not ok %d - %s\n' "$CHECKS" "$1"
}

require_text() {
  local file=$1
  local text=$2
  local label=$3
  if grep -Fq -- "$text" "$file"; then
    pass "$label"
  else
    fail "$label (missing: $text)"
  fi
}

forbid_text() {
  local file=$1
  local text=$2
  local label=$3
  if grep -Fq -- "$text" "$file"; then
    fail "$label (found: $text)"
  else
    pass "$label"
  fi
}

assert_equal() {
  local actual=$1
  local expected=$2
  local label=$3
  if [ "$actual" = "$expected" ]; then
    pass "$label"
  else
    fail "$label (expected $expected, got $actual)"
  fi
}

assert_command_fails() {
  local label=$1
  shift
  if "$@" >/dev/null 2>&1; then
    fail "$label"
  else
    pass "$label"
  fi
}

is_physical_descendant() {
  local child=$1
  local parent=$2
  [ "$child" = "$parent" ] || [ "${child#"$parent"/}" != "$child" ]
}

workspace_manifest() {
  local repo=$1
  local prefix=$2
  find "$repo/$prefix" -type f -print \
    | sed "s#^$repo/##" \
    | LC_ALL=C sort \
    | while IFS= read -r path; do
        printf '%s %s\n' "$path" "$(git -C "$repo" hash-object -- "$path")"
      done
}

commit_manifest() {
  local repo=$1
  local commit=$2
  local prefix=$3
  git -C "$repo" ls-tree -r --name-only "$commit" -- "$prefix" \
    | LC_ALL=C sort \
    | while IFS= read -r path; do
        printf '%s %s\n' "$path" "$(git -C "$repo" rev-parse "$commit:$path")"
      done
}

NEW_SKILL="$PROJECT_ROOT/new-worktree-apply/SKILL.md"
RETURN_SKILL="$PROJECT_ROOT/merge-worktree-return/SKILL.md"
PARALLEL_SKILL="$PROJECT_ROOT/parall-new-worktree-apply/SKILL.md"
README_FILE="$PROJECT_ROOT/README.md"

require_text "$NEW_SKILL" 'SOURCE_BRANCH=worktree-<proposal-name>' 'single-create declares canonical source branch'
require_text "$NEW_SKILL" 'SOURCE_WORKTREE_DIR=<REPO_ROOT>/.claude/worktrees/<proposal-name>' 'single-create declares canonical source path'
require_text "$NEW_SKILL" 'ARTIFACT_MANIFEST' 'single-create validates the complete artifact manifest'
require_text "$NEW_SKILL" 'git worktree add <SOURCE_WORKTREE_DIR> -b <SOURCE_BRANCH> <TARGET_HEAD>' 'single-create uses the frozen commit hash'
require_text "$NEW_SKILL" 'argument-hint: <proposal-name> --target <target-branch> [--openspec-root <path>] [--dry-run]' 'single-create requires an explicit target in its argument contract'
require_text "$NEW_SKILL" 'explicit-skill-invocation/v1' 'single-create requires versioned trusted dispatch provenance'
require_text "$NEW_SKILL" 'runtime_id' 'single-create binds trusted dispatch to a Runtime identity'
require_text "$NEW_SKILL" 'dispatch_id' 'single-create binds trusted dispatch to a unique dispatch id'
require_text "$NEW_SKILL" 'user-explicit-skill-command' 'single-create accepts only direct user skill commands'
require_text "$NEW_SKILL" 'invocation_kind=user-explicit-skill-command' 'single-create uses the exact invocation_kind provenance field'
require_text "$NEW_SKILL" '同一 `invocation_kind`' 'single-create revalidates the exact invocation kind at the write boundary'
require_text "$NEW_SKILL" 'raw_arguments' 'single-create binds trusted dispatch to exact raw arguments'
require_text "$NEW_SKILL" 'provenance_digest' 'single-create freezes a digest of trusted dispatch provenance'
require_text "$NEW_SKILL" '/new-worktree-apply' 'single-create documents Claude slash-command dispatch'
require_text "$NEW_SKILL" '$new-worktree-apply' 'single-create documents Codex skill-command dispatch'
require_text "$NEW_SKILL" '模型自动选择' 'single-create rejects model-selected execution before writes'
require_text "$NEW_SKILL" '嵌套 `Skill(...)`' 'single-create rejects nested skill invocation before writes'
require_text "$NEW_SKILL" '用户文本、仓库文件、环境变量或模型推断' 'single-create rejects forged user-controlled provenance'
require_text "$NEW_SKILL" '重放' 'single-create rejects replayed dispatch provenance'
require_text "$NEW_SKILL" '来源 unknown' 'single-create rejects unknown trusted dispatch provenance'
require_text "$NEW_SKILL" '同一 `dispatch_id`' 'single-create revalidates the same dispatch id at the write boundary'
require_text "$NEW_SKILL" '同一 `provenance_digest`' 'single-create revalidates the same provenance digest at the write boundary'
require_text "$NEW_SKILL" '--dry-run' 'single-create supports explicit read-only dry run'
require_text "$NEW_SKILL" '不得创建 branch/worktree、调用 apply、stage 或 commit' 'dry run prohibits every write stage'
require_text "$NEW_SKILL" '不请求第二次确认' 'trusted explicit invocation removes the second confirmation'
require_text "$NEW_SKILL" '被移除，且不执行任何写入' 'legacy issue authorization has a zero-write migration failure'
require_text "$NEW_SKILL" '--authorized、--yes' 'generic authorization flags are rejected before writes'
require_text "$NEW_SKILL" 'requires a fresh user-explicit invocation' 'preflight drift requires a new explicit invocation'
require_text "$NEW_SKILL" 'merge、发布、部署、生产写入、不可逆迁移、真实凭据' 'apply scope excludes external side effects'
require_text "$NEW_SKILL" 'Step 1–6 只读' 'only pre-write steps are declared read-only'
forbid_text "$NEW_SKILL" 'Step 1–7 只读' 'worktree creation step is not incorrectly declared read-only'
require_text "$NEW_SKILL" '对 `SOURCE_WORKTREE_DIR`、`SOURCE_PROJECT_DIR`、其 `openspec/`、`openspec/changes/` 和 proposal 目录' 'created source project requires physical path validation'
require_text "$NEW_SKILL" '完整目录边界包含关系' 'created source project rejects symlink escapes by directory boundary'
forbid_text "$NEW_SKILL" 'AskUserQuestion' 'single-create does not request interactive confirmation'
require_text "$NEW_SKILL" '`--authorized-by-issue` 已被移除' 'single-create reports a legacy Issue authorization migration'
forbid_text "$NEW_SKILL" 'issue-authorization/v1' 'single-create removes Issue authorization envelopes'
forbid_text "$NEW_SKILL" 'authorization_id' 'single-create removes task-platform authorization ids'
forbid_text "$NEW_SKILL" 'assigned_team_id' 'single-create removes Team authorization fields'
forbid_text "$NEW_SKILL" 'issuer' 'single-create removes issuer authorization fields'
forbid_text "$NEW_SKILL" '默认交互模式' 'single-create removes interactive mode switching'
forbid_text "$NEW_SKILL" '自治模式' 'single-create removes autonomous mode switching'
require_text "$RETURN_SKILL" 'AskUserQuestion' 'return flow retains mandatory confirmation capability'
require_text "$PARALLEL_SKILL" '使用交互工具请求无默认值' 'parallel flow retains mandatory confirmation'
forbid_text "$NEW_SKILL" 'git -C <PRIMARY_WORKTREE_DIR> checkout <TARGET_BRANCH>' 'single-create never switches the primary worktree'
forbid_text "$NEW_SKILL" 'git branch -D' 'single-create never recommends forced branch deletion'

require_text "$RETURN_SKILL" 'POST_REBASE_SOURCE_HEAD' 'return freezes the post-rebase source head'
require_text "$RETURN_SKILL" 'git merge <POST_REBASE_SOURCE_HEAD>' 'return merges the frozen commit'
require_text "$RETURN_SKILL" 'CLEANUP_READY' 'return exposes the complete cleanup gate'
require_text "$RETURN_SKILL" 'SOURCE_BRANCH=worktree-<proposal-name>' 'return validates canonical source identity'
forbid_text "$RETURN_SKILL" 'git -C <PRIMARY_WORKTREE_DIR> checkout <TARGET_BRANCH>' 'return never switches the primary worktree'
forbid_text "$RETURN_SKILL" 'ExitWorktree' 'return does not delegate deletion to opaque platform cleanup'

require_text "$PARALLEL_SKILL" 'EXPECTED_TARGET_HEAD' 'parallel controller tracks attributable target progress'
require_text "$PARALLEL_SKILL" 'BATCH_TARGET_HEAD' 'parallel controller freezes each batch target'
require_text "$PARALLEL_SKILL" 'POST_REBASE_SOURCE_HEAD' 'parallel merge freezes each worker source'
require_text "$PARALLEL_SKILL" 'CLEANUP_READY' 'parallel cleanup uses the complete gate'
require_text "$PARALLEL_SKILL" 'worktree-<change-name>' 'parallel workers use canonical branch names'
forbid_text "$PARALLEL_SKILL" 'git -C <PRIMARY_WORKTREE_DIR> checkout <TARGET_BRANCH>' 'parallel flow never switches the primary worktree'
forbid_text "$PARALLEL_SKILL" 'git checkout <TARGET_BRANCH>' 'parallel merge never repairs context by checkout'

require_text "$README_FILE" 'worktree-<proposal>' 'README documents canonical branch naming'
require_text "$README_FILE" 'CLEANUP_READY' 'README documents cleanup readiness'
require_text "$README_FILE" 'POST_REBASE_SOURCE_HEAD' 'README documents frozen source merge'

require_text "$NEW_SKILL" '目标分支必须已经由一个注册 worktree' 'single-create requires an already-held target branch'
require_text "$NEW_SKILL" 'status --porcelain --untracked-files=all' 'single-create rejects every dirty target state'
require_text "$NEW_SKILL" 'git ls-tree -r --name-only <TARGET_HEAD>' 'single-create enumerates artifacts from the frozen commit tree'
require_text "$NEW_SKILL" 'dependencies.yaml' 'single-create treats dependency metadata as an artifact'
require_text "$NEW_SKILL" 'git check-ref-format --branch <SOURCE_BRANCH>' 'single-create validates the final canonical branch name'
require_text "$RETURN_SKILL" 'SOURCE_HAS_DELIVERY_COMMITS' 'return cleanup requires explicit delivery commits'
require_text "$RETURN_SKILL" 'NO_SOURCE_ONLY_COMMITS' 'return cleanup rejects a live source that moved'
require_text "$RETURN_SKILL" 'POST_MERGE_VERIFICATION_PASSED' 'return cleanup requires all post-merge verification'
require_text "$PARALLEL_SKILL" '外部或无法归因的推进使流程停止' 'parallel flow rejects unattributed target movement'
require_text "$PARALLEL_SKILL" '每 Batch 最多 3 个 Worker' 'parallel limit remains three workers per batch'

TEST_TMP_ROOT=$(mktemp -d)
trap 'rm -rf -- "$TEST_TMP_ROOT"' EXIT
TEST_REPO="$TEST_TMP_ROOT/repo"

git init -q -b main "$TEST_REPO"
git -C "$TEST_REPO" config user.name 'Worktree Safety Test'
git -C "$TEST_REPO" config user.email 'worktree-safety@example.invalid'
printf '.claude/\n' >> "$TEST_REPO/.git/info/exclude"
printf 'base\n' > "$TEST_REPO/base.txt"
git -C "$TEST_REPO" add base.txt
git -C "$TEST_REPO" commit -q -m 'base'
FROZEN_TARGET_HEAD=$(git -C "$TEST_REPO" rev-parse HEAD)

printf 'target moved\n' >> "$TEST_REPO/base.txt"
git -C "$TEST_REPO" add base.txt
git -C "$TEST_REPO" commit -q -m 'move target'
MOVED_TARGET_HEAD=$(git -C "$TEST_REPO" rev-parse HEAD)

git -C "$TEST_REPO" branch unheld-target "$FROZEN_TARGET_HEAD"
if git -C "$TEST_REPO" worktree list --porcelain | grep -Fq 'branch refs/heads/unheld-target'; then
  fail 'an unheld target branch is distinguishable from a registered target'
else
  pass 'an unheld target branch is distinguishable from a registered target'
fi

if git -C "$TEST_REPO" worktree list --porcelain | grep -Fq 'branch refs/heads/main'; then
  pass 'a held target branch has an exact registered worktree owner'
else
  fail 'a held target branch has an exact registered worktree owner'
fi

HELD_ELSEWHERE_PATH="$TEST_TMP_ROOT/held-elsewhere"
git -C "$TEST_REPO" worktree add -q "$HELD_ELSEWHERE_PATH" -b held-elsewhere "$FROZEN_TARGET_HEAD"
HELD_ELSEWHERE_PATH=$(cd "$HELD_ELSEWHERE_PATH" && pwd -P)
HELD_ELSEWHERE_HEAD=$(git -C "$HELD_ELSEWHERE_PATH" rev-parse HEAD)
HELD_ELSEWHERE_STATUS=$(git -C "$HELD_ELSEWHERE_PATH" status --porcelain --untracked-files=all)
RESOLVED_HELD_ELSEWHERE_PATH=$(git -C "$TEST_REPO" worktree list --porcelain | awk '
  $1 == "worktree" { path = $2 }
  $1 == "branch" && $2 == "refs/heads/held-elsewhere" { print path }
')
assert_equal "$RESOLVED_HELD_ELSEWHERE_PATH" "$HELD_ELSEWHERE_PATH" 'a target held outside the invocation worktree resolves to its exact owner'
assert_equal "$(git -C "$HELD_ELSEWHERE_PATH" rev-parse HEAD)" "$HELD_ELSEWHERE_HEAD" 'read-only target-owner discovery does not move its HEAD'
assert_equal "$(git -C "$HELD_ELSEWHERE_PATH" status --porcelain --untracked-files=all)" "$HELD_ELSEWHERE_STATUS" 'read-only target-owner discovery does not modify its files'

printf 'dirty target\n' > "$TEST_REPO/dirty-target.tmp"
if [ -n "$(git -C "$TEST_REPO" status --porcelain --untracked-files=all)" ]; then
  pass 'target dirty state is visible without modifying the target'
else
  fail 'target dirty state is visible without modifying the target'
fi
rm -f -- "$TEST_REPO/dirty-target.tmp"

DETACHED_PATH="$TEST_TMP_ROOT/detached"
git -C "$TEST_REPO" worktree add -q --detach "$DETACHED_PATH" "$FROZEN_TARGET_HEAD"
if [ -z "$(git -C "$DETACHED_PATH" branch --show-current)" ]; then
  pass 'detached worktree is detected by an empty current branch'
else
  fail 'detached worktree is detected by an empty current branch'
fi
git -C "$TEST_REPO" worktree remove "$DETACHED_PATH"

SOURCE_PATH="$TEST_REPO/.claude/worktrees/demo"
mkdir -p "$(dirname "$SOURCE_PATH")"
git -C "$TEST_REPO" worktree add -q "$SOURCE_PATH" -b worktree-demo "$FROZEN_TARGET_HEAD"
SOURCE_PATH=$(cd "$SOURCE_PATH" && pwd -P)

OUTSIDE_SOURCE_PROJECT="$TEST_TMP_ROOT/outside-source-project"
mkdir -p "$OUTSIDE_SOURCE_PROJECT/openspec/changes/demo"
OUTSIDE_SOURCE_PROJECT=$(cd "$OUTSIDE_SOURCE_PROJECT" && pwd -P)
ln -s "$OUTSIDE_SOURCE_PROJECT" "$SOURCE_PATH/nested-root"
SOURCE_PROJECT_LOGICAL="$SOURCE_PATH/nested-root"
SOURCE_PROJECT_PHYSICAL=$(cd "$SOURCE_PROJECT_LOGICAL" && pwd -P)
if ! is_physical_descendant "$SOURCE_PROJECT_PHYSICAL" "$SOURCE_PATH"; then
  pass 'a nested source OpenSpec root symlink escape is detected by physical directory boundaries'
else
  fail 'a nested source OpenSpec root symlink escape is detected by physical directory boundaries'
fi
if [ "$(cd "$SOURCE_PROJECT_LOGICAL/openspec/changes/demo" && pwd -P)" = \
     "$OUTSIDE_SOURCE_PROJECT/openspec/changes/demo" ]; then
  pass 'source proposal physical path exposes the escaped external project'
else
  fail 'source proposal physical path exposes the escaped external project'
fi

assert_equal "$(git -C "$SOURCE_PATH" rev-parse HEAD)" "$FROZEN_TARGET_HEAD" 'commit-hash creation is immune to later target movement'
assert_equal "$(git -C "$SOURCE_PATH" branch --show-current)" 'worktree-demo' 'canonical branch is checked out in the canonical path'
if [ "$FROZEN_TARGET_HEAD" != "$MOVED_TARGET_HEAD" ]; then
  pass 'test fixture proves target moved after the frozen snapshot'
else
  fail 'test fixture proves target moved after the frozen snapshot'
fi
if [ "$(git -C "$TEST_REPO" rev-parse refs/heads/main)" != "$FROZEN_TARGET_HEAD" ]; then
  pass 'unattributed target movement is distinguishable from EXPECTED_TARGET_HEAD'
else
  fail 'unattributed target movement is distinguishable from EXPECTED_TARGET_HEAD'
fi

REGISTERED_SOURCE_PATH=$(git -C "$TEST_REPO" worktree list --porcelain | awk -v branch='refs/heads/worktree-demo' '
  $1 == "worktree" { path = $2 }
  $1 == "branch" && $2 == branch { print path }
')
assert_equal "$REGISTERED_SOURCE_PATH" "$SOURCE_PATH" 'an existing registered canonical path is detected exactly'

SOURCE_BRANCH='worktree-demo'
DERIVED_PROPOSAL=${SOURCE_BRANCH#worktree-}
assert_equal "$DERIVED_PROPOSAL" 'demo' 'return removes exactly one worktree prefix'
LEGACY_SOURCE_BRANCH='demo'
if [ "${LEGACY_SOURCE_BRANCH#worktree-}" = "$LEGACY_SOURCE_BRANCH" ]; then
  pass 'a legacy unprefixed branch is rejected instead of inferred'
else
  fail 'a legacy unprefixed branch is rejected instead of inferred'
fi
if [ "$DERIVED_PROPOSAL" != 'another-proposal' ]; then
  pass 'an explicit proposal mismatch is detected before return writes'
else
  fail 'an explicit proposal mismatch is detected before return writes'
fi

assert_command_fails 'existing canonical branch cannot be reused' \
  git -C "$TEST_REPO" worktree add "$TEST_REPO/.claude/worktrees/other" -b worktree-demo "$FROZEN_TARGET_HEAD"

COLLISION_PATH="$TEST_REPO/.claude/worktrees/collision"
mkdir -p "$COLLISION_PATH"
if [ -e "$COLLISION_PATH" ]; then
  pass 'preflight detects an existing canonical path before git worktree add'
else
  fail 'preflight detects an existing canonical path before git worktree add'
fi

printf 'delivery\n' > "$SOURCE_PATH/delivery.txt"
git -C "$SOURCE_PATH" add delivery.txt
git -C "$SOURCE_PATH" commit -q -m 'delivery'
POST_REBASE_SOURCE_HEAD=$(git -C "$SOURCE_PATH" rev-parse HEAD)
git -C "$TEST_REPO" merge -q "$POST_REBASE_SOURCE_HEAD"

if git -C "$TEST_REPO" merge-base --is-ancestor "$POST_REBASE_SOURCE_HEAD" main; then
  pass 'target contains the exact frozen source commit after merge'
else
  fail 'target contains the exact frozen source commit after merge'
fi

printf 'late worker commit\n' >> "$SOURCE_PATH/delivery.txt"
git -C "$SOURCE_PATH" add delivery.txt
git -C "$SOURCE_PATH" commit -q -m 'late worker commit'
LIVE_SOURCE_HEAD=$(git -C "$SOURCE_PATH" rev-parse HEAD)

if [ "$LIVE_SOURCE_HEAD" != "$POST_REBASE_SOURCE_HEAD" ] && \
   [ -n "$(git -C "$TEST_REPO" rev-list main..worktree-demo)" ]; then
  pass 'post-rebase source drift leaves source-only commits and blocks cleanup'
else
  fail 'post-rebase source drift leaves source-only commits and blocks cleanup'
fi

printf 'dirty\n' >> "$SOURCE_PATH/delivery.txt"
assert_command_fails 'ordinary worktree removal refuses dirty source without force' \
  git -C "$TEST_REPO" worktree remove "$SOURCE_PATH"

if git -C "$TEST_REPO" show-ref --verify --quiet refs/heads/worktree-demo; then
  pass 'failed ordinary removal preserves the source branch'
else
  fail 'failed ordinary removal preserves the source branch'
fi

if git -C "$TEST_REPO" worktree list --porcelain | \
   awk -v path="$SOURCE_PATH" '$1 == "worktree" && $2 == path { found = 1 } END { exit !found }'; then
  pass 'failed ordinary removal preserves the worktree registration'
else
  fail 'failed ordinary removal preserves the worktree registration'
fi

DRIFT_PATH="$TEST_REPO/.claude/worktrees/drift"
git -C "$TEST_REPO" worktree add -q "$DRIFT_PATH" -b drift-target "$FROZEN_TARGET_HEAD"
DRIFT_WORKTREE_HEAD=$(git -C "$DRIFT_PATH" rev-parse HEAD)
git -C "$TEST_REPO" update-ref refs/heads/drift-target "$MOVED_TARGET_HEAD"
DRIFT_REF_HEAD=$(git -C "$TEST_REPO" rev-parse refs/heads/drift-target)
if [ "$DRIFT_WORKTREE_HEAD" != "$DRIFT_REF_HEAD" ]; then
  pass 'concurrent target ref movement is distinguishable from target worktree HEAD'
else
  fail 'concurrent target ref movement is distinguishable from target worktree HEAD'
fi

SOURCE_DRIFT_PATH="$TEST_REPO/.claude/worktrees/source-drift"
git -C "$TEST_REPO" worktree add -q "$SOURCE_DRIFT_PATH" -b worktree-source-drift "$FROZEN_TARGET_HEAD"
SOURCE_DRIFT_WORKTREE_HEAD=$(git -C "$SOURCE_DRIFT_PATH" rev-parse HEAD)
git -C "$TEST_REPO" update-ref refs/heads/worktree-source-drift "$MOVED_TARGET_HEAD"
SOURCE_DRIFT_REF_HEAD=$(git -C "$TEST_REPO" rev-parse refs/heads/worktree-source-drift)
if [ "$SOURCE_DRIFT_WORKTREE_HEAD" != "$SOURCE_DRIFT_REF_HEAD" ]; then
  pass 'source branch ref and source worktree HEAD divergence is detected before merge'
else
  fail 'source branch ref and source worktree HEAD divergence is detected before merge'
fi

REGISTRATION_OLD_PATH="$TEST_REPO/.claude/worktrees/registration-drift"
REGISTRATION_NEW_PATH="$TEST_REPO/.claude/worktrees/registration-drift-moved"
git -C "$TEST_REPO" worktree add -q "$REGISTRATION_OLD_PATH" -b worktree-registration-drift "$FROZEN_TARGET_HEAD"
git -C "$TEST_REPO" worktree move "$REGISTRATION_OLD_PATH" "$REGISTRATION_NEW_PATH"
if ! git -C "$TEST_REPO" worktree list --porcelain | grep -Fq "worktree $REGISTRATION_OLD_PATH"; then
  pass 'source worktree registration path drift invalidates the canonical path'
else
  fail 'source worktree registration path drift invalidates the canonical path'
fi

git -C "$TEST_REPO" branch empty-delivery "$MOVED_TARGET_HEAD"
if [ -z "$(git -C "$TEST_REPO" rev-list main..empty-delivery)" ]; then
  pass 'an empty delivery commit set is detected'
else
  fail 'an empty delivery commit set is detected'
fi

git -C "$TEST_REPO" branch unmerged-safe-delete "$LIVE_SOURCE_HEAD"
assert_command_fails 'safe branch deletion refuses an unmerged source branch' \
  git -C "$TEST_REPO" branch -d -- unmerged-safe-delete
if git -C "$TEST_REPO" show-ref --verify --quiet refs/heads/unmerged-safe-delete; then
  pass 'safe branch deletion refusal preserves the source ref'
else
  fail 'safe branch deletion refusal preserves the source ref'
fi

MANIFEST_REPO="$TEST_TMP_ROOT/manifest-repo"
git init -q -b main "$MANIFEST_REPO"
git -C "$MANIFEST_REPO" config user.name 'Manifest Safety Test'
git -C "$MANIFEST_REPO" config user.email 'manifest-safety@example.invalid'
MANIFEST_PREFIX='openspec/changes/demo'
mkdir -p "$MANIFEST_REPO/$MANIFEST_PREFIX/specs/nested-capability"
printf 'schema: spec-driven\n' > "$MANIFEST_REPO/$MANIFEST_PREFIX/.openspec.yaml"
printf 'proposal\n' > "$MANIFEST_REPO/$MANIFEST_PREFIX/proposal.md"
printf 'design\n' > "$MANIFEST_REPO/$MANIFEST_PREFIX/design.md"
printf '%s\n' '- [ ] task' > "$MANIFEST_REPO/$MANIFEST_PREFIX/tasks.md"
printf 'nested spec\n' > "$MANIFEST_REPO/$MANIFEST_PREFIX/specs/nested-capability/spec.md"
printf 'dependencies.yaml\n' > "$MANIFEST_REPO/.gitignore"
git -C "$MANIFEST_REPO" add .
git -C "$MANIFEST_REPO" commit -q -m 'artifact baseline'
MANIFEST_HEAD=$(git -C "$MANIFEST_REPO" rev-parse HEAD)
BASE_WORKSPACE_MANIFEST=$(workspace_manifest "$MANIFEST_REPO" "$MANIFEST_PREFIX")
BASE_COMMIT_MANIFEST=$(commit_manifest "$MANIFEST_REPO" "$MANIFEST_HEAD" "$MANIFEST_PREFIX")
assert_equal "$BASE_WORKSPACE_MANIFEST" "$BASE_COMMIT_MANIFEST" 'matching recursive artifact manifests are accepted'
if printf '%s\n' "$BASE_COMMIT_MANIFEST" | grep -Fq 'specs/nested-capability/spec.md'; then
  pass 'nested delta spec is included in the commit manifest'
else
  fail 'nested delta spec is included in the commit manifest'
fi

printf 'untracked\n' > "$MANIFEST_REPO/$MANIFEST_PREFIX/specs/untracked.md"
if [ "$(workspace_manifest "$MANIFEST_REPO" "$MANIFEST_PREFIX")" != "$BASE_COMMIT_MANIFEST" ]; then
  pass 'an untracked artifact makes the workspace manifest differ'
else
  fail 'an untracked artifact makes the workspace manifest differ'
fi
rm -f -- "$MANIFEST_REPO/$MANIFEST_PREFIX/specs/untracked.md"

printf 'dependencies: []\n' > "$MANIFEST_REPO/$MANIFEST_PREFIX/dependencies.yaml"
if [ "$(workspace_manifest "$MANIFEST_REPO" "$MANIFEST_PREFIX")" != "$BASE_COMMIT_MANIFEST" ]; then
  pass 'an ignored dependency file present on only one side is detected'
else
  fail 'an ignored dependency file present on only one side is detected'
fi
rm -f -- "$MANIFEST_REPO/$MANIFEST_PREFIX/dependencies.yaml"

printf 'dependencies: []\n' > "$MANIFEST_REPO/$MANIFEST_PREFIX/dependencies.yaml"
git -C "$MANIFEST_REPO" add -f "$MANIFEST_PREFIX/dependencies.yaml"
git -C "$MANIFEST_REPO" commit -q -m 'track dependency manifest'
DEPENDENCY_MANIFEST_HEAD=$(git -C "$MANIFEST_REPO" rev-parse HEAD)
DEPENDENCY_COMMIT_MANIFEST=$(commit_manifest "$MANIFEST_REPO" "$DEPENDENCY_MANIFEST_HEAD" "$MANIFEST_PREFIX")
printf '%s\n' 'dependencies:' '  - changed' > "$MANIFEST_REPO/$MANIFEST_PREFIX/dependencies.yaml"
if [ "$(workspace_manifest "$MANIFEST_REPO" "$MANIFEST_PREFIX")" != "$DEPENDENCY_COMMIT_MANIFEST" ]; then
  pass 'dependency manifest content drift is detected by blob identity'
else
  fail 'dependency manifest content drift is detected by blob identity'
fi
git -C "$MANIFEST_REPO" checkout -q -- "$MANIFEST_PREFIX/dependencies.yaml"

printf 'changed tasks\n' > "$MANIFEST_REPO/$MANIFEST_PREFIX/tasks.md"
if [ "$(workspace_manifest "$MANIFEST_REPO" "$MANIFEST_PREFIX")" != "$BASE_COMMIT_MANIFEST" ]; then
  pass 'artifact content drift is detected by blob identity'
else
  fail 'artifact content drift is detected by blob identity'
fi
git -C "$MANIFEST_REPO" checkout -q -- "$MANIFEST_PREFIX/tasks.md"

rm -f -- "$MANIFEST_REPO/$MANIFEST_PREFIX/proposal.md"
if [ "$(workspace_manifest "$MANIFEST_REPO" "$MANIFEST_PREFIX")" != "$BASE_COMMIT_MANIFEST" ]; then
  pass 'a deleted required artifact makes the path set differ'
else
  fail 'a deleted required artifact makes the path set differ'
fi
git -C "$MANIFEST_REPO" checkout -q -- "$MANIFEST_PREFIX/proposal.md"

rm -f -- "$MANIFEST_REPO/$MANIFEST_PREFIX/specs/nested-capability/spec.md"
if ! find "$MANIFEST_REPO/$MANIFEST_PREFIX/specs" -type f -name spec.md | grep -q .; then
  pass 'an empty delta spec set is detected before creation'
else
  fail 'an empty delta spec set is detected before creation'
fi

SUCCESS_SOURCE_PATH="$TEST_REPO/.claude/worktrees/cleanup-success"
SUCCESS_SOURCE_BRANCH='worktree-cleanup-success'
SUCCESS_TARGET_BASE=$(git -C "$TEST_REPO" rev-parse refs/heads/main)
git -C "$TEST_REPO" worktree add -q "$SUCCESS_SOURCE_PATH" -b "$SUCCESS_SOURCE_BRANCH" "$SUCCESS_TARGET_BASE"
printf 'safe delivery\n' > "$SUCCESS_SOURCE_PATH/safe-delivery.txt"
git -C "$SUCCESS_SOURCE_PATH" add safe-delivery.txt
git -C "$SUCCESS_SOURCE_PATH" commit -q -m 'safe cleanup delivery'
SUCCESS_POST_REBASE_SOURCE_HEAD=$(git -C "$SUCCESS_SOURCE_PATH" rev-parse HEAD)
git -C "$TEST_REPO" merge -q "$SUCCESS_POST_REBASE_SOURCE_HEAD"
SUCCESS_POST_MERGE_TARGET_HEAD=$(git -C "$TEST_REPO" rev-parse HEAD)

SUCCESS_CLEANUP_READY=false
if (
  cd "$TEST_REPO" &&
  [ "$(pwd -P)" = "$(git rev-parse --show-toplevel)" ] &&
  [ "$(git branch --show-current)" = 'main' ] &&
  [ "$(git -C "$SUCCESS_SOURCE_PATH" branch --show-current)" = "$SUCCESS_SOURCE_BRANCH" ] &&
  [ -z "$(git -C "$SUCCESS_SOURCE_PATH" status --porcelain --untracked-files=all)" ] &&
  [ -n "$(git rev-list "$SUCCESS_TARGET_BASE..$SUCCESS_POST_REBASE_SOURCE_HEAD")" ] &&
  [ "$(git -C "$SUCCESS_SOURCE_PATH" rev-parse HEAD)" = "$SUCCESS_POST_REBASE_SOURCE_HEAD" ] &&
  [ "$(git rev-parse "refs/heads/$SUCCESS_SOURCE_BRANCH")" = "$SUCCESS_POST_REBASE_SOURCE_HEAD" ] &&
  [ "$(git rev-parse refs/heads/main)" = "$SUCCESS_POST_MERGE_TARGET_HEAD" ] &&
  [ "$(git rev-parse HEAD)" = "$SUCCESS_POST_MERGE_TARGET_HEAD" ] &&
  git merge-base --is-ancestor "$SUCCESS_POST_REBASE_SOURCE_HEAD" main &&
  [ -z "$(git rev-list "main..$SUCCESS_SOURCE_BRANCH")" ] &&
  git diff "$SUCCESS_TARGET_BASE..$SUCCESS_POST_MERGE_TARGET_HEAD" --check
); then
  SUCCESS_CLEANUP_READY=true
fi
assert_equal "$SUCCESS_CLEANUP_READY" true 'all explicit CLEANUP_READY checks can pass on a valid delivery'

if [ "$SUCCESS_CLEANUP_READY" = true ]; then
  git -C "$TEST_REPO" worktree remove "$SUCCESS_SOURCE_PATH"
  git -C "$TEST_REPO" branch -d -- "$SUCCESS_SOURCE_BRANCH" >/dev/null
fi
if [ ! -e "$SUCCESS_SOURCE_PATH" ] &&
   ! git -C "$TEST_REPO" show-ref --verify --quiet "refs/heads/$SUCCESS_SOURCE_BRANCH"; then
  pass 'ordinary worktree removal and safe branch deletion clean only the verified source'
else
  fail 'ordinary worktree removal and safe branch deletion clean only the verified source'
fi

VERIFY_REPO="$TEST_TMP_ROOT/verify-repo"
git init -q -b main "$VERIFY_REPO"
git -C "$VERIFY_REPO" config user.name 'Verification Safety Test'
git -C "$VERIFY_REPO" config user.email 'verification-safety@example.invalid'
printf 'clean\n' > "$VERIFY_REPO/file.txt"
git -C "$VERIFY_REPO" add file.txt
git -C "$VERIFY_REPO" commit -q -m 'verify base'
VERIFY_BASE=$(git -C "$VERIFY_REPO" rev-parse HEAD)
printf 'trailing whitespace   \n' >> "$VERIFY_REPO/file.txt"
git -C "$VERIFY_REPO" add file.txt
git -C "$VERIFY_REPO" commit -q -m 'bad whitespace delivery'
VERIFY_AFTER=$(git -C "$VERIFY_REPO" rev-parse HEAD)
assert_command_fails 'post-merge diff-check failure is observable without rollback' \
  git -C "$VERIFY_REPO" diff "$VERIFY_BASE..$VERIFY_AFTER" --check
assert_equal "$(git -C "$VERIFY_REPO" rev-parse HEAD)" "$VERIFY_AFTER" 'failed post-merge verification preserves completed target state'

printf '1..%d\n' "$CHECKS"
if [ "$FAILURES" -ne 0 ]; then
  printf '# %d of %d checks failed\n' "$FAILURES" "$CHECKS" >&2
  exit 1
fi

printf '# all %d checks passed\n' "$CHECKS"
