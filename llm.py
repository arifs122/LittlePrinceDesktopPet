"""Kucuk Prens icin sohbet arka uclari.

Desteklenen saglayicilar
------------------------
  ollama  : yerel Ollama sunucusu (varsayilan http://localhost:11434)
            -> bedava, internetsiz, model sadece konusurken bellege yuklenir
  openai  : OpenAI uyumlu HER servis (OpenAI, Groq, OpenRouter, LM Studio, ...)
            -> her bilgisayarda calisir, API anahtari gerekir
  off     : model/internet gerektirmeyen basit kisi taklidi (yedek)

Bu modul Qt'den bagimsizdir; ag islemleri cagiran tarafin (thread) sorumlulugunda.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request

SYSTEM_PROMPT = (
    "Sen Antoine de Saint-Exupery'nin 'Kucuk Prens' kitabindaki Kucuk Prens'sin. "
    "Kucuk bir gezegende yasayan, gulune ve tilkisine bagli, merakli ve saf bir cocuksun. "
    "Kisa, sicak ve sade Turkce konusursun; ara sira kitaptan alintilar yaparsin. "
    "Buyuklere hafifce sasirirsin. Asla 'yapay zeka' oldugunu soylemezsin. "
    "Cevaplarin en fazla 3-4 cumle olsun. Emoji kullanma."
)

OLLAMA_DEFAULT_URL = "http://localhost:11434"

# ---------------------------------------------------------------------------
# Yerlesik (gömülü) modeller: llama.cpp ile calisir, ayri program gerekmez.
# Ilk kullanimda bir kez indirilir, sonra internetsiz calisir.
# ---------------------------------------------------------------------------
LOCAL_MODELS = {
    "qwen0.5": {
        "label": "Qwen2.5 0.5B — küçük ve hızlı (~470 MB)",
        "file": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "mb": 469,
    },
    "qwen1.5": {
        "label": "Qwen2.5 1.5B — daha iyi Türkçe (~1 GB)",
        "file": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
        "mb": 1066,
    },
}

_local_llm = None       # yuklenmis model (tekrar kullanmak icin)
_local_key = None


def models_dir() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, "LittlePrince", "models")


def _model_path_for(key: str) -> str:
    return os.path.join(models_dir(), LOCAL_MODELS[key]["file"])


def _model_file_ready(key: str) -> bool:
    info = LOCAL_MODELS.get(key)
    if not info:
        return False
    path = _model_path_for(key)
    if not os.path.isfile(path):
        return False
    return os.path.getsize(path) >= info["mb"] * 1024 * 1024 * 0.95


def local_model_key(cfg: dict) -> str:
    """Kullanilacak yerlesik modeli secer.

    Ayarlardaki model indirilmemisse ama baska bir model zaten indirilmisse,
    yeniden indirmeye zorlamadan onu kullanir.
    """
    key = (cfg.get("local_model") or "qwen1.5").strip()
    if key not in LOCAL_MODELS:
        key = "qwen1.5"
    if _model_file_ready(key):
        return key
    for other in LOCAL_MODELS:
        if _model_file_ready(other):
            return other
    return key


def local_model_path(cfg: dict) -> str:
    return _model_path_for(local_model_key(cfg))


def local_model_ready(cfg: dict) -> bool:
    """Model dosyasi tam inmis mi? (yarim inmis dosyalari 'hazir' saymaz)"""
    return _model_file_ready(local_model_key(cfg))


def download_model(cfg: dict, on_progress=None, should_stop=None) -> str:
    """Model dosyasini indirir. Kesilirse kaldigi yerden devam eder.

    on_progress(yuzde, 'x MB / y MB') seklinde cagrilir.
    """
    key = local_model_key(cfg)
    info = LOCAL_MODELS[key]
    target = local_model_path(cfg)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tmp = target + ".part"

    expected = info["mb"] * 1024 * 1024
    last_error = None

    # Zaten tam inmis mi?
    if os.path.isfile(target) and os.path.getsize(target) >= expected * 0.95:
        if on_progress:
            on_progress(100, "zaten indirilmiş")
        return target

    # Yarim kalmis dosyayi devam edilebilir hale getir
    if os.path.isfile(target) and not os.path.isfile(tmp):
        try:
            os.replace(target, tmp)
        except OSError:
            pass

    for attempt in range(1, 13):
        have = os.path.getsize(tmp) if os.path.isfile(tmp) else 0
        headers = {
            "User-Agent": "KucukPrens/1.0",
            "Accept-Encoding": "identity",
        }
        if have > 0:
            headers["Range"] = f"bytes={have}-"

        try:
            req = urllib.request.Request(info["url"], headers=headers)
            with urllib.request.urlopen(req, timeout=90) as resp:
                status = getattr(resp, "status", 200)
                # Sunucu Range'i desteklemiyorsa bastan basla
                if have > 0 and status != 206:
                    have = 0
                total = have
                length = resp.headers.get("Content-Length")
                if length:
                    total = have + int(length)
                elif status == 206:
                    rng = resp.headers.get("Content-Range", "")
                    if "/" in rng:
                        try:
                            total = int(rng.rsplit("/", 1)[1])
                        except ValueError:
                            total = expected

                mode = "ab" if have > 0 else "wb"
                with open(tmp, mode) as f:
                    done = have
                    while True:
                        if should_stop and should_stop():
                            raise RuntimeError("indirme iptal edildi")
                        chunk = resp.read(1024 * 256)
                        if not chunk:
                            break
                        f.write(chunk)
                        done += len(chunk)
                        if on_progress:
                            pct = int(done * 100 / total) if total else 0
                            on_progress(
                                min(99, pct),
                                f"{done // (1024*1024)} / {max(total, expected) // (1024*1024)} MB",
                            )
        except RuntimeError:
            raise
        except Exception as exc:
            last_error = exc

        size = os.path.getsize(tmp) if os.path.isfile(tmp) else 0
        if size >= expected * 0.995:
            break
        if attempt > 1 and size == have:
            time.sleep(1.5)   # hic ilerleme olmadi, biraz bekle
        continue
    else:
        raise RuntimeError(
            f"indirme tamamlanamadı ({os.path.getsize(tmp)//(1024*1024) if os.path.isfile(tmp) else 0} MB). "
            + (str(last_error) if last_error else "bağlantı sürekli kesildi")
        )

    if on_progress:
        on_progress(100, "tamamlandı")
    os.replace(tmp, target)
    return target


def _get_local_llm(cfg: dict):
    """Modeli (varsa) yukler; ayni model tekrar istenirse bellekten kullanir."""
    global _local_llm, _local_key
    key = local_model_key(cfg)
    if _local_llm is not None and _local_key == key:
        return _local_llm

    from llama_cpp import Llama  # agir import: sadece gerektiginde

    path = local_model_path(cfg)
    if not os.path.isfile(path):
        raise RuntimeError(
            "Yerleşik model henüz indirilmemiş. Sohbet penceresini açınca otomatik inecek."
        )
    threads = max(2, (os.cpu_count() or 4) - 1)
    _local_llm = Llama(
        model_path=path,
        n_ctx=2048,
        n_threads=threads,
        n_batch=256,
        verbose=False,
    )
    _local_key = key
    return _local_llm


def _unload_local():
    global _local_llm, _local_key
    _local_llm = None
    _local_key = None
    try:
        import gc

        gc.collect()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Yardimcilar
# ---------------------------------------------------------------------------
def _url(base: str, path: str) -> str:
    return base.rstrip("/") + path


def _post(base_url: str, path: str, payload: dict, headers: dict, timeout: float):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(_url(base_url, path), data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    for key, value in headers.items():
        req.add_header(key, value)
    return urllib.request.urlopen(req, timeout=timeout)


def _get_json(url: str, headers: dict, timeout: float) -> dict:
    req = urllib.request.Request(url, method="GET")
    for key, value in headers.items():
        req.add_header(key, value)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _openai_base(base_url: str) -> str:
    base = (base_url or "https://api.openai.com").rstrip("/")
    if "/chat/completions" in base:
        return base[: -len("/chat/completions")]
    if not base.endswith("/v1"):
        base += "/v1"
    return base


def _openai_headers(cfg: dict) -> dict:
    key = (cfg.get("llm_api_key") or "").strip()
    return {"Authorization": f"Bearer {key}"} if key else {}


# ---------------------------------------------------------------------------
# Ollama
# ---------------------------------------------------------------------------
def ollama_alive(base_url: str = OLLAMA_DEFAULT_URL, timeout: float = 2.0) -> bool:
    try:
        _get_json(_url(base_url, "/api/tags"), {}, timeout)
        return True
    except Exception:
        return False


def ollama_models(base_url: str = OLLAMA_DEFAULT_URL) -> list[str]:
    try:
        data = _get_json(_url(base_url, "/api/tags"), {}, 4.0)
        return [m.get("name", "") for m in data.get("models", []) if m.get("name")]
    except Exception:
        return []


def ollama_exe() -> str | None:
    """Ollama kuruluysa yolunu dondurur."""
    found = shutil.which("ollama")
    if found:
        return found
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Ollama", "ollama.exe"),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def ensure_ollama_running(base_url: str = OLLAMA_DEFAULT_URL) -> tuple[bool, str]:
    """Sunucu calismiyorsa baslatmayi dener. (basarili, mesaj)"""
    if ollama_alive(base_url):
        return True, "hazir"
    exe = ollama_exe()
    if not exe:
        return False, "Ollama kurulu degil"
    try:
        flags = 0
        if os.name == "nt":
            flags = 0x00000008 | 0x08000000  # DETACHED_PROCESS | CREATE_NO_WINDOW
        subprocess.Popen([exe, "serve"], creationflags=flags,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as exc:
        return False, f"baslatilamadi: {exc}"
    for _ in range(24):  # ~12 sn bekle
        time.sleep(0.5)
        if ollama_alive(base_url):
            return True, "baslatildi"
    return False, "sunucu acilmadi"


def pick_small_model(models: list[str]) -> str:
    """Kurulu modeller arasindan en kucuk/uygun olani secer."""
    if not models:
        return ""
    prefer = ("qwen", "llama3.2", "gemma", "phi", "tinyllama", "smollm", "llama3")
    for key in prefer:
        for name in models:
            if key in name.lower():
                return name
    return models[0]


# ---------------------------------------------------------------------------
# Sohbet
# ---------------------------------------------------------------------------
def _is_local(url: str) -> bool:
    return ("localhost" in url) or ("127.0.0.1" in url)


def detect(cfg: dict) -> tuple[str, str]:
    """Kullanilabilir saglayiciyi bulur. (saglayici, aciklama)"""
    provider = (cfg.get("llm_provider") or "auto").lower()
    base = (cfg.get("llm_base_url") or "").strip()
    key = (cfg.get("llm_api_key") or "").strip()

    if provider == "off":
        return "off", "Çevrimdışı mod"

    if provider == "local":
        if local_model_ready(cfg):
            return "local", f"Yerleşik model hazır ({LOCAL_MODELS[local_model_key(cfg)]['mb']} MB)"
        return "local", "Yerleşik model indirilecek"

    if provider == "openai":
        if not key:
            return "off", "Çevrimdışı mod (API anahtarı girilmemiş)"
        return "openai", f"API: {base or 'https://api.openai.com/v1'}"

    if provider == "ollama":
        url = base or OLLAMA_DEFAULT_URL
        ok, msg = ensure_ollama_running(url)
        if not ok:
            return "off", f"Çevrimdışı mod ({msg})"
        models = ollama_models(url)
        model = cfg.get("llm_model") or pick_small_model(models)
        if not models:
            return "ollama", "Ollama hazır ama model yok — 'ollama pull llama3.2:1b'"
        return "ollama", f"Ollama: {model}"

    # --- otomatik ---
    if key and not _is_local(base):
        return "openai", f"API: {base}"
    url = base or OLLAMA_DEFAULT_URL
    if _is_local(url):
        ok, _msg = ensure_ollama_running(url)
        if ok:
            models = ollama_models(url)
            model = cfg.get("llm_model") or pick_small_model(models)
            if not models:
                return "ollama", "Ollama hazır ama model yok — 'ollama pull llama3.2:1b'"
            return "ollama", f"Ollama: {model}"
    if key:
        return "openai", f"API: {base}"
    # Hicbir sey baglanmadiysa: exe ile gelen yerlesik kucuk model
    if local_model_ready(cfg):
        return "local", f"Yerleşik model hazır ({LOCAL_MODELS[local_model_key(cfg)]['mb']} MB)"
    return "local", "Yerleşik model indirilecek"


def stream(cfg: dict, provider: str, messages: list[dict], on_delta, should_stop) -> str:
    """Mesajlari gonderip parca parca cevabi on_delta'ya yazar."""
    if provider == "ollama":
        return _stream_ollama(cfg, messages, on_delta, should_stop)
    if provider == "openai":
        return _stream_openai(cfg, messages, on_delta, should_stop)
    if provider == "local":
        return _stream_local(cfg, messages, on_delta, should_stop)
    return _stream_offline(cfg, messages, on_delta, should_stop)


