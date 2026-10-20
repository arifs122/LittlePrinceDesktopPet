"""Settings dialog: character options + optional AI.

The AI tab only exists in builds that include it (see features.ai_enabled()).
"""
from __future__ import annotations

import os

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from . import config
from . import features
from . import i18n
from . import platforms as platform_api


class TestWorker(QThread):
    """Tests the AI connection in the background."""

    result = Signal(str, str)

    def __init__(self, cfg: dict):
        super().__init__()
        self.cfg = dict(cfg)

    def run(self):
        try:
            from . import llm

            provider, desc = llm.detect(self.cfg)
            ok = provider != "off"
            self.result.emit(("✓ " if ok else "✗ ") + desc, "ok" if ok else "no")
        except Exception as exc:
            self.result.emit(f"✗ Error: {exc}", "no")


PROVIDERS = [
    ("auto", "Automatic (API/Ollama first, else built-in model)"),
    ("local", "Built-in model — ships with the app, downloaded once"),
    ("ollama", "Ollama — local model (offline, free)"),
    ("openai", "OpenAI-compatible service (needs a key)"),
    ("off", "Off — offline replies only"),
]


class SettingsDialog(QDialog):
    def __init__(self, pet):
        super().__init__(None)
        self.pet = pet
        self._ai = features.ai_enabled()
        self.setWindowTitle("Little Prince — Settings")
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setMinimumWidth(460)

        cfg = dict(pet.cfg)

        tabs = QTabWidget()
        tabs.addTab(self._build_character_tab(cfg), "Character")
        if self._ai:
            tabs.addTab(self._build_ai_tab(cfg), "AI")

        btn_reset = QPushButton("Reset to defaults")
        btn_reset.clicked.connect(self._reset)
        btn_center = QPushButton("Bring to screen")
        btn_center.clicked.connect(lambda: self.pet.respawn())
        btn_close = QPushButton("Close")
        btn_close.setDefault(True)
        btn_close.clicked.connect(self.close)

        row = QHBoxLayout()
        row.addWidget(btn_reset)
        row.addWidget(btn_center)
        row.addStretch(1)
        row.addWidget(btn_close)

        self.path_label = QLabel()
        self.path_label.setWordWrap(True)
        self.path_label.setStyleSheet("color: #888; font-size: 10px;")

        btn_folder = QPushButton("Open settings folder")
        btn_folder.clicked.connect(self._open_folder)
        row2 = QHBoxLayout()
        row2.addWidget(btn_folder)
        row2.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        layout.addLayout(row)
        layout.addLayout(row2)
        layout.addWidget(self.path_label)

        self._update_path_label()
        if self._ai:
            self._update_local_status()
        self._center_on_screen()

    # ------------------------------------------------------------------
    def _build_character_tab(self, cfg: dict) -> QWidget:
        page = QWidget()

        self.language = QComboBox()
        for code, label in i18n.LANGS:
            self.language.addItem(label, code)
        self.language.setCurrentIndex(
            max(0, self.language.findData(cfg.get("language", "auto")))
        )
        self.language.currentIndexChanged.connect(self._changed)

        self.scale = QDoubleSpinBox()
        self.scale.setRange(0.7, 3.5)
        self.scale.setSingleStep(0.1)
        self.scale.setDecimals(1)
        self.scale.setSuffix("  ×")
        self.scale.setValue(float(cfg["scale"]))
        self.scale.valueChanged.connect(self._changed)

        self.speed = QDoubleSpinBox()
        self.speed.setRange(0.5, 6.0)
        self.speed.setSingleStep(0.1)
        self.speed.setDecimals(1)
        self.speed.setValue(float(cfg["walk_speed"]))
        self.speed.valueChanged.connect(self._changed)

        self.chance = QSpinBox()
        self.chance.setRange(0, 100)
        self.chance.setSuffix(" %")
        self.chance.setValue(int(round(float(cfg["companion_chance"]) * 100)))
        self.chance.valueChanged.connect(self._changed)

        self.teleport = QSpinBox()
        self.teleport.setRange(0, 100)
        self.teleport.setSuffix(" %")
        self.teleport.setValue(int(round(float(cfg["teleport_chance"]) * 100)))
        self.teleport.valueChanged.connect(self._changed)

        self.tp_cool = QSpinBox()
        self.tp_cool.setRange(0, 3600)
        self.tp_cool.setSingleStep(5)
        self.tp_cool.setSuffix(" s")
        self.tp_cool.setValue(int(cfg.get("teleport_cooldown", 20)))
        self.tp_cool.valueChanged.connect(self._changed)

        self.sit_min = QSpinBox()
        self.sit_min.setRange(0, 600)
        self.sit_min.setSingleStep(5)
        self.sit_min.setSuffix(" s")
        self.sit_min.setValue(int(cfg.get("sit_min_seconds", 10)))
        self.sit_min.valueChanged.connect(self._changed)

        self.sleep_on = QCheckBox("Fall asleep when left alone")
        self.sleep_on.setChecked(bool(cfg["sleep_enabled"]))
        self.sleep_on.stateChanged.connect(self._changed)

        self.sleep_after = QSpinBox()
        self.sleep_after.setRange(15, 3600)
        self.sleep_after.setSingleStep(15)
        self.sleep_after.setSuffix(" s")
        self.sleep_after.setValue(int(cfg["sleep_after"]))
        self.sleep_after.valueChanged.connect(self._changed)

        self.on_top = QCheckBox("Always stay on top")
        self.on_top.setChecked(bool(cfg["always_on_top"]))
        self.on_top.stateChanged.connect(self._changed)

        form = QFormLayout(page)
        form.addRow("Language:", self.language)
        form.addRow("Size:", self.scale)
        form.addRow("Walk speed:", self.speed)
        form.addRow("Chance a companion joins when sitting:", self.chance)
        form.addRow("Chance to teleport to another surface:", self.teleport)
        form.addRow("Minimum time between teleports:", self.tp_cool)
        form.addRow("Minimum sit time:", self.sit_min)
        form.addRow("", self.sleep_on)
        form.addRow("Seconds before sleeping:", self.sleep_after)
        form.addRow("", self.on_top)
        return page

    # ------------------------------------------------------------------
    def _build_ai_tab(self, cfg: dict) -> QWidget:
        from . import llm

        page = QWidget()

        self.provider = QComboBox()
        for value, label in PROVIDERS:
            self.provider.addItem(label, value)
        self.provider.setCurrentIndex(
            max(0, self.provider.findData(cfg.get("llm_provider", "auto")))
        )
        self.provider.currentIndexChanged.connect(self._provider_changed)

        self.base_url = QLineEdit(cfg.get("llm_base_url", ""))
        self.base_url.setPlaceholderText("http://localhost:11434")
        self.base_url.editingFinished.connect(self._changed)

        self.model = QLineEdit(cfg.get("llm_model", ""))
        self.model.setPlaceholderText("empty = automatic (e.g. llama3.2:1b)")
        self.model.editingFinished.connect(self._changed)

        self.api_key = QLineEdit(cfg.get("llm_api_key", ""))
        self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setPlaceholderText("sk-… or a Groq/OpenRouter key")
        self.api_key.editingFinished.connect(self._changed)

        show_key = QCheckBox("Show key")
        show_key.stateChanged.connect(
            lambda: self.api_key.setEchoMode(
                QLineEdit.Normal if show_key.isChecked() else QLineEdit.Password
            )
        )

        self.test_label = QLabel("")
        self.test_label.setWordWrap(True)
        btn_test = QPushButton("Test connection")
        btn_test.clicked.connect(self._test)

        # built-in model
        self.local_model = QComboBox()
        for key, info in llm.LOCAL_MODELS.items():
            self.local_model.addItem(info["label"], key)
        self.local_model.setCurrentIndex(
            max(0, self.local_model.findData(cfg.get("local_model", "qwen1.5")))
        )
        self.local_model.currentIndexChanged.connect(self._changed)

        self.local_status = QLabel("")
        self.local_status.setWordWrap(True)
        self.local_status.setStyleSheet("font-size: 11px; color: #666;")

        self.dl_btn = QPushButton("Download built-in model")
        self.dl_btn.clicked.connect(self._download_local)

        form = QFormLayout(page)
        form.addRow("Provider:", self.provider)
        form.addRow("Built-in model:", self.local_model)
        form.addRow("", self.local_status)
        form.addRow("", self.dl_btn)
        form.addRow("Server address:", self.base_url)
        form.addRow("Model:", self.model)
        form.addRow("API key:", self.api_key)
        form.addRow("", show_key)

        test_row = QHBoxLayout()
        test_row.addWidget(btn_test)
        test_row.addWidget(self.test_label, 1)
        form.addRow("", test_row)

        help_box = QGroupBox("How does it work?")
        help_text = QLabel(
            "<b>Built-in model (no setup at all):</b><br>"
            "Click “Download built-in model” above. It runs inside the app with "
            "llama.cpp — no extra software, works offline afterwards.<br><br>"
            "<b>Ollama:</b> install from ollama.com, then run "
            "<code>ollama pull llama3.2:1b</code> once.<br><br>"
            "<b>Cloud (works on any machine):</b> get an API key and pick "
            "<i>OpenAI-compatible</i>.<br>"
            "• OpenAI: https://api.openai.com/v1<br>"
            "• Groq: https://api.groq.com/openai/v1<br>"
            "• OpenRouter: https://openrouter.ai/api/v1<br>"
            "• LM Studio (local): http://localhost:1234/v1<br><br>"
            "<i>Note: the API key is stored in plain text in the settings file.</i>"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("font-size: 11px; color: #555;")
        box = QVBoxLayout(help_box)
        box.addWidget(help_text)
        form.addRow(help_box)
        return page

    # ------------------------------------------------------------------
    def _current_values(self) -> dict:
        values = {
            "language": self.language.currentData(),
            "scale": self.scale.value(),
            "walk_speed": self.speed.value(),
            "companion_chance": self.chance.value() / 100.0,
            "teleport_chance": self.teleport.value() / 100.0,
            "teleport_cooldown": self.tp_cool.value(),
            "sit_min_seconds": self.sit_min.value(),
            "sleep_enabled": self.sleep_on.isChecked(),
            "sleep_after": self.sleep_after.value(),
            "always_on_top": self.on_top.isChecked(),
        }
        if self._ai:
            values.update(
                {
                    "llm_provider": self.provider.currentData(),
                    "llm_base_url": self.base_url.text().strip(),
                    "llm_model": self.model.text().strip(),
                    "llm_api_key": self.api_key.text().strip(),
                    "local_model": self.local_model.currentData(),
                }
            )
        return values

    def _provider_changed(self):
        provider = self.provider.currentData()
        base = self.base_url.text().strip()
        if provider == "openai" and (not base or "11434" in base):
            self.base_url.setText("https://api.openai.com/v1")
        elif provider == "ollama" and (
            not base or "api.openai" in base or "openrouter" in base or "groq" in base
        ):
            self.base_url.setText("http://localhost:11434")
        elif provider == "auto" and not base:
            self.base_url.setText("http://localhost:11434")
        self._changed()

    def _changed(self):
        self.pet.apply_settings(self._current_values())
        self._update_path_label()
        if self._ai:
            self._update_local_status()

    # ------------------------------------------------------------------
    def _update_local_status(self):
        if not hasattr(self, "local_status"):
            return
        from . import llm

        key = self.local_model.currentData()
        info = llm.LOCAL_MODELS.get(key, {})
        path = os.path.join(llm.models_dir(), info.get("file", ""))
        if os.path.isfile(path):
            mb = os.path.getsize(path) // (1024 * 1024)
            self.local_status.setText(f"✓ Downloaded ({mb} MB) — {path}")
            self.local_status.setStyleSheet("font-size: 11px; color: #2E7D32;")
            self.dl_btn.setText("Download again")
        else:
            self.local_status.setText(
                f"✗ Not downloaded yet (~{info.get('mb', '?')} MB). "
                "You can also download it from the chat window."
            )
            self.local_status.setStyleSheet("font-size: 11px; color: #B3261E;")
            self.dl_btn.setText("Download built-in model")

    def _download_local(self):
        self._changed()
        from .chat import DownloadWorker

        self.dl_btn.setEnabled(False)
        self.local_status.setText("Downloading…")
        self._dl = DownloadWorker(self.pet.cfg)
        self._dl.progress.connect(
            lambda pct, text: self.local_status.setText(f"Downloading… {pct}% ({text})")
        )
        self._dl.done.connect(self._on_local_downloaded)
        self._dl.start()

    def _on_local_downloaded(self, ok: bool, err: str):
        self.dl_btn.setEnabled(True)
        if not ok:
            self.local_status.setText(f"Download failed: {err}")
            self.local_status.setStyleSheet("font-size: 11px; color: #B3261E;")
            return
        self._update_local_status()

    def _test(self):
        self._changed()
        self.test_label.setText("Testing…")
        self.test_label.setStyleSheet("color: #888;")
        self._worker = TestWorker(self.pet.cfg)
        self._worker.result.connect(self._on_test)
        self._worker.start()

    def _on_test(self, text: str, state: str):
        self.test_label.setText(text)
        self.test_label.setStyleSheet(
            "color: #2E7D32;" if state == "ok" else "color: #B3261E;"
        )

    def _reset(self):
        d = config.DEFAULTS
        self.language.setCurrentIndex(max(0, self.language.findData(d["language"])))
        self.scale.setValue(d["scale"])
        self.speed.setValue(d["walk_speed"])
        self.chance.setValue(int(d["companion_chance"] * 100))
        self.teleport.setValue(int(d["teleport_chance"] * 100))
        self.tp_cool.setValue(d["teleport_cooldown"])
        self.sit_min.setValue(d["sit_min_seconds"])
        self.sleep_on.setChecked(d["sleep_enabled"])
        self.sleep_after.setValue(d["sleep_after"])
        self.on_top.setChecked(d["always_on_top"])
        if self._ai:
            self.provider.setCurrentIndex(
                max(0, self.provider.findData(d["llm_provider"]))
            )
            self.base_url.setText(d["llm_base_url"])
            self.model.setText(d["llm_model"])
            self.api_key.setText(d["llm_api_key"])
            self.local_model.setCurrentIndex(
                max(0, self.local_model.findData(d["local_model"]))
            )
        self._changed()

    # ------------------------------------------------------------------
    def _update_path_label(self):
        ok = getattr(self.pet, "save_ok", True)
        status = "saved ✓" if ok else "NOT SAVED ✗"
        mode = "portable" if config.is_portable() else "persistent"
        self.path_label.setText(f"Settings file ({mode}): {config.path()} — {status}")

    def _open_folder(self):
        try:
            platform_api.open_folder(os.path.dirname(config.path()))
        except Exception as exc:
            QMessageBox.warning(self, "Cannot open", str(exc))

    def _center_on_screen(self):
        scr = QGuiApplication.primaryScreen().availableGeometry()
        self.move(
            scr.center().x() - self.width() // 2,
            scr.center().y() - self.height() // 2,
        )
