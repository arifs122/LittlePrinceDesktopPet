"""Oturma suresi ve isinlanma bekleme suresini test eder."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication

import pet as pet_mod


def main():
    app = QApplication(sys.argv)
    p = pet_mod.PetWindow()
    p.cfg["teleport_chance"] = 0.0
    p.cfg["sit_min_seconds"] = 10

    # --- oturma suresi ---
    sits = []
    for _ in range(400):
        p.sit_locked = False
        p.support_hwnd = None
        p.choose_action()
        if p.state == "sit":
            sits.append(p.action_frames)
    fps = 1000 / pet_mod.TICK_MS
    print(f"  oturma secildi: {len(sits)} kez")
    if sits:
        print(
            f"  en kisa={min(sits)} kare ({min(sits)/fps:.1f} sn), "
            f"en uzun={max(sits)} kare ({max(sits)/fps:.1f} sn) "
            + ("OK" if min(sits) >= 9.9 * fps else "SORUN: 10 sn'den kisa!")
        )

    # --- isinlanma bekleme suresi ---
    p.cfg["teleport_chance"] = 1.0
    p.cfg["teleport_cooldown"] = 20
    p.tp_cooldown = 0
    p.tp_phase = 0

    def fake_start():
        p.tp_target = ({"x1": 0, "x2": 900, "y": 500, "hwnd": None}, 100.0)
        p.tp_phase = 1
        return True

    p._start_teleport = fake_start
    p.choose_action()
    print(f"  ilk isinlanma: phase={p.tp_phase} cooldown={p.tp_cooldown:.1f} sn "
          + ("OK" if p.tp_cooldown == 20 else "SORUN"))

    # cooldown varken tekrar isinlanmamali
    p.tp_phase = 0
    blocked = True
    for _ in range(50):
        p.choose_action()
        if p.tp_phase:
            blocked = False
            break
    print(f"  cooldown varken tekrar denedi mi? {'HAYIR (OK)' if blocked else 'EVET (SORUN)'}")

    # cooldown bitince isinlanabilmeli
    p.tp_cooldown = 0.0
    p.tp_phase = 0
    for _ in range(50):
        p.choose_action()
        if p.tp_phase:
            break
    print(f"  cooldown bitince: phase={p.tp_phase} "
          + ("OK" if p.tp_phase else "SORUN"))

    # --- ayarlar kaydediliyor mu ---
    p.apply_settings({"teleport_cooldown": 33, "sit_min_seconds": 12})
    import config
    reloaded = config.load()
    print(
        f"  kaydedilen: cooldown={reloaded['teleport_cooldown']} "
        f"sit_min={reloaded['sit_min_seconds']} "
        + ("OK" if reloaded["teleport_cooldown"] == 33 else "SORUN")
    )
    p.apply_settings({"teleport_cooldown": 20, "sit_min_seconds": 10})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
