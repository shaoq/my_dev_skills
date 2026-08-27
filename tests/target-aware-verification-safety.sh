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

VERIFY_SKILL="$PROJECT_ROOT/verify-impl-consistency/SKILL.md"
COMPLETION_SKILL="$PROJECT_ROOT/check-changes-completed/SKILL.md"

require_text "$VERIFY_SKILL" 'argument-hint: "[<change-name> --base <target-branch>]"' \
  'verify advertises only project-level or explicit change/base mode'
require_text "$VERIFY_SKILL" 'MODE=project-level' \
  'verify names the no-argument project-level mode'
require_text "$VERIFY_SKILL" 'MODE=change-scoped' \
  'verify names the explicit change-scoped mode'
require_text "$VERIFY_SKILL" 'refs/heads/<BASE_BRANCH>' \
  'verify resolves only an explicit local base branch'
require_text "$VERIFY_SKILL" 'BASE_HEAD' \
  'verify freezes the target commit'
require_text "$VERIFY_SKILL" 'CURRENT_HEAD' \
  'verify freezes the current commit'
require_text "$VERIFY_SKILL" 'git merge-base --is-ancestor <BASE_HEAD> <CURRENT_HEAD>' \
  'verify rejects a non-ancestor baseline'
require_text "$VERIFY_SKILL" 'git diff <BASE_HEAD>..<CURRENT_HEAD> --name-only' \
  'verify attributes incremental evidence to immutable commits'
require_text "$VERIFY_SKILL" 'stale evidence' \
  'verify reports ref or current-head drift as stale evidence'
require_text "$VERIFY_SKILL" '不得自动选择 active change' \
  'verify never auto-selects an active change'
require_text "$VERIFY_SKILL" '重复的 `--base`' \
  'verify rejects duplicate base options'
require_text "$VERIFY_SKILL" '未知选项' \
  'verify rejects unknown options'
require_text "$VERIFY_SKILL" 'missing option value' \
  'verify rejects a base option without a value'
require_text "$VERIFY_SKILL" 'repeated positional change' \
  'verify rejects repeated change positionals'
require_text "$VERIFY_SKILL" 'If the local branch is absent' \
  'verify rejects a nonexistent local base branch'
require_text "$VERIFY_SKILL" 'not executed: BASE_HEAD is not an ancestor of CURRENT_HEAD' \
  'verify reports non-ancestor incremental verification as not executed'

require_text "$COMPLETION_SKILL" 'argument-hint: "--target <target-branch> --change <active-change> [--change <active-change> ...] [--backfill]"' \
  'completion advertises an explicit target and repeated change selectors'
require_text "$COMPLETION_SKILL" '[--backfill]' \
  'completion advertises explicit backfill authorization'
require_text "$COMPLETION_SKILL" 'READ_ONLY_DEFAULT=true' \
  'completion defaults to diagnostic-only mode'
require_text "$COMPLETION_SKILL" 'exactly one bare `--backfill`' \
  'completion accepts only one valueless backfill flag'
require_text "$COMPLETION_SKILL" 'duplicate, valued, or malformed `--backfill`' \
  'completion rejects malformed backfill authorization'
require_text "$COMPLETION_SKILL" 'SELECTED_CHANGES' \
  'completion uses an explicit selected-change set'
require_text "$COMPLETION_SKILL" 'LC_ALL=C sort' \
  'completion sorts its selected-change set deterministically'
require_text "$COMPLETION_SKILL" 'refs/heads/<TARGET_BRANCH>' \
  'completion resolves only an explicit local target branch'
require_text "$COMPLETION_SKILL" 'git merge-base --is-ancestor <BASE_HEAD> <CURRENT_HEAD>' \
  'completion blocks a non-ancestor target'
require_text "$COMPLETION_SKILL" 'git log <BASE_HEAD>..<CURRENT_HEAD> -- <expected-file-paths>' \
  'completion D3 uses the frozen comparison range'
require_text "$COMPLETION_SKILL" 'CHANGED_FILES=$(git diff <BASE_HEAD>..<CURRENT_HEAD> --name-only)' \
  'completion D5 reuses the same frozen comparison range'
require_text "$COMPLETION_SKILL" '未选择的 change 不得读取其 change-level artifacts' \
  'completion keeps unselected changes outside scanning and backfill'
require_text "$COMPLETION_SKILL" 'ZERO_WRITE_GATE' \
  'completion has a named zero-write gate'
require_text "$COMPLETION_SKILL" 'archivable = unknown/blocked' \
  'completion blocks archivable conclusions on drift'
require_text "$COMPLETION_SKILL" '不同目标分支必须分组调用' \
  'completion requires separate invocations for different targets'
require_text "$COMPLETION_SKILL" '重复的 `--change`' \
  'completion rejects duplicate change selectors'
require_text "$COMPLETION_SKILL" 'archive-only' \
  'completion rejects archive-only selections'
require_text "$COMPLETION_SKILL" 'missing target/change' \
  'completion rejects an incomplete selector set'
require_text "$COMPLETION_SKILL" 'unknown flag' \
  'completion rejects unknown flags'
require_text "$COMPLETION_SKILL" 'any positional argument' \
  'completion rejects positional arguments'
require_text "$COMPLETION_SKILL" 'not selected)' \
  'completion does not recursively scan an unselected active dependency'
