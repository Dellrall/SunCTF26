#!/usr/bin/env bash
#
# CTF Python Virtual Environment Startup & Setup Script
# Usage:
#   source setup_env.sh      (to create/update and immediately activate in current shell)
#   bash setup_env.sh        (to create/update environment)
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

echo "================================================"
echo "    SunCTF Python Environment Initializer       "
echo "================================================"

# 1. Create virtual environment if missing
if [ ! -d "${VENV_DIR}" ]; then
    echo "[*] Creating Python virtual environment in ${VENV_DIR}..."
    python3 -m venv "${VENV_DIR}"
    if [ $? -ne 0 ]; then
        echo "[-] Failed to create virtual environment. Ensure python3-venv is installed."
        return 1 2>/dev/null || exit 1
    fi
    echo "[+] Virtual environment created successfully."
else
    echo "[+] Found existing virtual environment in ${VENV_DIR}."
fi

# 2. Upgrade pip inside venv
echo "[*] Upgrading pip, setuptools, wheel..."
"${VENV_DIR}/bin/python3" -m pip install --upgrade pip setuptools wheel --quiet

# 3. Install/Sync dependencies from requirements.txt
if [ -f "${SCRIPT_DIR}/requirements.txt" ]; then
    echo "[*] Installing CTF dependencies from requirements.txt..."
    "${VENV_DIR}/bin/pip" install -r "${SCRIPT_DIR}/requirements.txt" --quiet
    if [ $? -eq 0 ]; then
        echo "[+] Dependencies installed / verified."
    else
        echo "[!] Some packages encountered errors during installation. Check pip output."
    fi
fi

# 4. Activate in current shell if sourced
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    # Script is being sourced
    source "${VENV_DIR}/bin/activate"
    echo ""
    echo "[+] Virtual environment is now ACTIVE in this shell."
    echo "    Python binary: $(which python3)"
else
    echo ""
    echo "------------------------------------------------"
    echo "To activate this environment in your shell, run:"
    echo "    source .venv/bin/activate"
    echo "------------------------------------------------"
fi