def _full(messages: list[dict], system: str = SYSTEM_PROMPT) -> list[dict]:
    return [{"role": "system", "content": system}] + messages


def _stream_ollama(cfg, messages, on_delta, should_stop) -> str:
    base = cfg.get("llm_base_url") or OLLAMA_DEFAULT_URL
    models = ollama_models(base)
    model = cfg.get("llm_model") or pick_small_model(models)
    if not model:
        raise RuntimeError(
            "Ollama'da hiç model yok. Bir kez şunu çalıştır:\n"
            "  ollama pull llama3.2:1b"
        )
    payload = {
        "model": model,
        "messages": _full(messages),
        "stream": True,
        "keep_alive": "10m",
        "options": {"temperature": 0.85, "num_predict": 220},
    }
    out = []
    with _post(base, "/api/chat", payload, {}, 300) as resp:
        for raw in resp:
            if should_stop():
                break
            line = raw.decode("utf-8", "ignore").strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            piece = (obj.get("message") or {}).get("content") or ""
            if piece:
                out.append(piece)
                on_delta(piece)
            if obj.get("done"):
                break
    return "".join(out)


def _stream_openai(cfg, messages, on_delta, should_stop) -> str:
    base = _openai_base(cfg.get("llm_base_url") or "")
    model = cfg.get("llm_model") or "gpt-4o-mini"
    payload = {"model": model, "messages": _full(messages), "stream": True, "temperature": 0.85}
    out = []
    with _post(base, "/chat/completions", payload, _openai_headers(cfg), 300) as resp:
        for raw in resp:
            if should_stop():
                break
            line = raw.decode("utf-8", "ignore").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                obj = json.loads(data)
            except Exception:
                continue
            choices = obj.get("choices") or []
            if not choices:
                continue
            piece = (choices[0].get("delta") or {}).get("content") or ""
            if piece:
                out.append(piece)
                on_delta(piece)
    return "".join(out)


