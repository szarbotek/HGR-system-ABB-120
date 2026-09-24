#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_PREFIX="$PROJECT_ROOT/.conda2"

cd "$PROJECT_ROOT"
eval "$(conda shell.bash hook)"
conda activate "$ENV_PREFIX"

if [[ -z "${QT_PLUGIN_PATH:-}" || ! -d "$QT_PLUGIN_PATH" ]]; then
    QT_PLUGIN_PATH="$(find "$CONDA_PREFIX" -type d -path '*/PyQt5/Qt5/plugins' -print -quit)"
    export QT_PLUGIN_PATH
fi

if [[ -z "$QT_PLUGIN_PATH" || ! -d "$QT_PLUGIN_PATH" ]]; then
    echo "Error: Not found pluggins folder." >&2
    exit 1
fi

export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"

if [[ "${QT_DEBUG_PLUGINS:-0}" == "1" ]]; then
    echo "QT_PLUGIN_PATH=$QT_PLUGIN_PATH"
    echo "QT_QPA_PLATFORM=$QT_QPA_PLATFORM"
fi

# Zapisujemy nazwę modułu z pierwszego argumentu
MODULE="$1"

# Przesuwamy listę argumentów o 1 w lewo (usuwamy $1 z "$@")
shift

# Uruchamiamy python -m z właściwym modułem i pozostałymi argumentami
exec python -m "$MODULE" "$@"