require_text "$COMPLETION_SKILL" 'discard the plan, perform zero backfill, zero stage, zero' \
  'completion discards planned writes when snapshots drift'
require_text "$COMPLETION_SKILL" 'BACKFILL_AUTHORIZED=true' \
  'completion opens deterministic writes only after explicit authorization'
require_text "$COMPLETION_SKILL" 'missing, negative, or ambiguous' \
  'completion preserves Level-2 residual tasks without affirmative confirmation'

TEST_TMP_ROOT=$(mktemp -d)
trap 'rm -rf -- "$TEST_TMP_ROOT"' EXIT
TEST_REPO="$TEST_TMP_ROOT/repo"

git init -q -b main "$TEST_REPO"
git -C "$TEST_REPO" config user.name 'Target Verification Safety Test'
git -C "$TEST_REPO" config user.email 'target-verification@example.invalid'
printf 'root\n' > "$TEST_REPO/root.txt"
git -C "$TEST_REPO" add root.txt
git -C "$TEST_REPO" commit -q -m 'root'
ROOT_HEAD=$(git -C "$TEST_REPO" rev-parse HEAD)

git -C "$TEST_REPO" switch -q -c develop
printf 'develop\n' > "$TEST_REPO/develop.txt"
git -C "$TEST_REPO" add develop.txt
git -C "$TEST_REPO" commit -q -m 'develop baseline'
BASE_HEAD=$(git -C "$TEST_REPO" rev-parse refs/heads/develop)

git -C "$TEST_REPO" switch -q -c feature
printf 'feature\n' > "$TEST_REPO/feature.txt"
git -C "$TEST_REPO" add feature.txt
git -C "$TEST_REPO" commit -q -m 'feature delivery'
CURRENT_HEAD=$(git -C "$TEST_REPO" rev-parse HEAD)

if git -C "$TEST_REPO" merge-base --is-ancestor "$BASE_HEAD" "$CURRENT_HEAD"; then
  pass 'develop snapshot is an ancestor of the feature snapshot'
else
  fail 'develop snapshot is an ancestor of the feature snapshot'
fi
assert_equal "$(git -C "$TEST_REPO" diff "$BASE_HEAD..$CURRENT_HEAD" --name-only)" \
  'feature.txt' 'the frozen range attributes only feature delivery'
assert_equal "$(git -C "$TEST_REPO" diff "$BASE_HEAD..$BASE_HEAD" --name-only)" \
  '' 'an equal target/current snapshot produces an empty range'

git -C "$TEST_REPO" branch release "$ROOT_HEAD"
RELEASE_TREE=$(git -C "$TEST_REPO" rev-parse "$ROOT_HEAD^{tree}")
RELEASE_HEAD=$(printf 'release-only\n' | git -C "$TEST_REPO" commit-tree "$RELEASE_TREE" -p "$ROOT_HEAD")
git -C "$TEST_REPO" update-ref refs/heads/release "$RELEASE_HEAD" "$ROOT_HEAD"
assert_command_fails 'a target-side-only snapshot is rejected as non-ancestor' \
  git -C "$TEST_REPO" merge-base --is-ancestor "$RELEASE_HEAD" "$CURRENT_HEAD"

git -C "$TEST_REPO" branch -f develop "$CURRENT_HEAD"
if [ "$(git -C "$TEST_REPO" rev-parse refs/heads/develop)" != "$BASE_HEAD" ]; then
  pass 'target ref drift is observable against the frozen BASE_HEAD'
else
  fail 'target ref drift is observable against the frozen BASE_HEAD'
fi
assert_equal "$(git -C "$TEST_REPO" diff "$BASE_HEAD..$CURRENT_HEAD" --name-only)" \
  'feature.txt' 'moving the target ref cannot change frozen evidence'

printf 'current moved\n' > "$TEST_REPO/current.txt"
git -C "$TEST_REPO" add current.txt
git -C "$TEST_REPO" commit -q -m 'current moved'
if [ "$(git -C "$TEST_REPO" rev-parse HEAD)" != "$CURRENT_HEAD" ]; then
  pass 'current HEAD drift is observable against frozen CURRENT_HEAD'
else
  fail 'current HEAD drift is observable against frozen CURRENT_HEAD'
fi

FIXED_MAIN_HITS=$(find "$PROJECT_ROOT" \
  -path '*/archive/*' -prune -o \
  -name SKILL.md -type f -print0 \
  | xargs -0 awk '
      {
        line=$0
        sub(/^[[:space:]]+/, "", line)
        if (line ~ /^git (diff|log)( [^[:space:]]+)* (main\.\.HEAD|refs\/heads\/main)([[:space:]]|$)/) {
          print FILENAME ":" FNR ":" $0
        }
      }
    ')
if [ -z "$FIXED_MAIN_HITS" ]; then
  pass 'non-archived source skills contain no executable fixed-main comparison'
else
  fail "non-archived source skills contain no executable fixed-main comparison (found: $FIXED_MAIN_HITS)"
fi

printf '1..%d\n' "$CHECKS"
if [ "$FAILURES" -ne 0 ]; then
  printf '# %d of %d checks failed\n' "$FAILURES" "$CHECKS" >&2
  exit 1
fi

printf '# all %d checks passed\n' "$CHECKS"