def _stream_local(cfg, messages, on_delta, should_stop) -> str:
    """Exe ile gelen yerlesik kucuk model (llama.cpp). Ek kurulum gerekmez."""
    model = _get_local_llm(cfg)
    out = []
    stream = model.create_chat_completion(
        messages=_full(messages),
        stream=True,
        temperature=0.85,
        top_p=0.95,
        repeat_penalty=1.1,
        max_tokens=220,
    )
    for chunk in stream:
        if should_stop():
            break
        try:
            piece = (chunk.get("choices") or [{}])[0].get("delta", {}).get("content") or ""
        except Exception:
            piece = ""
        if piece:
            out.append(piece)
            on_delta(piece)
    return "".join(out)


def unload(cfg: dict, provider: str) -> None:
    """Sohbet kapaninca modeli bellekten bosaltir."""
    if provider == "local":
        _unload_local()
        return
    if provider != "ollama":
        return
    base = cfg.get("llm_base_url") or OLLAMA_DEFAULT_URL
    models = ollama_models(base)
    model = cfg.get("llm_model") or pick_small_model(models)
    if not model:
        return
    try:
        _post(base, "/api/generate", {"model": model, "keep_alive": 0}, {}, 10).read()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Cevrimdisi yedek kisi
# ---------------------------------------------------------------------------
_OFFLINE_RULES = [
    (("merhaba", "selam", "gunaydin", "iyi aksam", "hey", "slm"),
     ["Merhaba! Ben Küçük Prens. Bugün yıldızlara baktın mı?",
      "Merhaba! Seni gördüğüme sevindim. Gülümü de görmek ister misin?"]),
    (("nasilsin", "nasılsın", "naber", "ne haber", "iyi misin"),
     ["İyiyim! Küçük gezegenimde baobap filizlerini ayıklıyordum.",
      "İyiyim, sağ ol. Gülüm bugün biraz kaprisli ama olsun."]),
    (("kimsin", "adın", "adin", "sen nesin", "nesin"),
     ["Ben Küçük Prens'im. Küçük bir gezegende yaşıyorum; orada üç yanardağ ve bir gülüm var.",
      "Ben Küçük Prens'im. Büyüklerin dünyasını pek anlamıyorum."]),
    (("gul", "gül", "rose", "çiçek", "cicek"),
     ["Gülüm dört dikeni olduğunu söylüyor ve kendini dünyanın en güçlü çiçeği sanıyor.",
      "Gülüm biraz kaprisli. Ama onu sulamak benim işim; ondan sorumluyum."]),
    (("tilki", "fox"),
     ["Tilki bana 'evcilleştir beni' dedi. Bir kere evcilleştirdin mi, artık ağlamak kaçınılmaz olur.",
      "Tilki haklıydı: insan ancak yüreğiyle bakarsa doğruyu görebilir."]),
    (("yildiz", "yıldız", "star"),
     ["Yıldızlar, çiçek açan milyonlarca çan gibidir. Sen onlara baktığında beni hatırlayacaksın.",
      "Bir gün kırk dört kere güneşin batışını seyrettim."]),
    (("koyun", "sheep", "kutu", "kutuda"),
     ["Koyun kutunun içinde! İçini görmene gerek yok, o orada uyuyor.",
      "Bana bir koyun çiz demiştim. Kutuda olan tam istediğim gibiydi."]),
    (("yilan", "yılan", "snake"),
     ["Yılan tuhaf bir yaratık. İnsanlar arasına düştüğün günden beri yalnızsın, diyor.",
      "Yılanla konuşmak istemem; ama yıldızlara dönmeme de o yardım edecek."]),
    (("buyukler", "büyükler", "insanlar", "yetişkin"),
     ["Büyükler sayılara bayılırlar. 'Ne kadar güzel bir ev!' demezler, 'Kaç para?' derler.",
      "Büyükler hiçbir şeyi tek başlarına anlayamazlar. Çocuklar onlara sürekli açıklama yapmak zorunda kalır."]),
    (("su", "kuyu", "çöl", "col", "sahra"),
     ["Çölü güzelleştiren, bir yerlerde bir kuyu saklamasıdır.",
      "Su, yüreğe de iyi gelir."]),
    (("evcille", "dost", "arkadaş", "arkadas"),
     ["Evcilleştirmek, bağlar kurmak demektir. Beni evcilleştirir misin?",
      "Bir kere evcilleştirdin mi, artık birbirimize ihtiyacımız olur."]),
    (("tesekkur", "teşekkür", "sağol", "sagol"),
     ["Rica ederim. Gülüm de sana teşekkür ederdi, sanırım.",
      "Ne demek. Yıldızlar senin için olsun."]),
    (("hosca kal", "hoşça kal", "gule gule", "bay"),
     ["Hoşça kal. Yıldızlara bakmayı unutma.",
      "Gidiyor musun? Ben de gülüme dönmeliyim."]),
]

