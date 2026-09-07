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

require_occurrences() {
  local file=$1
  local text=$2
  local expected=$3
  local label=$4
  local actual
  actual=$(grep -Foc -- "$text" "$file" || true)
  assert_equal "$actual" "$expected" "$label"
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

step8_source_project_gate() {
  local source_worktree_dir=$1
  local source_project_dir=$2
  local proposal=$3
  local apply_sentinel=$4
  local source_worktree_physical
  local source_project_physical
  local source_openspec_physical
  local source_changes_physical
  local source_proposal_physical

  source_worktree_physical=$(cd "$source_worktree_dir" && pwd -P) || return 1
  source_project_physical=$(cd "$source_project_dir" && pwd -P) || return 1
  source_openspec_physical=$(cd "$source_project_dir/openspec" && pwd -P) || return 1
  source_changes_physical=$(cd "$source_project_dir/openspec/changes" && pwd -P) || return 1
  source_proposal_physical=$(cd "$source_project_dir/openspec/changes/$proposal" && pwd -P) || return 1

  [ "$source_worktree_physical" = "$source_worktree_dir" ] || return 1
  [ -n "$source_project_physical" ] || return 1
  [ -n "$source_openspec_physical" ] || return 1
  [ -n "$source_changes_physical" ] || return 1
  [ -n "$source_proposal_physical" ] || return 1
  is_physical_descendant "$source_project_physical" "$source_worktree_physical" || return 1
  is_physical_descendant "$source_openspec_physical" "$source_project_physical" || return 1
  is_physical_descendant "$source_changes_physical" "$source_openspec_physical" || return 1
  is_physical_descendant "$source_proposal_physical" "$source_changes_physical" || return 1

  printf 'apply-called\n' > "$apply_sentinel"
}

prewrite_source_parent_gate() {
  local repo_root=$1
  local source_worktree_dir=$2
  local source_branch=$3
  local target_head=$4
  local apply_sentinel=$5
  local repo_physical
  local claude_physical
  local worktrees_physical

  repo_physical=$(cd "$repo_root" && pwd -P) || return 1
  [ -d "$repo_root/.claude" ] && [ ! -L "$repo_root/.claude" ] || return 1
  claude_physical=$(cd "$repo_root/.claude" && pwd -P) || return 1
  is_physical_descendant "$claude_physical" "$repo_physical" || return 1
  [ -d "$repo_root/.claude/worktrees" ] && [ ! -L "$repo_root/.claude/worktrees" ] || return 1
  worktrees_physical=$(cd "$repo_root/.claude/worktrees" && pwd -P) || return 1
  is_physical_descendant "$worktrees_physical" "$repo_physical" || return 1
  is_physical_descendant "$worktrees_physical" "$claude_physical" || return 1
  [ ! -e "$source_worktree_dir" ] && [ ! -L "$source_worktree_dir" ] || return 1

  git -C "$repo_root" worktree add "$source_worktree_dir" -b "$source_branch" "$target_head" || return 1
  printf 'apply-called\n' > "$apply_sentinel"
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
CODEX_POLICY="$PROJECT_ROOT/new-worktree-apply/agents/openai.yaml"
RETURN_SKILL="$PROJECT_ROOT/merge-worktree-return/SKILL.md"
PARALLEL_SKILL="$PROJECT_ROOT/parall-new-worktree-apply/SKILL.md"
PROPOSAL_SKILL="$PROJECT_ROOT/parall-new-proposal/SKILL.md"
COMPLETION_SKILL="$PROJECT_ROOT/check-changes-completed/SKILL.md"
README_FILE="$PROJECT_ROOT/README.md"
WORKTREE_SPEC="$PROJECT_ROOT/openspec/specs/worktree-targeting/spec.md"
INVOCATION_SPEC="$PROJECT_ROOT/openspec/specs/skill-invocation-governance/spec.md"
RETURN_DELTA="$PROJECT_ROOT/openspec/changes/archive/2026-08-29-allow-deferred-post-merge-cleanup/specs/worktree-targeting/spec.md"

require_text "$NEW_SKILL" 'SOURCE_BRANCH=worktree-<proposal-name>' 'single-create declares canonical source branch'
require_text "$NEW_SKILL" 'SOURCE_WORKTREE_DIR=<REPO_ROOT>/.claude/worktrees/<proposal-name>' 'single-create declares canonical source path'
require_text "$NEW_SKILL" 'ARTIFACT_MANIFEST' 'single-create validates the complete artifact manifest'
require_text "$NEW_SKILL" 'git worktree add <SOURCE_WORKTREE_DIR> -b <SOURCE_BRANCH> <TARGET_HEAD>' 'single-create uses the frozen commit hash'
require_text "$NEW_SKILL" 'argument-hint: <proposal-name> [--target <target-branch>] [--openspec-root <path>] [--dry-run]' 'single-create advertises an optional explicit target'
require_text "$NEW_SKILL" '主工作树登记的命名本地 ref、`origin/HEAD` 本地同名 ref、`main/master/trunk` 现有本地 ref' 'single-create uses the shared target inference order'
require_text "$NEW_SKILL" 'TARGET_SOURCE=inferred:<primary-worktree|origin-head|fallback-name>' 'single-create records the inferred target source'
require_text "$NEW_SKILL" 'AUTHORIZATION_PATH=deterministic' 'single-create has an explicit-target deterministic path'
require_text "$NEW_SKILL" 'AUTHORIZATION_PATH=interactive' 'single-create has an inferred-target interactive path'
require_text "$NEW_SKILL" '显式目标不存在时不回退' 'single-create never falls back from an invalid explicit target'
require_text "$NEW_SKILL" '选中候选后' 'single-create never skips a selected candidate after later validation fails'
require_text "$NEW_SKILL" '候选资格只由分支来源和本地 ref 存在性决定' 'single-create separates candidate eligibility from post-selection validation'
require_text "$NEW_SKILL" 'PREFLIGHT_SNAPSHOT[<round>]' 'single-create versions repeated interactive snapshots'
require_text "$NEW_SKILL" 'ACTIVE_CONFIRMED_SNAPSHOT' 'single-create identifies the active confirmed snapshot'
require_text "$NEW_SKILL" '最新事实存在任何 blocker' 'single-create stops instead of reconfirming a blocker'
require_text "$RETURN_SKILL" '选中候选后' 'return never skips a selected candidate after later validation fails'
require_text "$PARALLEL_SKILL" 'TARGET_SOURCE=explicit' 'parallel apply records an explicit target source'
require_text "$PARALLEL_SKILL" 'TARGET_SOURCE=inferred:<primary-worktree|origin-head|fallback-name>' 'parallel apply records the inferred target source'
require_text "$PARALLEL_SKILL" '选中候选后' 'parallel apply never skips a selected candidate after later validation fails'
for skill_file in "$NEW_SKILL" "$RETURN_SKILL" "$PARALLEL_SKILL" "$PROPOSAL_SKILL" "$COMPLETION_SKILL"; do
  forbid_text "$skill_file" 'disable-model-invocation:' "$(basename "$(dirname "$skill_file")") permits model and Team invocation"
  forbid_text "$skill_file" 'model:' "$(basename "$(dirname "$skill_file")") inherits the current model"
done
if [ -e "$CODEX_POLICY" ] || [ -L "$CODEX_POLICY" ]; then
  fail 'single-create removes the Codex implicit-invocation prohibition'
else
  pass 'single-create removes the Codex implicit-invocation prohibition'
fi
require_text "$NEW_SKILL" '/new-worktree-apply' 'single-create documents Claude slash-command dispatch'
require_text "$NEW_SKILL" '$new-worktree-apply' 'single-create documents Codex skill-command dispatch'
require_text "$NEW_SKILL" '自然语言、Team/subagent 或其他 skill' 'single-create permits intent-based and nested invocation without expanding authority'
forbid_text "$NEW_SKILL" 'runtime_id' 'single-create does not require an inaccessible Runtime id'
forbid_text "$NEW_SKILL" 'dispatch_id' 'single-create does not require an inaccessible dispatch id'
forbid_text "$NEW_SKILL" 'raw_arguments' 'single-create does not require inaccessible raw arguments'
forbid_text "$NEW_SKILL" 'provenance_digest' 'single-create does not require an inaccessible provenance digest'
require_text "$NEW_SKILL" 'REVALIDATION_SNAPSHOT' 'single-create uses a distinct final revalidation snapshot'
require_text "$NEW_SKILL" '不得覆盖或重新冻结 `PREFLIGHT_SNAPSHOT`' 'single-create keeps the preflight baseline immutable'
require_text "$NEW_SKILL" 'PREWRITE_SOURCE_PARENT_OK' 'single-create gates worktree creation on physical parent containment'
require_text "$NEW_SKILL" '--dry-run' 'single-create supports explicit read-only dry run'
require_text "$NEW_SKILL" '不得创建 branch/worktree、调用 apply、stage 或 commit' 'dry run prohibits every write stage'
require_text "$NEW_SKILL" '不请求第二次确认' 'explicit-target single-create removes the second confirmation'
require_text "$NEW_SKILL" '被移除，且不执行任何写入' 'legacy issue authorization has a zero-write migration failure'
require_text "$NEW_SKILL" '--authorized、--yes' 'generic authorization flags are rejected before writes'
require_text "$NEW_SKILL" 'requires a fresh invocation' 'preflight drift requires a fresh invocation'
require_text "$NEW_SKILL" 'merge、发布、部署、生产写入、不可逆迁移、真实凭据' 'apply scope excludes external side effects'
require_text "$NEW_SKILL" 'Step 1–6 只读' 'only pre-write steps are declared read-only'
forbid_text "$NEW_SKILL" 'Step 1–7 只读' 'worktree creation step is not incorrectly declared read-only'
require_text "$NEW_SKILL" '对 `SOURCE_WORKTREE_DIR`、`SOURCE_PROJECT_DIR`、其 `openspec/`、`openspec/changes/` 和 proposal 目录' 'created source project requires physical path validation'
require_text "$NEW_SKILL" '完整目录边界包含关系' 'created source project rejects symlink escapes by directory boundary'
require_text "$NEW_SKILL" 'AskUserQuestion' 'single-create can confirm an inferred target plan'
require_text "$NEW_SKILL" '使用交互工具请求无默认值' 'single-create inferred target confirmation has no default or timeout'
require_text "$NEW_SKILL" '`--authorized-by-issue` 已被移除' 'single-create reports a legacy Issue authorization migration'
forbid_text "$NEW_SKILL" 'issue-authorization/v1' 'single-create removes Issue authorization envelopes'
forbid_text "$NEW_SKILL" 'authorization_id' 'single-create removes task-platform authorization ids'
forbid_text "$NEW_SKILL" 'assigned_team_id' 'single-create removes Team authorization fields'
forbid_text "$NEW_SKILL" 'issuer' 'single-create removes issuer authorization fields'
forbid_text "$NEW_SKILL" '自治模式' 'single-create does not restore task-platform autonomous mode switching'
require_text "$RETURN_SKILL" 'AskUserQuestion' 'return flow retains interactive compatibility confirmation capability'
require_text "$PARALLEL_SKILL" '使用交互工具请求无默认值' 'parallel flow retains mandatory confirmation'
require_occurrences "$PROPOSAL_SKILL" 'WRITE_AUTHORIZATION_GATE=open' 1 'proposal creation has exactly one material-write authorization gate'
require_occurrences "$PARALLEL_SKILL" 'WRITE_AUTHORIZATION_GATE=open' 1 'parallel apply has exactly one material-write authorization gate'
require_occurrences "$RETURN_SKILL" 'WRITE_AUTHORIZATION_GATE=open' 1 'worktree return has exactly one material-write authorization gate'
forbid_text "$NEW_SKILL" 'git -C <PRIMARY_WORKTREE_DIR> checkout <TARGET_BRANCH>' 'single-create never switches the primary worktree'
forbid_text "$NEW_SKILL" 'git branch -D' 'single-create never recommends forced branch deletion'

require_text "$RETURN_SKILL" 'POST_REBASE_SOURCE_HEAD' 'return freezes the post-rebase source head'
require_text "$RETURN_SKILL" 'git merge <POST_REBASE_SOURCE_HEAD>' 'return merges the frozen commit'
require_text "$RETURN_SKILL" 'CLEANUP_READY' 'return exposes the complete cleanup gate'
require_text "$RETURN_SKILL" 'TASK_CLEANUP_POLICY_PASSED' 'return separates task cleanup eligibility from proposal completion'
require_text "$RETURN_SKILL" '精确标签 `[post-merge-verification]`' 'return recognizes only explicitly deferred post-merge tasks'
require_text "$RETURN_SKILL" '由用户后续在 target worktree 执行' 'return assigns deferred verification to the user'
require_text "$RETURN_SKILL" 'incomplete / non-archivable' 'return reports deferred proposals as incomplete and non-archivable'
require_text "$RETURN_SKILL" '不得执行、勾选、stage 或 commit' 'return does not mutate user-owned deferred tasks'
require_text "$RETURN_SKILL" 'LIMITED_RETURN_AUTHORIZED' 'return records clear bounded execution intent independently of caller identity'
require_text "$RETURN_SKILL" 'TARGET_SOURCE == explicit' 'return deterministic path requires an explicit target'
require_text "$RETURN_SKILL" 'SOURCE_CLEAN' 'return distinguishes clean deterministic sources from confirmed pending plans'
require_text "$RETURN_SKILL" 'DETERMINISTIC_RETURN_READY' 'return computes the no-second-confirmation path from observable facts'
require_text "$RETURN_SKILL" 'AUTHORIZATION_PATH=deterministic' 'return reports the deterministic authorization path'
require_text "$RETURN_SKILL" 'AUTHORIZATION_PATH=interactive' 'return preserves and reports the interactive compatibility path'
require_text "$RETURN_SKILL" '不请求第二次确认' 'explicit-target clean-source return does not repeat confirmation'
require_text "$RETURN_SKILL" 'fresh invocation' 'deterministic return drift requires a fresh invocation'
require_text "$RETURN_SKILL" '不得自动转入 interactive path' 'deterministic drift or conflict cannot silently widen authorization'
require_text "$RETURN_SKILL" 'status、review、discussion' 'read-only requests do not authorize return writes'
require_text "$RETURN_SKILL" '全部 pending 文件' 'dirty-source interactive plan displays the complete pending set'
require_text "$RETURN_SKILL" 'TARGET_SOURCE=inferred' 'inferred target remains behind interactive confirmation'
forbid_text "$RETURN_SKILL" 'issue-authorization/v1' 'return does not introduce Issue authorization envelopes'
forbid_text "$RETURN_SKILL" 'authorization_id' 'return does not introduce task-platform authorization ids'
forbid_text "$RETURN_SKILL" '--authorized' 'return does not introduce generic approval flags'
forbid_text "$RETURN_SKILL" '--yes' 'return does not introduce generic yes flags'
forbid_text "$RETURN_SKILL" 'CALLER_RUNTIME' 'return authorization does not depend on caller runtime'
forbid_text "$RETURN_SKILL" '`DONE == TOTAL`；若不完整则 merge 保留但 cleanup 被阻止' 'return no longer blocks cleanup solely because deferred tasks remain'
require_text "$RETURN_SKILL" 'SOURCE_BRANCH=worktree-<proposal-name>' 'return validates canonical source identity'
forbid_text "$RETURN_SKILL" 'git -C <PRIMARY_WORKTREE_DIR> checkout <TARGET_BRANCH>' 'return never switches the primary worktree'
forbid_text "$RETURN_SKILL" 'ExitWorktree' 'return does not delegate deletion to opaque platform cleanup'

require_text "$PARALLEL_SKILL" 'EXPECTED_TARGET_HEAD' 'parallel controller tracks attributable target progress'
require_text "$PARALLEL_SKILL" 'BATCH_TARGET_HEAD' 'parallel controller freezes each batch target'
require_text "$PARALLEL_SKILL" 'POST_REBASE_SOURCE_HEAD' 'parallel merge freezes each worker source'
require_text "$PARALLEL_SKILL" 'CLEANUP_READY' 'parallel cleanup uses the complete gate'
require_text "$PARALLEL_SKILL" 'TASK_CLEANUP_POLICY_PASSED' 'parallel computes task cleanup policy independently per child'
require_text "$PARALLEL_SKILL" '精确标签 `[post-merge-verification]`' 'parallel recognizes only explicitly deferred child tasks'
require_text "$PARALLEL_SKILL" '由用户后续在 target worktree 执行' 'parallel assigns deferred child verification to the user'
require_text "$PARALLEL_SKILL" 'incomplete / non-archivable' 'parallel reports deferred children as incomplete and non-archivable'
require_text "$PARALLEL_SKILL" '不得执行、勾选、stage 或 commit' 'parallel does not mutate user-owned deferred tasks'
require_text "$PARALLEL_SKILL" '可推进依赖 Wave' 'parallel lets structurally delivered deferred children unblock dependent Waves'
forbid_text "$PARALLEL_SKILL" 'artifacts 与 tasks 全部完成' 'parallel no longer requires deferred child tasks to be complete'
require_text "$PARALLEL_SKILL" 'worktree-<change-name>' 'parallel workers use canonical branch names'
forbid_text "$PARALLEL_SKILL" 'git -C <PRIMARY_WORKTREE_DIR> checkout <TARGET_BRANCH>' 'parallel flow never switches the primary worktree'
forbid_text "$PARALLEL_SKILL" 'git checkout <TARGET_BRANCH>' 'parallel merge never repairs context by checkout'

require_text "$README_FILE" 'worktree-<proposal>' 'README documents canonical branch naming'
require_text "$README_FILE" 'CLEANUP_READY' 'README documents cleanup readiness'
require_text "$README_FILE" 'POST_REBASE_SOURCE_HEAD' 'README documents frozen source merge'
require_text "$README_FILE" '显式 `--target` + clean source' 'README documents deterministic return without a second confirmation'
require_text "$README_FILE" 'inferred target 或 dirty source' 'README documents the interactive return compatibility path'
require_text "$WORKTREE_SPEC" 'A clear return request with an explicit target, a strictly clean canonical source, and a complete stable preflight SHALL proceed' 'canonical spec requires deterministic return behavior'
require_text "$WORKTREE_SPEC" '`parall-new-worktree-apply` MUST retain one explicit affirmative response' 'canonical spec preserves the parallel confirmation boundary'
forbid_text "$WORKTREE_SPEC" '`merge-worktree-return` and `parall-new-worktree-apply` MUST obtain one explicit affirmative response' 'canonical spec no longer applies unconditional confirmation to deterministic returns'
require_text "$WORKTREE_SPEC" 'When the option is omitted, `new-worktree-apply`, `merge-worktree-return`, and `parall-new-worktree-apply` SHALL select `TARGET_BRANCH`' 'canonical spec shares target inference across all worktree skills'
require_text "$WORKTREE_SPEC" 'an inferred target MUST instead receive one explicit affirmative response' 'canonical spec confirms inferred single-apply targets'
require_text "$WORKTREE_SPEC" 'Candidate eligibility SHALL depend only on branch-source resolution and local ref existence' 'canonical spec separates candidate eligibility from validation'
require_text "$WORKTREE_SPEC" 'ACTIVE_CONFIRMED_SNAPSHOT' 'canonical spec versions interactive confirmation rounds'
require_text "$WORKTREE_SPEC" 'If the latest facts contain any blocker' 'canonical spec stops instead of confirming a blocker'
forbid_text "$INVOCATION_SPEC" '`merge-worktree-return` MUST retain one affirmative confirmation immediately before documented material writes' 'invocation governance does not contradict deterministic return'
require_text "$INVOCATION_SPEC" 'An inferred target MUST receive one affirmative confirmation' 'invocation governance confirms inferred single apply'
require_text "$COMPLETION_SKILL" '/new-worktree-apply <name> --target <TARGET_BRANCH>' 'completion handoff preserves its frozen target'
forbid_text "$README_FILE" '漂移时零写失败并要求新的用户显式调用' 'README does not collapse both drift paths into deterministic behavior'
require_text "$RETURN_DELTA" '### Requirement: Preflight authorization and integration confirmation' 'delta updates the shared authorization requirement for archive consistency'
require_text "$RETURN_DELTA" '### Requirement: Pre-write snapshot revalidation' 'delta updates shared revalidation semantics for both return paths'

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

PARENT_ESCAPE_REPO="$TEST_TMP_ROOT/parent-escape-repo"
PARENT_ESCAPE_OUTSIDE="$TEST_TMP_ROOT/parent-escape-outside"
git init -q -b main "$PARENT_ESCAPE_REPO"
git -C "$PARENT_ESCAPE_REPO" config user.name 'Parent Escape Safety Test'
git -C "$PARENT_ESCAPE_REPO" config user.email 'parent-escape@example.invalid'
printf 'base\n' > "$PARENT_ESCAPE_REPO/base.txt"
git -C "$PARENT_ESCAPE_REPO" add base.txt
git -C "$PARENT_ESCAPE_REPO" commit -q -m 'base'
PARENT_ESCAPE_HEAD=$(git -C "$PARENT_ESCAPE_REPO" rev-parse HEAD)
PARENT_ESCAPE_WORKTREES=$(git -C "$PARENT_ESCAPE_REPO" worktree list --porcelain)
mkdir -p "$PARENT_ESCAPE_OUTSIDE/worktrees"
ln -s "$PARENT_ESCAPE_OUTSIDE" "$PARENT_ESCAPE_REPO/.claude"
PARENT_ESCAPE_STATUS=$(git -C "$PARENT_ESCAPE_REPO" status --porcelain --untracked-files=all)
PARENT_ESCAPE_SOURCE="$PARENT_ESCAPE_REPO/.claude/worktrees/escaped"
PARENT_ESCAPE_SENTINEL="$TEST_TMP_ROOT/parent-escape-apply-called"
if prewrite_source_parent_gate "$PARENT_ESCAPE_REPO" "$PARENT_ESCAPE_SOURCE" \
  worktree-escaped "$PARENT_ESCAPE_HEAD" "$PARENT_ESCAPE_SENTINEL"; then
  fail 'symlinked worktree parent escape is rejected before creation'
else
  pass 'symlinked worktree parent escape is rejected before creation'
fi
if ! git -C "$PARENT_ESCAPE_REPO" show-ref --verify --quiet refs/heads/worktree-escaped; then
  pass 'parent escape creates no source branch'
else
  fail 'parent escape creates no source branch'
fi
if [ ! -e "$PARENT_ESCAPE_OUTSIDE/worktrees/escaped" ]; then
  pass 'parent escape creates no outside worktree leaf'
else
  fail 'parent escape creates no outside worktree leaf'
fi
if [ ! -e "$PARENT_ESCAPE_SENTINEL" ]; then
  pass 'parent escape never invokes apply action'
else
  fail 'parent escape never invokes apply action'
fi
assert_equal "$(git -C "$PARENT_ESCAPE_REPO" rev-parse HEAD)" "$PARENT_ESCAPE_HEAD" \
  'parent escape preserves target HEAD'
assert_equal "$(git -C "$PARENT_ESCAPE_REPO" status --porcelain --untracked-files=all)" \
  "$PARENT_ESCAPE_STATUS" 'parent escape preserves target status'
assert_equal "$(git -C "$PARENT_ESCAPE_REPO" worktree list --porcelain)" \
  "$PARENT_ESCAPE_WORKTREES" 'parent escape preserves worktree registrations'

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

SOURCE_HEAD_BEFORE_GATE=$(git -C "$SOURCE_PATH" rev-parse HEAD)
SOURCE_STATUS_BEFORE_GATE=$(git -C "$SOURCE_PATH" status --porcelain --untracked-files=all)
SOURCE_BRANCH_BEFORE_GATE=$(git -C "$TEST_REPO" rev-parse refs/heads/worktree-demo)
APPLY_SENTINEL="$TEST_TMP_ROOT/source-escape-apply-called"
if step8_source_project_gate "$SOURCE_PATH" "$SOURCE_PROJECT_LOGICAL" demo "$APPLY_SENTINEL"; then
  fail 'source project escape gate rejects before apply'
else
  pass 'source project escape gate rejects before apply'
fi
if [ ! -e "$APPLY_SENTINEL" ]; then
  pass 'source project escape never invokes apply action'
else
  fail 'source project escape never invokes apply action'
fi
REGISTERED_SOURCE_AFTER_GATE=$(git -C "$TEST_REPO" worktree list --porcelain | awk -v branch='refs/heads/worktree-demo' '
  $1 == "worktree" { path = $2 }
  $1 == "branch" && $2 == branch { print path }
')
assert_equal "$REGISTERED_SOURCE_AFTER_GATE" "$SOURCE_PATH" 'source project gate failure preserves worktree registration'
assert_equal "$(git -C "$TEST_REPO" rev-parse refs/heads/worktree-demo)" "$SOURCE_BRANCH_BEFORE_GATE" 'source project gate failure preserves source branch ref'
assert_equal "$(git -C "$SOURCE_PATH" rev-parse HEAD)" "$SOURCE_HEAD_BEFORE_GATE" 'source project gate failure preserves source HEAD'
assert_equal "$(git -C "$SOURCE_PATH" status --porcelain --untracked-files=all)" "$SOURCE_STATUS_BEFORE_GATE" 'source project gate failure preserves source files'

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
