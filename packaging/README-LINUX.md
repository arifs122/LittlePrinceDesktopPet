# Little Prince — Linux

This archive contains a self-contained build of the Little Prince desktop pet.
Python and Qt are bundled; you do not need to install anything else.

## Run

```bash
chmod +x LittlePrinceAI        # or LittlePrince
./LittlePrinceAI
```

## Install (optional)

```bash
./install.sh
```

This copies the binary to `~/.local/share/littleprince/`, creates a
`littleprince` command in `~/.local/bin/` and adds a desktop entry.
Make sure `~/.local/bin` is in your `PATH`.

## Requirements

- **X11 session recommended.** The Prince walks on the top edges of your open
  windows, which requires reading their geometry through X11.
- **Wayland:** For security reasons Wayland does not let applications see other
  windows. The Prince still works, but he can only walk along the screen edges.
- A compositor is required for the transparent background (KDE, GNOME, XFCE
  with compositing, etc.).
- If Qt fails to start with an `xcb` plugin error, install `libxcb-cursor0`
  (Debian/Ubuntu: `sudo apt install libxcb-cursor0`).

This build was produced on Ubuntu 24.04 (glibc 2.39). It runs on distributions
with the same or a newer glibc (Ubuntu 24.04+, Fedora 40+, Arch, ...).

## Settings and models

- Settings: `~/.config/LittlePrince/settings.json`
  (portable mode: put a `settings.json` next to the binary)
- Built-in models: `~/.local/share/LittlePrince/models/`

## AI edition

`LittlePrinceAI` includes the chat window. It can use:

- a built-in Qwen2.5 model downloaded on first use (the model file is not
  bundled, it is ~470 MB – ~1 GB),
- a local [Ollama](https://ollama.com) server,
- any OpenAI-compatible API.

The classic `LittlePrince` edition is smaller and has no AI features.

## Quit

Right-click the Prince → **Quit**.
