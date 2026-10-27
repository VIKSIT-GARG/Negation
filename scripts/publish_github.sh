#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v gh >/dev/null 2>&1; then
  echo 'Install the official GitHub CLI (gh), then run: gh auth login' >&2
  exit 1
fi
gh auth status >/dev/null
login="$(gh api user --jq .login)"
if [[ "$login" != 'VIKSIT-GARG' ]]; then
  echo 'Expected GitHub account VIKSIT-GARG. Switch account before publishing.' >&2
  exit 1
fi
if [[ ! -d .git ]]; then
  git init -b main
  git add .
  git -c user.name='Viksit Garg' -c user.email='184533486+VIKSIT-GARG@users.noreply.github.com' commit -m 'Build NegationScope dataset construction and evaluation framework'
fi
if git remote get-url origin >/dev/null 2>&1; then
  echo 'An origin remote already exists; inspect it before publishing.' >&2
  exit 1
fi
gh repo create VIKSIT-GARG/NegationScope --private --source=. --remote=origin --push \
  --description 'Personal framework for negation dataset construction and paired visual evaluation, with attributed VBench, VLMEvalKit and NegBench source.'
