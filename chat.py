"""Kucuk Prens ile sohbet penceresi.

Pencere acilinca yapay zeka hazirlanir, kapaninca model bellekten bosaltilir.
Yani model sadece konusmak istediginizde calisir.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QGuiApplication
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

import llm

MAX_HISTORY = 12

STYLE = """
QWidget { background: #FBF7F0; color: #33302B; }
QTextBrowser {
    background: #FFFFFF; border: 1px solid #E4DACA; border-radius: 10px;
    padding: 6px; font-size: 13px;
}
QLineEdit {
    background: #FFFFFF; border: 1px solid #E4DACA; border-radius: 8px;
    padding: 8px 10px; font-size: 13px;
}
QLineEdit:focus { border: 1px solid #C8A24A; }
QPushButton {
    background: #3EA34C; color: white; border: none; border-radius: 8px;
    padding: 8px 16px; font-size: 13px; font-weight: 600;
}
QPushButton:disabled { background: #B9C4B9; color: #EFEFEF; }
QPushButton#ghost {
    background: transparent; color: #6B6357; border: 1px solid #E4DACA;
    font-weight: 400;
}
QLabel#status { color: #8A8175; font-size: 11px; }
"""


def _esc(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )


class DetectWorker(QThread):
    """Kullanilabilir yapay zeka arka ucunu bulur (arayuzu bloklamaz)."""

    done = Signal(str, str)

    def __init__(self, cfg: dict):
        super().__init__()
        self.cfg = dict(cfg)

    def run(self):
        try:
            provider, desc = llm.detect(self.cfg)
        except Exception as exc:
            provider, desc = "off", f"Çevrimdışı mod ({exc})"
        self.done.emit(provider, desc)


class UnloadWorker(QThread):
    def __init__(self, cfg: dict, provider: str):
        super().__init__()
        self.cfg = dict(cfg)
        self.provider = provider

    def run(self):
        try:
            llm.unload(self.cfg, self.provider)
        except Exception:
            pass


class DownloadWorker(QThread):
    """Yerlesik modeli arka planda indirir."""

    progress = Signal(int, str)
    done = Signal(bool, str)

    def __init__(self, cfg: dict):
        super().__init__()
        self.cfg = dict(cfg)
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        try:
            llm.download_model(
                self.cfg,
                lambda pct, text: self.progress.emit(pct, text),
                lambda: self._stop,
            )
            self.done.emit(True, "")
        except Exception as exc:
            self.done.emit(False, str(exc))


class ChatWorker(QThread):
    delta = Signal(str)
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, cfg: dict, provider: str, messages: list[dict]):
        super().__init__()
        self.cfg = dict(cfg)
        self.provider = provider
        self.messages = messages
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        try:
            text = llm.stream(
                self.cfg,
                self.provider,
                self.messages,
                self.delta.emit,
                lambda: self._stop,
            )
            self.done.emit(text)
        except Exception as exc:
            self.failed.emit(str(exc))


class ChatWindow(QWidget):
    def __init__(self, pet):
        super().__init__(None, Qt.Window)
        self.pet = pet
        self.setWindowTitle("Talk to the Little Prince")
        self.setMinimumSize(420, 440)
        self.resize(450, 560)
        self.setStyleSheet(STYLE)

        self.history: list[dict] = []          # modele gonderilecek gecmis
        self.lines: list[list[str]] = []       # ekranda gorunenler  [rol, metin]
        self.provider = "off"
        self.provider_ready = False
        self._desc = ""
        self._pending = ""
        self._awaiting = False
        self._detect: DetectWorker | None = None
        self._worker: ChatWorker | None = None
        self._unload: UnloadWorker | None = None
        self._dl: DownloadWorker | None = None

        title = QLabel("🧭  Little Prince")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))

        btn_settings = QPushButton("Settings")
        btn_settings.setObjectName("ghost")
        btn_settings.clicked.connect(lambda: self.pet.open_settings())

        top = QHBoxLayout()
        top.addWidget(title)
        top.addStretch(1)
        top.addWidget(btn_settings)

        self.status = QLabel("Closed — open the window to talk")
        self.status.setObjectName("status")
        self.status.setWordWrap(True)

        self.view = QTextBrowser()
        self.view.setOpenExternalLinks(True)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type something and press Enter…")
        self.input.returnPressed.connect(self.send)
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send)

        self.dl_btn = QPushButton("Download built-in model")
        self.dl_btn.clicked.connect(self.start_download)
        self.dl_btn.hide()
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.hide()

        bottom = QHBoxLayout()
        bottom.addWidget(self.input, 1)
        bottom.addWidget(self.send_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)
        layout.addLayout(top)
        layout.addWidget(self.status)
        layout.addWidget(self.view, 1)
        layout.addWidget(self.dl_btn)
        layout.addWidget(self.progress)
        layout.addLayout(bottom)

        self._lines_append("prenses", "Hello! I am the Little Prince. Ask me anything.")

    # ------------------------------------------------------------------
    # Gorunum
    # ------------------------------------------------------------------
    def _lines_append(self, who: str, text: str):
        self.lines.append([who, text])
        self._render()

    def _render(self):
        parts = [
            "<style>"
            "p.who { margin:10px 0 2px 0; color:#8A8175; font-size:10px;"
            " letter-spacing:1px; }"
            "p.me { color:#3EA34C; }"
            "p.msg { margin:0 0 10px 0; font-size:13px; line-height:140%; }"
            "</style>"
        ]
        for who, text in self.lines:
            cls = "me" if who == "prenses" else ""
            label = "LITTLE PRINCE" if who == "prenses" else "YOU"
            parts.append(f'<p class="who {cls}">{label}</p>')
            parts.append(f'<p class="msg">{_esc(text)}</p>')
        self.view.setHtml("".join(parts))
        bar = self.view.verticalScrollBar()
        bar.setValue(bar.maximum())

    # ------------------------------------------------------------------
    # Acilis / kapanis
    # ------------------------------------------------------------------
    def show_chat(self):
        self.move_near(self.pet)
        self.show()
        self.raise_()
        self.activateWindow()
        self.input.setFocus()
        if not self.provider_ready and (self._detect is None or not self._detect.isRunning()):
            self._start_detect()

    def _start_detect(self):
        self.provider_ready = False
        self.send_btn.setEnabled(False)
        self.status.setText("Preparing the AI… (the model may load on first use)")
        self._detect = DetectWorker(self.pet.cfg)
        self._detect.done.connect(self._on_detected)
        self._detect.start()

    def _on_detected(self, provider: str, desc: str):
        self.provider = provider
        self._desc = desc
        self.provider_ready = True

        # Yerlesik model secili ama henuz indirilmemis -> indirme dugmesi goster
        if provider == "local" and not llm.local_model_ready(self.pet.cfg):
            info = llm.LOCAL_MODELS[llm.local_model_key(self.pet.cfg)]
            self.dl_btn.setText(f"Download built-in model (~{info['mb']} MB)")
            self.dl_btn.setEnabled(True)
            self.dl_btn.show()
            self.progress.hide()
            self.send_btn.setEnabled(False)
            self.input.setEnabled(False)
            self.status.setText(
                "No service is connected. We can run the small model that ships with the app. "
                "Press the button to download it (~470 MB)."
            )
            return

        self.dl_btn.hide()
        self.progress.hide()
        self.send_btn.setEnabled(True)
        self.input.setEnabled(True)
        if provider == "off":
            self.status.setText(
                f"Connection: {desc} — gerçek yapay zekâ için Ayarlar > Yapay zekâ"
            )
        else:
            self.status.setText(f"Connection: {desc}")

    # ------------------------------------------------------------------
    def start_download(self):
        self.dl_btn.setEnabled(False)
        self.progress.setValue(0)
        self.progress.show()
        self.status.setText("Downloading the model… (closing the window stops it)")
        self._dl = DownloadWorker(self.pet.cfg)
        self._dl.progress.connect(self._on_progress)
        self._dl.done.connect(self._on_downloaded)
        self._dl.start()

    def _on_progress(self, pct: int, text: str):
        self.progress.setValue(pct)
        self.status.setText(f"Downloading… %{pct}  ({text})")

    def _on_downloaded(self, ok: bool, err: str):
        if ok:
            self.dl_btn.hide()
            self.progress.hide()
            self.status.setText("Built-in model ready — ask away!")
            self.send_btn.setEnabled(True)
            self.input.setEnabled(True)
            self.input.setFocus()
        else:
            self.progress.hide()
            self.dl_btn.setEnabled(True)
            self.status.setText(f"Download failed: {err}")

    def closeEvent(self, event):
        if self._worker is not None and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(3000)
        if self._dl is not None and self._dl.isRunning():
            self._dl.stop()
            self._dl.wait(3000)
        self.provider_ready = False
        # Modeli bellekten bosalt: yapay zeka artik calismasin
        self._unload = UnloadWorker(self.pet.cfg, self.provider)
        self._unload.start()
        event.accept()

    def move_near(self, pet):
        scr = QGuiApplication.primaryScreen().availableGeometry()
        x = min(max(scr.left() + 12, pet.x + pet.W + 14), scr.right() - self.width() - 12)
        y = min(max(scr.top() + 12, pet.y - 60), scr.bottom() - self.height() - 12)
        self.move(int(x), int(y))

    # ------------------------------------------------------------------
    # Sohbet
    # ------------------------------------------------------------------
    def send(self):
        if self._worker is not None and self._worker.isRunning():
            return
        text = self.input.text().strip()
        if not text or not self.provider_ready:
            return

        self.input.clear()
        self._lines_append("sen", text)
        self.history.append({"role": "user", "content": text})
        self.history = self.history[-MAX_HISTORY:]

        self._pending = ""
        self._awaiting = True
        self._lines_append("prenses", "…")
        self.send_btn.setEnabled(False)
        self.input.setEnabled(False)
        if self.provider == "local":
            self.status.setText(
                "Preparing the model… (the first message may take a few seconds)"
            )

        self._worker = ChatWorker(self.pet.cfg, self.provider, list(self.history))
        self._worker.delta.connect(self._on_delta)
        self._worker.done.connect(self._on_done)
        self._worker.failed.connect(self._on_failed)
        self._worker.start()

    def _on_delta(self, piece: str):
        self._pending += piece
        if self.lines and self.lines[-1][0] == "prenses":
            self.lines[-1][1] = self._pending
        else:
            self.lines.append(["prenses", self._pending])
        self._render()

    def _finish(self, text: str, error: str | None = None):
        if not self._awaiting:
            return
        self._awaiting = False
        self.send_btn.setEnabled(True)
        self.input.setEnabled(True)
        self.input.setFocus()
        if self._desc:
            self.status.setText(f"Connection: {self._desc}")

        if error:
            if self.history and self.history[-1]["role"] == "user":
                self.history.pop()
            if self.lines and self.lines[-1][0] == "prenses":
                self.lines.pop()
            self._lines_append("prenses", f"⚠ Something went wrong: {error}")
            return

        final = (text or self._pending).strip() or "…"
        if self.lines and self.lines[-1][0] == "prenses":
            self.lines[-1][1] = final
        else:
            self.lines.append(["prenses", final])
        self._render()

        self.history.append({"role": "assistant", "content": final})
        self.history = self.history[-MAX_HISTORY:]

        short = final.split("\n")[0].strip()
        if len(short) > 90:
            short = short[:87] + "…"
        if short and self.pet is not None:
            self.pet.bubble.say(short, 5.0)

    def _on_done(self, text: str):
        self._finish(text)

    def _on_failed(self, message: str):
        self._finish("", error=message)
