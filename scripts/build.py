"""Iki surumu de derler (PyInstaller).

Kullanim:
    python scripts/build.py            # ikisi: classic + ai
    python scripts/build.py classic    # sadece LittlePrince   (AI'siz)
    python scripts/build.py ai         # sadece LittlePrinceAI (AI'li)
    python scripts/build.py --dry-run  # komutu yazdir, derleme yapma

Windows'ta `scripts\\build.bat`, Linux'ta `scripts/build.sh` bu dosyayi cagirir.
Linux'ta ayrica `dist/` icinde kurulabilir bir .tar.gz paketi olusur.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ICON = ASSETS / "app.ico"
PNG = ASSETS / "app.png"
FLAG = ASSETS / "ai_enabled.flag"
ENTRY = ROOT / "main.py"
DIST = ROOT / "dist"
BUILD = ROOT / "build"

IS_WINDOWS = sys.platform == "win32"
IS_LINUX = sys.platform.startswith("linux")
EXE_SUFFIX = ".exe" if IS_WINDOWS else ""

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
    "littleprince.llm",
    "littleprince.chat",
    "llama_cpp",
    "numpy",
    "jinja2",
    "diskcache",
]

EDITIONS = {
    "classic": {
        "name": "LittlePrince",
        "hidden": ["littleprince.settings_dialog"],
        "collect": [],
        "add_data": [],
        "excludes": CLASSIC_EXCLUDES,
    },
    "ai": {
        "name": "LittlePrinceAI",
        "hidden": [
            "littleprince.settings_dialog",
            "littleprince.chat",
            "littleprince.llm",
        ],
        "collect": ["llama_cpp"],
        "add_data": [f"{FLAG}{os.pathsep}."],
        "excludes": COMMON_EXCLUDES,
    },
}


def binary_path(edition: str) -> Path:
    return DIST / (EDITIONS[edition]["name"] + EXE_SUFFIX)


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


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
        "--distpath",
        str(DIST),
        "--workpath",
        str(BUILD),
        "--specpath",
        str(BUILD),
    ]
    if IS_WINDOWS and ICON.exists():
        cmd += ["--icon", str(ICON)]

    hidden = list(spec["hidden"])
    collect = list(spec["collect"])
    if edition == "ai":
        if not _module_available("llama_cpp"):
            print(
                "UYARI: llama_cpp kurulu degil; AI surumu yerlesik model olmadan "
                "derleniyor (Ollama / OpenAI uyumlu API calisir).",
                flush=True,
            )
        else:
            hidden.append("llama_cpp")
    for mod in hidden:
        cmd += ["--hidden-import", mod]
    for pkg in collect:
        if _module_available(pkg):
            cmd += ["--collect-all", pkg]
    for data in spec["add_data"]:
        cmd += ["--add-data", data]
    for mod in spec["excludes"]:
        cmd += ["--exclude-module", mod]

    if IS_WINDOWS:
        cmd += ["--exclude-module", "littleprince.platforms.x11"]
    else:
        cmd += ["--exclude-module", "littleprince.platforms.win32"]

    cmd.append(str(ENTRY))
    return cmd


def _run(cmd: list[str], dry_run: bool) -> None:
    print(">", subprocess.list2cmdline(cmd), flush=True)
    if not dry_run:
        subprocess.run(cmd, cwd=ROOT, check=True)


def _write_linux_extras(stage: Path, edition: str) -> None:
    """Linux tar paketine kurulum betigi ve kisa bir README ekler."""
    name = EDITIONS[edition]["name"]
    install = (ROOT / "packaging" / "install-linux.sh").read_text(encoding="utf-8")
    install = install.replace("@APP_NAME@", name)
    target = stage / "install.sh"
    target.write_text(install, encoding="utf-8")
    target.chmod(0o755)

    shutil.copy2(PNG, stage / "littleprince.png")
    shutil.copy2(ROOT / "LICENSE", stage / "LICENSE")
    shutil.copy2(ROOT / "packaging" / "README-LINUX.md", stage / "README-LINUX.md")


def package_linux(edition: str) -> Path | None:
    """Linux ikilisini kurulabilir bir tar.gz haline getirir."""
    if not IS_LINUX:
        return None
    binary = binary_path(edition)
    if not binary.exists():
        return None

    name = EDITIONS[edition]["name"]
    stage = DIST / f"{name}-linux-x86_64"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    shutil.copy2(binary, stage / name)
    _write_linux_extras(stage, edition)

    archive = DIST / f"{name}-linux-x86_64.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(stage, arcname=stage.name)
    shutil.rmtree(stage)
    return archive


def build(edition: str, dry_run: bool = False) -> bool:
    if edition not in EDITIONS:
        raise ValueError(f"Bilinmeyen surum: {edition}")

    if not ICON.exists() or (IS_LINUX and not PNG.exists()):
        print("uygulama simgesi yok, uretiliyor...", flush=True)
        _run([sys.executable, str(ROOT / "scripts" / "make_icon.py")], dry_run)

    _run(command(edition), dry_run)
    return dry_run or binary_path(edition).exists()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Little Prince derleyicisi")
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
                print(f"OK: {binary_path(edition)}", flush=True)
                archive = package_linux(edition)
                if archive:
                    print(f"PAKET: {archive}", flush=True)
            else:
                failed.append(edition)
                print(f"HATA: {binary_path(edition)} olusmadi", flush=True)
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