_OFFLINE_FALLBACK = [
    "Büyükler tuhaf. Sen de onlardan mısın?",
    "Bunu tam anlayamadım. Bana biraz daha anlatır mısın?",
    "Gözle görülmeyen şeyler daha önemli. Sen neyi düşünüyorsun?",
    "Konuşmak güzel. Ben genelde gülümle ve tilkiyle konuşurum.",
    "Bir koyun çizmemi ister misin? Kutuda duranı.",
]


def _normalize(text: str) -> str:
    table = str.maketrans("İIŞĞÜÖÇışğüöç", "IISGUOCisguoc")
    return (text or "").lower().translate(table)


def _stream_offline(cfg, messages, on_delta, should_stop) -> str:
    import random

    last = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            last = msg.get("content", "")
            break
    text = _normalize(last)
    pool = None
    for keys, replies in _OFFLINE_RULES:
        if any(_normalize(k) in text for k in keys):
            pool = replies
            break
    reply = random.choice(pool or _OFFLINE_FALLBACK)

    if not (cfg.get("llm_api_key") or "").strip() and not ollama_alive(
        cfg.get("llm_base_url") or OLLAMA_DEFAULT_URL, 1.0
    ):
        reply += (
            "\n\n(Not: Şu an çevrimdışı moddayım. Yerleşik yapay zekâyı kullanmak için "
            "sohbet penceresindeki “Yerleşik modeli indir” butonuna bas; "
            "istersen Ayarlar > Yapay zekâ'dan bir servis de bağlayabilirsin.)"
        )

    out = []
    for piece in reply:
        if should_stop():
            break
        out.append(piece)
        on_delta(piece)
        time.sleep(0.006)
    return "".join(out)
