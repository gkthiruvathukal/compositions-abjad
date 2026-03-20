#!/usr/bin/env bash
#
# build-docs.sh - Bootstrap a local virtualenv and build Sphinx documentation.
#
# Usage:
#   ./build-docs.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
DOCS_DIR="${ROOT_DIR}/docs"
PYTHON_BIN=""

require_command() {
    local command_name="$1"
    local error_message="$2"
    if ! command -v "${command_name}" >/dev/null 2>&1; then
        echo "Error: ${error_message}" >&2
        return 1
    fi
}

detect_python() {
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_BIN="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_BIN="python"
    else
        echo "Error: Python 3 is required but was not found in PATH." >&2
        exit 1
    fi
}

ensure_venv() {
    if [ ! -d "${VENV_DIR}" ]; then
        echo "Creating virtual environment at ${VENV_DIR}"
        "${PYTHON_BIN}" -m venv "${VENV_DIR}"
    fi
}

activate_venv() {
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"
}

install_project() {
    echo "Installing project in editable mode"
    python -m pip install --no-build-isolation -e "${ROOT_DIR}"
}

install_docs_dependencies() {
    echo "Installing docs dependencies"
    python -m pip install -r "${DOCS_DIR}/requirements.txt"
}

check_optional_pdf_tools() {
    if command -v latexmk >/dev/null 2>&1; then
        return
    fi

    echo "Warning: latexmk is not installed; skipping PDF docs build." >&2
    echo "  macOS:  brew install --cask mactex-no-gui" >&2
    echo "  Ubuntu: sudo apt install latexmk texlive-latex-extra texlive-fonts-recommended" >&2
    exit 0
}

build_docs_html() {
    echo "Building Sphinx HTML documentation"
    make -C "${DOCS_DIR}" html
}

build_docs_pdf() {
    echo "Building Sphinx PDF documentation"
    make -C "${DOCS_DIR}" latexpdf
}

main() {
    require_command "make" "make is required to build the Sphinx documentation." || exit 1
    detect_python
    ensure_venv
    activate_venv
    install_project
    install_docs_dependencies
    build_docs_html
    check_optional_pdf_tools
    build_docs_pdf
    echo "Documentation build complete. Artifacts are in ${DOCS_DIR}/_build"
}

main "$@"
