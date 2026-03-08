#!/usr/bin/env bash
set -euo pipefail

force=false
skip_planning_copy=false

for arg in "$@"; do
    case "$arg" in
        --force) force=true ;;
        --skip-planning-copy) skip_planning_copy=true ;;
        *)
            echo "Unknown argument: $arg" >&2
            exit 1
            ;;
    esac
done

docspec_root="$(CDPATH='' cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$docspec_root/.." && pwd)"
template_root="$docspec_root/repo-template"
planning_root="$repo_root/.DocSpecSpark/planning"

if [[ ! -d "$template_root" ]]; then
    echo "Missing repo template directory: $template_root" >&2
    exit 1
fi

copy_tree() {
    local source_dir="$1"
    local dest_dir="$2"

    mkdir -p "$dest_dir"
    shopt -s dotglob nullglob
    for path in "$source_dir"/*; do
        local name target
        name="$(basename "$path")"

        if [[ "$name" == '__pycache__' || "$name" == '.pytest_cache' || "$name" == '.ruff_cache' ]]; then
            continue
        fi

        target="$dest_dir/$name"

        if [[ -d "$path" ]]; then
            mkdir -p "$target"
            copy_tree "$path" "$target"
            continue
        fi

        if [[ -e "$target" && "$force" != true ]]; then
            printf 'skip  %s\n' "$target"
            continue
        fi

        cp "$path" "$target"
        printf 'write %s\n' "$target"
    done
    shopt -u dotglob nullglob
}

printf 'Bootstrapping DocSpecSpark source repository in %s\n' "$repo_root"
copy_tree "$template_root" "$repo_root"

if [[ "$skip_planning_copy" != true ]]; then
    mkdir -p "$planning_root"
    for path in "$docspec_root"/*.md; do
        [[ -e "$path" ]] || continue
        name="$(basename "$path")"
        if [[ "$name" == 'BOOTSTRAP.md' ]]; then
            continue
        fi

        target="$planning_root/$name"
        if [[ -e "$target" && "$force" != true ]]; then
            printf 'skip  %s\n' "$target"
            continue
        fi

        cp "$path" "$target"
        printf 'copy  %s\n' "$target"
    done
fi

cat <<'EOF'

Bootstrap complete.
Next steps:
  1. uv sync
    2. uv run docspec init ../acme-corp-docs --profile small-business-manufacturing
    3. uv run docspec show-constitution --workspace ../acme-corp-docs
    4. uv run docspec create employee-handbook.md --workspace ../acme-corp-docs --overwrite
    5. uv run docspec build --workspace ../acme-corp-docs
    6. uv run docspec publish --workspace ../acme-corp-docs --version 1.0.0
EOF