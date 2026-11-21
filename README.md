# Shura

**Lyrics for whatever is playing on Spotify, in a corner of your screen.**
Word by word, on a slowly moving background made from the album cover. Works on **Windows** and **Linux**.

## Download

| Platform | File |
|---|---|
| Windows 10 / 11 | [Windows/Shura.exe](Windows/Shura.exe?raw=1) |
| Linux | [Linux/shura.py](Linux/shura.py?raw=1) |

No installer, no account. Lyrics come from [lrclib.net](https://lrclib.net).

## Features

- Word-by-word highlight with a soft glow, like Apple Music / Beautiful Lyrics
- Blurred, slowly rotating background taken from the cover art
- Right-to-left lyrics (Hebrew, Arabic) laid out correctly
- Hover for play / pause / next / previous
- Click a line to jump to it, click the progress bar to seek
- Scroll over the lyrics to fix the sync if it's early or late
- Drag to move (snaps to corners), right-click for settings
- **Game mode (Windows):** stays on top of borderless full-screen games such as League of Legends, lets clicks pass through to the game and moves away from the minimap
- Never takes focus, fades out when the music is paused

## Lyric styles & backgrounds (Windows)

Right-click → **Lyric style**:

| Style | Looks like |
|---|---|
| Modern | Word-by-word highlight with a glow (default) |
| Headlines | Big, heavy words popping in one at a time, like Instagram lyric stickers |
| Typewriter | Monospace text typed out letter by letter, lines piling up |
| Simple | Plain lines, no effects |

Right-click → **Background**: moving blurred cover, the album cover itself, a solid colour from the cover, or plain dark.
If Windows doesn't provide the cover, Shura looks it up online (iTunes search).

## Windows

1. Download `Shura.exe` and run it.
2. If SmartScreen shows a blue warning, click **More info**, then **Run anyway** (the exe isn't code-signed).
3. Play something in the Spotify desktop app.

| Shortcut | Action |
|---|---|
| Right-click | Settings: position, size, opacity, sync, game mode |
| `Ctrl+Alt+L` | Hide / show |
| Mouse wheel over lyrics | Lyrics earlier / later |

**Games:** set the game's window mode to **Borderless**. Windows doesn't allow any window to draw over exclusive full screen.

## Linux

Tested on CachyOS / Arch with KDE Plasma (Wayland). Also works on Hyprland, Sway and X11.

```bash
sudo pacman -S --needed python-gobject python-cairo gtk3 gtk-layer-shell
python3 shura.py              # run
python3 shura.py --install    # add to the app menu
```

Works with the official Spotify app and the Flatpak version (through MPRIS).

## How it works

- **Now playing:** the Windows media session on Windows, MPRIS over D-Bus on Linux
- **Lyrics:** lrclib.net, cached locally. Uses word timings when the lyrics have them, otherwise estimates them from the line
- **Background:** the cover is shrunk to a few pixels, blurred and drawn huge in three slowly rotating layers
- **Windows app:** plain Win32 + GDI+ written in Go, no dependencies
- **Linux app:** a single Python file using GTK 3, Cairo and Pango

Inspired by [Beautiful Lyrics](https://github.com/surfbryce/beautiful-lyrics).
