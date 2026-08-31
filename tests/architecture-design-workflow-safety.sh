#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
RESULTS_DIR=""
RUNTIME=""

while (($#)); do
  case "$1" in
    --results-dir)
      if [[ $# -lt 2 || -z "${2:-}" ]]; then
        echo "--results-dir requires a non-empty value" >&2
        exit 2
      fi
      RESULTS_DIR="$2"
      shift 2
      ;;
    --runtime)
      if [[ $# -lt 2 || -z "${2:-}" ]]; then
        echo "--runtime requires a non-empty value" >&2
        exit 2
      fi
      RUNTIME="$2"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -n "$RESULTS_DIR" && -z "$RUNTIME" ]] || [[ -z "$RESULTS_DIR" && -n "$RUNTIME" ]]; then
  echo "--results-dir and --runtime must be supplied together" >&2
  exit 2
fi

if [[ -n "$RUNTIME" && "$RUNTIME" != "codex" && "$RUNTIME" != "claude" ]]; then
  echo "unsupported runtime: $RUNTIME (expected codex or claude)" >&2
  exit 2
fi


python3 "$PROJECT_ROOT/tests/architecture_design_workflow_safety.py" "$PROJECT_ROOT" "$RESULTS_DIR" "$RUNTIME"
