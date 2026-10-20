"""Iki surumu de derler (PyInstaller).

Kullanim:
    python build.py            # ikisi: classic + ai
    python build.py classic    # sadece LittlePrince.exe   (AI'siz)
    python build.py ai         # sadece LittlePrinceAI.exe (AI'li)
    python build.py --dry-run  # komutu yazdir, derleme yapma

Windows'ta `build.bat` bu dosyayi cagirir; ayni isi gorur.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ICON = ROOT / "app.ico"
FLAG = ROOT / "ai_enabled.flag"
ENTRY = ROOT / "main.py"

# PyInstaller'in paketlemesine gerek olmayan Qt modulleri (exe'yi kucultir).
QT_EXCLUDES = [
    "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebEngineQuick",
    "PySide6.QtPdf",
    "PySide6.QtPdfWidgets",
    "PySide6.QtQml",
    "PySide6.QtQuick",
    "PySide6.QtQuickWidgets",
    "PySide6.QtQuick3D",
    "PySide6.QtQuickControls2",
    "PySide6.Qt3DCore",
    "PySide6.Qt3DRender",
    "PySide6.Qt3DInput",
    "PySide6.Qt3DLogic",
    "PySide6.Qt3DAnimation",
    "PySide6.Qt3DExtras",
    "PySide6.QtCharts",
    "PySide6.QtDataVisualization",
    "PySide6.QtGraphs",
    "PySide6.QtMultimedia",
    "PySide6.QtMultimediaWidgets",
    "PySide6.QtSql",
    "PySide6.QtTest",
    "PySide6.QtBluetooth",
    "PySide6.QtDesigner",
    "PySide6.QtHelp",
    "PySide6.QtLocation",
    "PySide6.QtNetworkAuth",
    "PySide6.QtNfc",
    "PySide6.QtOpenGL",
    "PySide6.QtOpenGLWidgets",
    "PySide6.QtPositioning",
    "PySide6.QtRemoteObjects",
    "PySide6.QtScxml",
    "PySide6.QtSensors",
    "PySide6.QtSerialPort",
    "PySide6.QtSerialBus",
    "PySide6.QtSpatialAudio",
    "PySide6.QtStateMachine",
    "PySide6.QtTextToSpeech",
    "PySide6.QtUiTools",
    "PySide6.QtWebChannel",
    "PySide6.QtWebSockets",
    "PySide6.QtHttpServer",
    "PySide6.QtSvg",
    "PySide6.QtSvgWidgets",
    "PySide6.QtNetwork",
    "PySide6.QtPrintSupport",
    "PySide6.QtConcurrent",
    "PySide6.QtDBus",
]

COMMON_EXCLUDES = QT_EXCLUDES + ["tkinter", "PIL"]

# Classic surumde AI ile ilgili her sey disarida kalir.
CLASSIC_EXCLUDES = COMMON_EXCLUDES + [
    "llm",
    "chat",
    "llama_cpp",
    "numpy",
    "jinja2",
    "diskcache",
]

EDITIONS = {
    "classic": {
        "name": "LittlePrince",
        "hidden": ["settings_dialog"],
        "collect": [],
        "add_data": [],
        "excludes": CLASSIC_EXCLUDES,
    },
    "ai": {
        "name": "LittlePrinceAI",
        "hidden": ["settings_dialog", "chat", "llm", "llama_cpp"],
        "collect": ["llama_cpp"],
        "add_data": [f"{FLAG}{os.pathsep}."],
        "excludes": COMMON_EXCLUDES,
    },
}


def command(edition: str) -> list[str]:
    """Verilen surum icin PyInstaller komutunu dondurur."""
    spec = EDITIONS[edition]
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        spec["name"],
        "--icon",
        str(ICON),
    ]
    for mod in spec["hidden"]:
        cmd += ["--hidden-import", mod]
    for pkg in spec["collect"]:
        cmd += ["--collect-all", pkg]
    for data in spec["add_data"]:
        cmd += ["--add-data", data]
    for mod in spec["excludes"]:
        cmd += ["--exclude-module", mod]
    cmd.append(str(ENTRY))
    return cmd


def _run(cmd: list[str], dry_run: bool) -> None:
    print(">", subprocess.list2cmdline(cmd), flush=True)
    if not dry_run:
        subprocess.run(cmd, cwd=ROOT, check=True)


def build(edition: str, dry_run: bool = False) -> bool:
    if edition not in EDITIONS:
        raise ValueError(f"Bilinmeyen surum: {edition}")

    if not ICON.exists():
        print("app.ico yok, uretiliyor...", flush=True)
        _run([sys.executable, str(ROOT / "tools" / "make_icon.py")], dry_run)

    _run(command(edition), dry_run)
    return dry_run or (ROOT / "dist" / f"{EDITIONS[edition]['name']}.exe").exists()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Little Prince exe derleyicisi")
    parser.add_argument(
        "edition",
        nargs="?",
        default="all",
        choices=["classic", "ai", "all"],
        help="hangi surum derlensin (varsayilan: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="derleme yapmadan komutlari yazdir",
    )
    args = parser.parse_args(argv)

    editions = ["classic", "ai"] if args.edition == "all" else [args.edition]
    failed: list[str] = []
    for edition in editions:
        print(f"\n=== {edition} ===", flush=True)
        try:
            if build(edition, args.dry_run):
                print(f"OK: dist/{EDITIONS[edition]['name']}.exe", flush=True)
            else:
                failed.append(edition)
                print(f"HATA: dist/{EDITIONS[edition]['name']}.exe olusmadi", flush=True)
        except subprocess.CalledProcessError as exc:
            failed.append(edition)
            print(f"HATA: {edition} derlenemedi (cikis kodu {exc.returncode})", flush=True)
        except Exception as exc:
            failed.append(edition)
            print(f"HATA: {edition}: {exc!r}", flush=True)

    if failed:
        print("\nBasarisiz: " + ", ".join(failed), flush=True)
        return 1
    print("\nTum derlemeler hazir (dist klasoru).", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
