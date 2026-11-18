#!/usr/bin/env python3
# Shura - Spotify lyrics in a corner of the screen (Linux: Wayland via layer-shell, or X11).
#
#   ./shura.py              run
#   ./shura.py --install    add to the app menu (~/.local)
#   ./shura.py --uninstall  remove it again
#
# Needs (CachyOS / Arch):  sudo pacman -S --needed python-gobject python-cairo gtk3 gtk-layer-shell

import base64
import colorsys
import hashlib
import json
import math
import os
import re
import shutil
import sys
import threading
import time
import urllib.parse
import urllib.request

APP_ID = "io.github.shura"
HOME = os.path.expanduser("~")
CONF_DIR = os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.join(HOME, ".config")), "shura")
CACHE_DIR = os.path.join(os.environ.get("XDG_CACHE_HOME", os.path.join(HOME, ".cache")), "shura")
DEPS_HINT = "sudo pacman -S --needed python-gobject python-cairo gtk3 gtk-layer-shell"
ICON_PNG = base64.b64decode("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")


# ------------------------------------------------------------------ install

def desktop_entry(exec_path):
    return (
        "[Desktop Entry]\nType=Application\nName=Shura\nComment=Spotify lyrics in a corner of the screen\n"
        "Comment[he]=מילים לשירים מספוטיפיי בפינת המסך\n"
        f"Exec=\"{exec_path}\"\nIcon=shura\nTerminal=false\nCategories=AudioVideo;Audio;\nStartupNotify=false\n"
    )


def install():
    bin_dir = os.path.join(HOME, ".local", "bin")
    app_dir = os.path.join(HOME, ".local", "share", "applications")
    icon_dir = os.path.join(HOME, ".local", "share", "icons", "hicolor", "256x256", "apps")
    for d in (bin_dir, app_dir, icon_dir):
        os.makedirs(d, exist_ok=True)
    target = os.path.join(bin_dir, "shura")
    shutil.copyfile(os.path.abspath(__file__), target)
    os.chmod(target, 0o755)
    with open(os.path.join(icon_dir, "shura.png"), "wb") as f:
        f.write(ICON_PNG)
    with open(os.path.join(app_dir, "shura.desktop"), "w") as f:
        f.write(desktop_entry(target))
    print("Installed. Shura is now in your app menu (or run: shura).")


def uninstall():
    for p in (
        os.path.join(HOME, ".local", "bin", "shura"),
        os.path.join(HOME, ".local", "share", "applications", "shura.desktop"),
        os.path.join(HOME, ".local", "share", "icons", "hicolor", "256x256", "apps", "shura.png"),
        os.path.join(HOME, ".config", "autostart", "shura.desktop"),
    ):
        try:
            os.remove(p)
        except FileNotFoundError:
            pass
    print("Removed.")


if "--install" in sys.argv:
    install()
    sys.exit(0)
if "--uninstall" in sys.argv:
    uninstall()
    sys.exit(0)


# ------------------------------------------------------------------ imports

def fail(msg):
    sys.stderr.write(msg + "\n")
    for cmd in (["notify-send", "Shura", msg], ["kdialog", "--sorry", msg]):
        if shutil.which(cmd[0]):
            os.spawnvp(os.P_NOWAIT, cmd[0], cmd)
            break
    sys.exit(1)


try:
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    gi.require_version("Pango", "1.0")
    gi.require_version("PangoCairo", "1.0")
    gi.require_version("GdkPixbuf", "2.0")
    import cairo
    gi.require_foreign("cairo")
except (ImportError, ValueError) as e:
    fail(f"Shura is missing a few packages ({e}).\nInstall them with:\n  {DEPS_HINT}")

LAYER = None
if os.environ.get("WAYLAND_DISPLAY") and os.environ.get("GDK_BACKEND", "") != "x11":
    try:
        gi.require_version("GtkLayerShell", "0.1")
        from gi.repository import GtkLayerShell as LAYER  # noqa: N812
    except (ImportError, ValueError):
        # no layer-shell: run through XWayland, where a window may position itself
        os.environ["GDK_BACKEND"] = "x11"

from gi.repository import Gdk, GdkPixbuf, Gio, GLib, Gtk, Pango, PangoCairo  # noqa: E402

if LAYER is not None and hasattr(LAYER, "is_supported") and not LAYER.is_supported():
    env = dict(os.environ, GDK_BACKEND="x11")
    os.execvpe(sys.executable, [sys.executable] + sys.argv, env)


# ------------------------------------------------------------------ settings

DEFAULTS = {"corner": "BR", "mx": None, "my": None, "x": None, "y": None, "size": "M",
            "idle_opacity": 0.92, "compact": False, "offset_ms": 0, "stay_paused": False, "hidden": False,
            "karaoke": True, "over_fullscreen": True}


class Settings(dict):
    path = os.path.join(CONF_DIR, "settings.json")

    def __init__(self):
        super().__init__(DEFAULTS)
        try:
            with open(self.path) as f:
                self.update({k: v for k, v in json.load(f).items() if k in DEFAULTS})
        except (OSError, ValueError):
            pass
        if self["size"] not in ("S", "M", "L"):
            self["size"] = "M"

    def save(self):
        os.makedirs(CONF_DIR, exist_ok=True)
        try:
            with open(self.path, "w") as f:
                json.dump(self, f, indent=2)
        except OSError:
            pass


# ------------------------------------------------------------------ lyrics

RE_TS = re.compile(r"\[(\d+):(\d+(?:[.:]\d+)?)\]")
RE_WORD = re.compile(r"<\d+:\d+(?:[.:]\d+)?>")
RE_PAREN = re.compile(r"\s*[(\[][^)\]]*(feat|ft\.|with |remaster|live|version|edit|mix|mono|stereo)[^)\]]*[)\]]", re.I)
RE_DASH = re.compile(r"\s+-\s+.*(remaster|live|version|edit|mix|mono|stereo).*$", re.I)


def is_rtl(s):
    return any(0x0590 <= ord(c) <= 0x06FF or 0xFB1D <= ord(c) <= 0xFDFF for c in s)


def parse_lrc(text):
    out = []
    for raw in text.replace("\r", "").split("\n"):
        stamps = RE_TS.findall(raw)
        if not stamps:
            continue
        body = RE_TS.sub("", raw)
        words = " ".join(RE_WORD.sub("", body).split())
        wt = parse_word_times(body)
        for m, s in stamps:
            entry = {"t": int(m) * 60 + float(s.replace(":", ".", 1)), "x": words}
            if wt:
                entry["w"] = wt
            out.append(entry)
    out.sort(key=lambda l: l["t"])
    res = []
    for l in out:
        if l["x"] == "" and res and res[-1]["x"] == "":
            continue
        res.append(l)
    if res and res[0]["t"] > 2.5 and res[0]["x"]:
        res.insert(0, {"t": 0.0, "x": ""})
    return res


RE_WORD_CAP = re.compile(r"<(\d+):(\d+(?:[.:]\d+)?)>")


def parse_word_times(body):
    """Enhanced LRC: '<00:12.30> word <00:13.00> next' -> [[time, word], ...]"""
    tags = list(RE_WORD_CAP.finditer(body))
    out = []
    for i, m in enumerate(tags):
        t = int(m.group(1)) * 60 + float(m.group(2).replace(":", ".", 1))
        end = tags[i + 1].start() if i + 1 < len(tags) else len(body)
        nxt = (int(tags[i + 1].group(1)) * 60 + float(tags[i + 1].group(2).replace(":", ".", 1))) if i + 1 < len(tags) else t
        chunk = body[m.end():end].split()
        for j, w in enumerate(chunk):
            out.append([t + (nxt - t) * j / len(chunk) if nxt > t and len(chunk) > 1 else t, w])
    return out


def parse_plain(text):
    return [{"t": -1, "x": l.strip()} for l in text.replace("\r", "").split("\n") if l.strip()]


def clean_title(t):
    return RE_DASH.sub("", RE_PAREN.sub("", t)).strip()


def pick(items, dur):
    plain, instr = None, False
    for it in items or []:
        d = it.get("duration") or 0
        if dur > 0 and d > 0 and abs(d - dur) > 8:
            continue
        if (it.get("syncedLyrics") or "").strip():
            lines = parse_lrc(it["syncedLyrics"])
            if lines:
                return {"synced": True, "lines": lines}
        if plain is None and (it.get("plainLyrics") or "").strip():
            plain = {"synced": False, "lines": parse_plain(it["plainLyrics"])}
        instr = instr or bool(it.get("instrumental"))
    if plain:
        return plain
    if instr:
        return {"synced": False, "instrumental": True, "lines": []}
    return None


def cache_path(artist, title):
    h = hashlib.sha1(f"{artist}|{title}".lower().encode()).hexdigest()
    return os.path.join(CACHE_DIR, "lyrics", h + ".json")


def fetch_lyrics(artist, title, dur):
    """Returns lyrics dict, None if not found; raises OSError on network trouble."""
    cp = cache_path(artist, title)
    try:
        with open(cp) as f:
            return json.load(f)
    except (OSError, ValueError):
        pass
    q = urllib.parse.quote
    ct, ca = clean_title(title), artist.split(",")[0].strip()
    urls = [f"https://lrclib.net/api/search?track_name={q(title)}&artist_name={q(artist)}"]
    if ct != title or ca != artist:
        urls.append(f"https://lrclib.net/api/search?track_name={q(ct)}&artist_name={q(ca)}")
    urls.append(f"https://lrclib.net/api/search?q={q(ct + ' ' + ca)}")
    fallback, any_ok = None, False
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Shura/1.0"})
            with urllib.request.urlopen(req, timeout=12) as r:
                items = json.load(r)
        except (OSError, ValueError):
            continue
        any_ok = True
        best = pick(items, dur)
        if best and (best["synced"] or best.get("instrumental")):
            fallback = best
            break
        if best and fallback is None:
            fallback = best
    if fallback:
        os.makedirs(os.path.dirname(cp), exist_ok=True)
        try:
            with open(cp, "w") as f:
                json.dump(fallback, f)
        except OSError:
            pass
        return fallback
    if not any_ok:
        raise OSError("network")
    return None


# ------------------------------------------------------------------ colour

def to_hsl(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h, s, l


def from_hsl(h, s, l):
    return colorsys.hls_to_rgb(h, l, s)


def accent_from_pixbuf(pb):
    w, h, n, rs = pb.get_width(), pb.get_height(), pb.get_n_channels(), pb.get_rowstride()
    px = pb.get_pixels()
    buckets = 18
    ws, rsum, gsum, bsum = [0.0] * buckets, [0.0] * buckets, [0.0] * buckets, [0.0] * buckets
    ar = ag = ab = an = 0.0
    step = 24
    for yi in range(step):
        for xi in range(step):
            x = (xi * w) // step + w // (2 * step)
            y = (yi * h) // step + h // (2 * step)
            o = y * rs + x * n
            r, g, b = px[o] / 255, px[o + 1] / 255, px[o + 2] / 255
            ar, ag, ab, an = ar + r, ag + g, ab + b, an + 1
            hh, s, l = to_hsl(r, g, b)
            if l < 0.12 or l > 0.92 or s < 0.18:
                continue
            wt = s * (1 - abs(l - 0.5) * 1.6)
            if wt <= 0:
                continue
            i = int(hh * buckets) % buckets
            ws[i] += wt
            rsum[i] += wt * r
            gsum[i] += wt * g
            bsum[i] += wt * b
    best, bw = -1, 0.0
    for i in range(buckets):
        v = ws[i] + 0.5 * ws[(i + 1) % buckets] + 0.5 * ws[(i - 1) % buckets]
        if v > bw:
            best, bw = i, v
    if best >= 0 and bw > 4 and ws[best] > 0:
        return rsum[best] / ws[best], gsum[best] / ws[best], bsum[best] / ws[best]
    return (ar / an, ag / an, ab / an) if an else DEFAULT_ACCENT


def card_color(c):
    h, s, l = to_hsl(*c)
    if s < 0.12:
        return from_hsl(h, s, min(max(l * 0.5, 0.17), 0.24))
    s, l = max(0.32, min(s, 0.6)), 0.32
    if 0.10 < h < 0.45:
        l, s = 0.30, min(s, 0.5)
    return from_hsl(h, s, l)


DEFAULT_ACCENT = (0.17, 0.17, 0.18)


def mixc(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


# ------------------------------------------------------------------ Spotify over MPRIS

class Player:
    PLAYER = "org.mpris.MediaPlayer2.Player"
    PATH = "/org/mpris/MediaPlayer2"

    def __init__(self):
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.name = None
        self.owner = None
        self.ok = False
        self.title = self.artist = self.album = self.art_url = self.trackid = ""
        self.length = 0.0
        self.playing = False
        self.raw, self.raw_at = 0.0, time.monotonic()
        self.reliable = False
        self.track_at = time.monotonic()
        self.seen_nonzero = False
        self.ignore_until = 0.0
        self._busy = False
        self._last_find = 0.0
        self.bus.signal_subscribe(None, self.PLAYER, "Seeked", self.PATH, None,
                                  Gio.DBusSignalFlags.NONE, self._on_seeked)

    def _find(self):
        try:
            res = self.bus.call_sync("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus",
                                     "ListNames", None, GLib.VariantType.new("(as)"), Gio.DBusCallFlags.NONE, 1000, None)
        except GLib.Error:
            return None
        names = [n for n in res.unpack()[0] if n.startswith("org.mpris.MediaPlayer2.")]
        for n in names:
            if n.startswith("org.mpris.MediaPlayer2.spotify"):
                return n
        for n in names:
            if "spot" in n.lower():
                return n
        return None

    def pos(self):
        if not self.playing:
            return self.raw
        p = self.raw + (time.monotonic() - self.raw_at)
        return min(p, self.length) if self.length > 0 else p

    def poll(self):
        if self._busy:
            return
        now = time.monotonic()
        if self.name is None:
            if now - self._last_find < 2:
                return
            self._last_find = now
            self.name = self._find()
            if self.name is None:
                self.ok = False
                return
            try:
                self.owner = self.bus.call_sync("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus",
                                                "GetNameOwner", GLib.Variant("(s)", (self.name,)),
                                                GLib.VariantType.new("(s)"), Gio.DBusCallFlags.NONE, 1000, None).unpack()[0]
            except GLib.Error:
                self.owner = None
        self._busy = True
        self.bus.call(self.name, self.PATH, "org.freedesktop.DBus.Properties", "GetAll",
                      GLib.Variant("(s)", (self.PLAYER,)), GLib.VariantType.new("(a{sv})"),
                      Gio.DBusCallFlags.NONE, 1500, None, self._on_props)

    def _on_props(self, bus, result):
        self._busy = False
        try:
            props = bus.call_finish(result).unpack()[0]
        except GLib.Error:
            self.name, self.ok = None, False
            return
        now = time.monotonic()
        meta = props.get("Metadata") or {}
        artist = meta.get("xesam:artist") or []
        if isinstance(artist, str):
            artist = [artist]
        title = meta.get("xesam:title") or ""
        artist = ", ".join(a for a in artist if a)
        if (artist, title) != (self.artist, self.title):
            self.track_at = now
            self.seen_nonzero = False
            self.raw, self.raw_at = 0.0, now
        self.title, self.artist = title, artist
        self.album = meta.get("xesam:album") or ""
        self.trackid = meta.get("mpris:trackid") or ""
        url = meta.get("mpris:artUrl") or ""
        self.art_url = url.replace("https://open.spotify.com/image/", "https://i.scdn.co/image/")
        self.length = (meta.get("mpris:length") or 0) / 1e6
        self.ok = bool(title)
        if now < self.ignore_until:
            return
        playing = props.get("PlaybackStatus") == "Playing"
        if playing != self.playing:
            self.raw, self.raw_at = self.pos(), now  # freeze/resume the local clock
            self.playing = playing
        rp = (props.get("Position") or 0) / 1e6
        if rp > 0.5:
            self.seen_nonzero = True
        # some Spotify builds always report 0 here; then we keep our own clock
        self.reliable = self.seen_nonzero
        if self.reliable and abs(rp - self.pos()) > 0.35:
            self.raw, self.raw_at = rp, now

    def _on_seeked(self, conn, sender, path, iface, signal, params):
        if self.owner and sender != self.owner:
            return
        self.raw, self.raw_at = params.unpack()[0] / 1e6, time.monotonic()
        self.seen_nonzero = True

    def call(self, method, params=None):
        if self.name:
            self.bus.call(self.name, self.PATH, self.PLAYER, method, params, None,
                          Gio.DBusCallFlags.NONE, 1500, None, lambda b, r: self._done(b, r))

    def _done(self, bus, result):
        try:
            bus.call_finish(result)
        except GLib.Error:
            pass

    def toggle(self):
        self.raw, self.raw_at = self.pos(), time.monotonic()
        self.playing = not self.playing
        self.ignore_until = time.monotonic() + 0.9
        self.call("PlayPause")

    def seek(self, sec):
        sec = max(0.0, sec)
        if self.trackid:
            self.call("SetPosition", GLib.Variant("(ox)", (self.trackid, int(sec * 1e6))))
        else:
            self.call("Seek", GLib.Variant("(x)", (int((sec - self.pos()) * 1e6),)))
        self.raw, self.raw_at = sec, time.monotonic()
        self.ignore_until = time.monotonic() + 0.9


# ------------------------------------------------------------------ drawing helpers

def rrect(cr, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    cr.close_path()


def fmt_time(s):
    s = int(max(0, s))
    return f"{s // 60}:{s % 60:02d}"


def esc(s):
    return GLib.markup_escape_text(s)


def ease(dt, speed):
    return 1 - math.exp(-dt * speed)


ST_NONE, ST_SEARCH, ST_OK, ST_NOTFOUND, ST_INSTR, ST_ERROR = range(6)
FONT = "Inter, Noto Sans, Cantarell, DejaVu Sans, sans"


# ------------------------------------------------------------------ moving cover background

BD_LAYERS = ((0.30, 0.35, 1.9, 0.045, 0.0, 1.0), (0.75, 0.70, 1.6, -0.032, 1.7, 0.45),
             (0.55, 0.15, 2.3, 0.021, 3.1, 0.22))


def pixbuf_rgb(pb):
    w, h, n, rs = pb.get_width(), pb.get_height(), pb.get_n_channels(), pb.get_rowstride()
    px = pb.get_pixels()
    return [[(px[y * rs + x * n] / 255, px[y * rs + x * n + 1] / 255, px[y * rs + x * n + 2] / 255)
             for x in range(w)] for y in range(h)]


class Backdrop:
    """A tiny, very blurred copy of the cover, drawn huge and slowly rotating in a few layers."""

    def __init__(self, pb=None, color=(0.22, 0.22, 0.26)):
        n = 6
        if pb is not None:
            grid = pixbuf_rgb(pb.scale_simple(n, n, GdkPixbuf.InterpType.HYPER))
        else:
            a, b = mixc(color, (1, 1, 1), 0.12), mixc(color, (0, 0, 0), 0.45)
            grid = [[mixc(a, b, (x + y) / (2 * n)) for x in range(n)] for y in range(n)]
        out = []
        lum = 0.0
        for row in grid:
            r2 = []
            for c in row:
                h, s, l = to_hsl(*c)
                c = from_hsl(h, min(1.0, s * 1.35), l)
                lum += 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
                r2.append(c)
            out.append(r2)
        lum /= n * n
        mul = max(0.35, min(1.15, 0.30 / max(lum, 0.01)))
        data = bytearray()
        for row in out:
            for c in row:
                data += bytes(int(max(0, min(1, v * mul)) * 255) for v in c)
        small = GdkPixbuf.Pixbuf.new_from_bytes(GLib.Bytes.new(bytes(data)), GdkPixbuf.Colorspace.RGB,
                                                False, 8, n, n, n * 3)
        big = small.scale_simple(48, 48, GdkPixbuf.InterpType.BILINEAR)
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 48, 48)
        c2 = cairo.Context(self.surface)
        Gdk.cairo_set_source_pixbuf(c2, big, 0, 0)
        c2.paint()
        self.pattern = cairo.SurfacePattern(self.surface)
        self.pattern.set_extend(cairo.EXTEND_REFLECT)
        self.pattern.set_filter(cairo.FILTER_BILINEAR)

    def paint(self, cr, w, h, t):
        size = max(w, h)
        for cx, cy, scale, speed, phase, alpha in BD_LAYERS:
            m = cairo.Matrix()
            m.translate(24, 24)
            f = 48 / (size * scale)
            m.scale(f, f)
            m.rotate(t * speed + phase)
            m.translate(-cx * w, -cy * h)
            self.pattern.set_matrix(m)
            cr.set_source(self.pattern)
            cr.paint_with_alpha(alpha)


def sweep(x0, x1, frac, feather, rtl, on, off):
    """Gradient that is 'on' up to frac of the word (in reading direction), 'off' after."""
    g = cairo.LinearGradient(x1 + feather, 0, x0 - feather, 0) if rtl else cairo.LinearGradient(x0 - feather, 0, x1 + feather, 0)
    span = (x1 - x0) + 2 * feather or 1
    pos = (feather + (x1 - x0) * frac) / span
    e = feather / span
    a, b = max(0.0, pos - e), min(1.0, pos + e)
    g.add_color_stop_rgba(0, *on)
    g.add_color_stop_rgba(a, *on)
    g.add_color_stop_rgba(b, *off)
    g.add_color_stop_rgba(1, *off)
    return g


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


# ------------------------------------------------------------------ the window

class Overlay(Gtk.Window):
    def __init__(self, app):
        super().__init__(type=Gtk.WindowType.TOPLEVEL, title="Shura")
        self.app = app
        self.cfg = Settings()
        self.player = Player()
        self.set_application(app)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_app_paintable(True)
        self.set_accept_focus(False)
        self.set_focus_on_map(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        vis = self.get_screen().get_rgba_visual()
        if vis is not None:
            self.set_visual(vis)
        try:
            loader = GdkPixbuf.PixbufLoader.new_with_type("png")
            loader.write(ICON_PNG)
            loader.close()
            self.set_icon(loader.get_pixbuf())
        except GLib.Error:
            pass

        if LAYER is not None:
            LAYER.init_for_window(self)
            LAYER.set_layer(self, LAYER.Layer.OVERLAY if self.cfg["over_fullscreen"] else LAYER.Layer.TOP)
            LAYER.set_namespace(self, "shura")
            if hasattr(LAYER, "set_keyboard_mode"):
                LAYER.set_keyboard_mode(self, LAYER.KeyboardMode.NONE)
            else:
                LAYER.set_keyboard_interactivity(self, False)
        else:
            self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
            self.set_keep_above(True)
            self.stick()

        self.area = Gtk.DrawingArea()
        self.add(self.area)
        self.area.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK |
                             Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.SCROLL_MASK |
                             Gdk.EventMask.SMOOTH_SCROLL_MASK | Gdk.EventMask.ENTER_NOTIFY_MASK |
                             Gdk.EventMask.LEAVE_NOTIFY_MASK)
        self.area.connect("draw", self.on_draw)
        self.area.connect("motion-notify-event", self.on_motion)
        self.area.connect("button-press-event", self.on_press)
        self.area.connect("button-release-event", self.on_release)
        self.area.connect("scroll-event", self.on_scroll)
        self.area.connect("enter-notify-event", self.on_enter)
        self.area.connect("leave-notify-event", self.on_leave)
        self.connect("realize", lambda *_: self.update_input_shape())
        self.connect("configure-event", self.on_configure)

        # state
        self.key = ""
        self.key_at = 0.0
        self.fetch_key = None
        self.retry_at = 0.0
        self.status = ST_NONE
        self.status_at = time.monotonic()
        self.lyrics = None
        self.lays = []           # [y, h, state, layout]
        self.scroll = 0.0
        self.scroll_ok = False
        self.cur = -1
        self.cur_t = 0.0
        self.lyr_rtl = False
        self.mirror = False
        self.art = None
        self.art_url = None
        self.art_cache = {}
        self.accent = DEFAULT_ACCENT
        self.accent_target = DEFAULT_ACCENT
        self.hover = False
        self.mx = self.my = 0.0
        self.hover_btn = self.hover_line = -1
        self.hover_prog = False
        self.press = None
        self.drag = None
        self.ctrl_a = 0.0
        self.vis_a = 0.0
        self.op_a = 1.0
        self.shown = False
        self.last_playing = -100.0
        self.toast = ""
        self.toast_until = 0.0
        self.line_hits = []
        self.last_tick = time.monotonic()
        self.last_draw = 0.0
        self.last_poll = 0.0
        self.dirty = True
        self.bd = Backdrop()
        self.prev_bd = None
        self.bd_fade = 1.0
        self.bd_surface = None
        self.last_bd = 0.0
        self.started = time.monotonic()

        self.layout()
        GLib.timeout_add(16, self.tick)

    # -------------------------------------------------------------- geometry

    def compact(self):
        return self.cfg["compact"]

    def layout(self):
        k = {"S": 0.85, "L": 1.25}.get(self.cfg["size"], 1.0)
        self.k = k
        self.m = round(14 * k)                       # room for the shadow
        cw = round(420 * k)
        lyr_h = 150 * k if self.compact() else 186 * k
        strip_h = 0 if self.compact() else 42 * k
        ch = round(lyr_h + strip_h + 2 * k)
        self.W, self.H = cw + 2 * self.m, ch + 2 * self.m
        self.card = (self.m, self.m, cw, ch)
        cx, cy = self.m, self.m
        self.r_lyr = (cx + 22 * k, cy + 14 * k, cw - 44 * k, lyr_h - 14 * k)
        sh = 42 * k
        self.r_strip = (cx, cy + ch - 2 * k - sh, cw, sh + 2 * k)
        sx, sy, sw, _ = self.r_strip
        a = 24 * k
        self.r_art = (sx + sw - 12 * k - a if self.mirror else sx + 12 * k, sy + (sh - a) / 2, a, a)
        bw = 30 * k
        ctl_w = bw * 4
        if self.mirror:
            bx = sx + 8 * k
            self.btn_kind = ["menu", "prev", "play", "next"]
            self.r_time = (sx + 12 * k, sy, 90 * k, sh)
        else:
            bx = sx + sw - 8 * k - ctl_w
            self.btn_kind = ["prev", "play", "next", "menu"]
            self.r_time = (sx + sw - 102 * k, sy, 90 * k, sh)
        self.r_btn = [(bx + i * bw, sy + (sh - bw) / 2, bw, bw) for i in range(4)]
        self.r_ctl = (bx, sy, ctl_w, sh)
        self.bd_surface = None
        self.set_size_request(self.W, self.H)
        self.resize(self.W, self.H)
        self.measure_lines()
        self.place()
        self.update_input_shape()
        self.dirty = True

    def font(self, px, weight="Bold"):
        d = Pango.FontDescription.from_string(f"{FONT} {weight}")
        d.set_absolute_size(px * Pango.SCALE)
        return d

    def make_layout(self, text, px, weight="Bold", width=None, markup=False, ellipsize=False, align=None):
        lo = self.area.create_pango_layout("")
        lo.set_font_description(self.font(px, weight))
        if markup:
            lo.set_markup(text, -1)
        else:
            lo.set_text(text, -1)
        if width:
            lo.set_width(int(width * Pango.SCALE))
            lo.set_wrap(Pango.WrapMode.WORD_CHAR)
        if ellipsize:
            lo.set_ellipsize(Pango.EllipsizeMode.END)
        if align is not None:
            lo.set_auto_dir(False)
            lo.set_alignment(align)
        return lo

    def measure_lines(self):
        """Lay every line out word by word, with a start/end time for each word."""
        self.lays = []
        if not self.lyrics:
            return
        k = self.k
        em = 24 * k
        row_h = em * 1.24
        space = em * 0.28
        W = self.r_lyr[2]
        lines = self.lyrics["lines"]
        y = 0.0
        rtl_count = 0
        for i, l in enumerate(lines):
            rtl = is_rtl(l["x"])
            lay = {"y": y, "h": 34 * k, "a": 0.42, "s": 0.94, "rtl": rtl, "words": []}
            if not l["x"]:
                self.lays.append(lay)
                y += lay["h"] + 8 * k
                continue
            rtl_count += rtl
            texts = l["x"].split()
            end = lines[i + 1]["t"] if i + 1 < len(lines) else l["t"] + 4
            given = l.get("w") or []
            if len(given) == len(texts):
                times = [w[0] for w in given] + [min(end, given[-1][0] + 1.2)]
            else:
                chars = sum(len(t) + 1 for t in texts)
                d = min((end - l["t"]) * 0.9, max(1.0, chars * 0.085))
                times, acc = [], 0
                for t in texts:
                    times.append(l["t"] + d * acc / chars)
                    acc += len(t) + 1
                times.append(l["t"] + d)
            words = []
            for j, t in enumerate(texts):
                lo = self.make_layout(t, em)
                ext = lo.get_pixel_extents()[1]
                words.append({"lo": lo, "w": ext.width, "x": 0.0, "y": 0.0, "rtl": is_rtl(t),
                              "t0": times[j], "t1": times[j + 1]})
            # visual order: runs written against the line direction are reversed
            order = list(range(len(words)))
            j = 0
            while j < len(words):
                if words[j]["rtl"] == rtl:
                    j += 1
                    continue
                e = j
                while e < len(words) and words[e]["rtl"] != rtl:
                    e += 1
                order[j:e] = order[j:e][::-1]
                j = e
            row, cursor = 0, 0.0
            for j in order:
                w = words[j]
                if cursor > 0 and cursor + w["w"] > W:
                    row, cursor = row + 1, 0.0
                w["x"] = W - cursor - w["w"] if rtl else cursor
                w["y"] = row * row_h
                cursor += w["w"] + space
            lay["words"] = words
            lay["h"] = (row + 1) * row_h - em * 0.12
            self.lays.append(lay)
            y += lay["h"] + 12 * k
        self.lyr_rtl = rtl_count * 2 > len(lines)
        self.scroll_ok = False

    def monitor_geometry(self):
        disp = Gdk.Display.get_default()
        mon = None
        win = self.get_window()
        if win is not None:
            mon = disp.get_monitor_at_window(win)
        if mon is None:
            mon = disp.get_primary_monitor() or disp.get_monitor(0)
        return mon.get_workarea() if LAYER is None else mon.get_geometry()

    def place(self):
        gap = 14 - self.m
        c = self.cfg["corner"]
        if LAYER is not None:
            E = LAYER.Edge
            for e in (E.TOP, E.BOTTOM, E.LEFT, E.RIGHT):
                LAYER.set_anchor(self, e, False)
                LAYER.set_margin(self, e, 0)
            mx = self.cfg["mx"] if self.cfg["mx"] is not None else gap
            my = self.cfg["my"] if self.cfg["my"] is not None else gap
            LAYER.set_anchor(self, E.BOTTOM if c in ("BR", "BL") else E.TOP, True)
            LAYER.set_anchor(self, E.RIGHT if c in ("BR", "TR") else E.LEFT, True)
            LAYER.set_margin(self, E.BOTTOM if c in ("BR", "BL") else E.TOP, int(my))
            LAYER.set_margin(self, E.RIGHT if c in ("BR", "TR") else E.LEFT, int(mx))
        else:
            wa = self.monitor_geometry()
            if c == "custom" and self.cfg["x"] is not None:
                x, y = self.cfg["x"], self.cfg["y"]
            else:
                x = wa.x + wa.width - self.W - gap if c in ("BR", "TR") else wa.x + gap
                y = wa.y + wa.height - self.H - gap if c in ("BR", "BL") else wa.y + gap
            self.move(int(x), int(y))

    def update_input_shape(self):
        win = self.get_window()
        if win is None:
            return
        x, y, w, h = self.card
        self.input_shape_combine_region(cairo.Region(cairo.RectangleInt(int(x), int(y), int(w), int(h))))

    def on_configure(self, *_):
        if LAYER is None and self.drag == "x11":
            x, y = self.get_position()
            self.cfg["x"], self.cfg["y"], self.cfg["corner"] = x, y, "custom"
            if getattr(self, "_x11_timer", None):
                GLib.source_remove(self._x11_timer)
            self._x11_timer = GLib.timeout_add(700, self.x11_drag_end)
        return False

    # -------------------------------------------------------------- state

    def set_status(self, s):
        self.status = s
        self.status_at = time.monotonic()
        self.dirty = True

    def on_track(self, now):
        p = self.player
        self.key = f"{p.artist}|{p.title}"
        self.key_at = now
        self.fetch_key = None
        self.lyrics = None
        self.lays = []
        self.cur = -1
        mirror = is_rtl(p.title)
        if mirror != self.mirror:
            self.mirror = mirror
            self.layout()
        self.set_status(ST_SEARCH if p.artist.strip() and p.title.strip() else ST_NONE)

    def maybe_fetch(self, now):
        if self.status == ST_ERROR and now > self.retry_at:
            self.set_status(ST_SEARCH)
            self.fetch_key = None
        if self.status != ST_SEARCH or self.fetch_key == self.key:
            return
        p = self.player
        if p.length <= 0 and now - self.key_at < 1.2:
            return
        self.fetch_key = key = self.key
        artist, title, dur = p.artist, p.title, p.length

        def work():
            try:
                res, err = fetch_lyrics(artist, title, dur), None
            except OSError as e:
                res, err = None, e
            GLib.idle_add(self.got_lyrics, key, res, err)

        threading.Thread(target=work, daemon=True).start()

    def got_lyrics(self, key, res, err):
        if key != self.key:
            return False
        if err is not None:
            self.set_status(ST_ERROR)
            self.retry_at = time.monotonic() + 15
        elif res is None:
            self.set_status(ST_NOTFOUND)
        elif res.get("instrumental") or not res["lines"]:
            self.set_status(ST_INSTR)
        else:
            self.lyrics = res
            self.measure_lines()
            self.set_status(ST_OK)
        return False

    def load_art(self, url):
        self.art_url = url
        self.art = None
        self.accent_target = DEFAULT_ACCENT
        if not url:
            return
        if url in self.art_cache:
            self.got_art(self.key, url, self.art_cache[url])
            return
        key = self.key

        def work():
            data = None
            try:
                if url.startswith("file://"):
                    with open(urllib.parse.unquote(url[7:]), "rb") as f:
                        data = f.read()
                else:
                    req = urllib.request.Request(url, headers={"User-Agent": "Shura/1.0"})
                    with urllib.request.urlopen(req, timeout=10) as r:
                        data = r.read()
            except OSError:
                pass
            if data:
                GLib.idle_add(self.got_art, key, url, data)

        threading.Thread(target=work, daemon=True).start()

    def got_art(self, key, url, data):
        if url != self.art_url:
            return False
        try:
            loader = GdkPixbuf.PixbufLoader()
            loader.write(data)
            loader.close()
            pb = loader.get_pixbuf()
        except GLib.Error:
            return False
        if pb is None:
            return False
        self.art_cache[url] = data
        if len(self.art_cache) > 30:
            self.art_cache.pop(next(iter(self.art_cache)))
        self.accent_target = accent_from_pixbuf(pb)
        try:
            self.prev_bd, self.bd, self.bd_fade = self.bd, Backdrop(pb), 0.0
        except (GLib.Error, ValueError):
            pass
        sf = self.get_scale_factor() or 1
        size = max(1, int(22 * self.k * sf))
        self.art = (pb.scale_simple(size, size, GdkPixbuf.InterpType.BILINEAR), sf)
        self.dirty = True
        return False

    def current_index(self, pos):
        lines = self.lyrics["lines"]
        if self.lyrics["synced"]:
            t = pos + self.cfg["offset_ms"] / 1000 + 0.15
            self.cur_t = t
            idx = -1
            for i, l in enumerate(lines):
                if l["t"] <= t:
                    idx = i
                else:
                    break
            return idx
        dur = self.player.length
        return min(len(lines) - 1, max(0, int(pos / dur * len(lines)))) if dur > 0 else 0

    def want_shown(self, now):
        p = self.player
        if self.cfg["hidden"] or not p.ok or self.status == ST_NONE:
            return False
        if self.hover or p.playing or self.cfg["stay_paused"]:
            return True
        return now - self.last_playing < 8

    # -------------------------------------------------------------- frame loop

    def tick(self):
        now = time.monotonic()
        dt = now - self.last_tick
        if dt <= 0 or dt > 0.1:
            dt = 0.016
        self.last_tick = now
        p = self.player
        if now - self.last_poll > 0.5:
            self.last_poll = now
            p.poll()
        if p.ok and f"{p.artist}|{p.title}" != self.key:
            self.on_track(now)
        if p.ok and p.art_url != self.art_url:
            self.load_art(p.art_url)
        self.maybe_fetch(now)
        if p.playing:
            self.last_playing = now

        want = self.want_shown(now)
        if want and not self.shown:
            self.shown = True
            self.vis_a = 0.0
            self.show_all()
            self.place()
            self.update_input_shape()
        if not self.shown:
            return True

        anim = False

        def step(cur, target, speed):
            nonlocal anim
            d = target - cur
            if abs(d) > 0.002:
                anim = True
                return cur + d * ease(dt, speed)
            return target

        self.vis_a = step(self.vis_a, 1.0 if want else 0.0, 9)
        if not want and self.vis_a < 0.02:
            self.shown = False
            self.hide()
            return True
        op = self.cfg["idle_opacity"]
        if self.status == ST_NOTFOUND and now - self.status_at > 6:
            op *= 0.55
        if self.hover:
            op = 1.0
        self.op_a = step(self.op_a, op, 8)
        self.ctrl_a = step(self.ctrl_a, 1.0 if self.hover else 0.0, 12)
        if sum(abs(self.accent[i] - self.accent_target[i]) for i in range(3)) > 0.004:
            self.accent = mixc(self.accent, self.accent_target, ease(dt, 4))
            anim = True
        else:
            self.accent = self.accent_target

        if self.bd_fade < 1:
            self.bd_fade = min(1.0, self.bd_fade + dt / 1.2)
            if self.bd_fade >= 1:
                self.prev_bd = None
        if self.status == ST_OK and self.lays:
            idx = self.current_index(p.pos())
            self.cur = idx
            anchor = self.r_lyr[3] * 0.34
            if idx < 0:
                target = self.lays[0]["y"] - anchor
            else:
                target = self.lays[idx]["y"] + self.lays[idx]["h"] / 2 - anchor
            if not self.scroll_ok:
                self.scroll, self.scroll_ok = target, True
            self.scroll = step(self.scroll, target, 6)
            for i, lay in enumerate(self.lays):
                t, sc = (0.30 if i < idx else 0.42), 0.94
                if i == idx:
                    t, sc = 1.0, 1.0
                if self.hover_line == i and i != idx:
                    t = 0.75
                lay["a"] = step(lay["a"], t, 9)
                lay["s"] = step(lay["s"], sc, 7)
            if p.playing and idx >= 0:
                anim = True  # the word sweep moves every frame
        if self.status == ST_SEARCH or now < self.toast_until:
            anim = True

        gap = 0.016 if self.hover else 0.033  # 30 fps is plenty and keeps the CPU quiet
        if (self.dirty or anim or now - self.last_draw > 0.066) and now - self.last_draw >= gap:
            self.dirty = False
            self.last_draw = now
            self.area.queue_draw()
        return True

    # -------------------------------------------------------------- painting

    def update_backdrop(self, now):
        x, y, w, h = self.card
        bw, bh = int(w / 2) + 2, int(h / 2) + 2
        if self.bd_surface is None or self.bd_surface.get_width() != bw or self.bd_surface.get_height() != bh:
            self.bd_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, bw, bh)
        cr = cairo.Context(self.bd_surface)
        t = now - self.started
        if self.prev_bd is not None and self.bd_fade < 1:
            self.prev_bd.paint(cr, bw, bh, t)
            cr.push_group()
            self.bd.paint(cr, bw, bh, t)
            cr.pop_group_to_source()
            cr.paint_with_alpha(self.bd_fade)
        else:
            self.bd.paint(cr, bw, bh, t)
        g = cairo.LinearGradient(0, 0, 0, bh)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.22)
        cr.set_source(g)
        cr.paint()
        self.last_bd = now

    def on_draw(self, widget, cr):
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        alpha = max(0.0, min(1.0, self.vis_a * self.op_a))
        if alpha <= 0.003:
            return True
        now = time.monotonic()
        if self.bd_surface is None or now - self.last_bd > 0.066:
            self.update_backdrop(now)
        cr.push_group()
        self.paint(cr)
        cr.pop_group_to_source()
        cr.paint_with_alpha(alpha)
        return True

    def paint(self, cr):
        k = self.k
        x, y, w, h = self.card
        rad = 12 * k
        for i in range(self.m, 0, -1):
            rrect(cr, x - i * 0.8, y - i * 0.5 + 3 * k, w + i * 1.6, h + i * 1.1, rad + i)
            cr.set_source_rgba(0, 0, 0, 0.02)
            cr.fill()
        rrect(cr, x - 1, y - 1, w + 2, h + 2, rad + 1)
        cr.set_source_rgba(0, 0, 0, 0.35)
        cr.fill()

        cr.save()
        rrect(cr, x, y, w, h, rad)
        cr.clip()
        cr.translate(x - 2 * k, y - 2 * k)
        cr.scale(2, 2)
        cr.set_source_surface(self.bd_surface, 0, 0)
        cr.get_source().set_filter(cairo.FILTER_BILINEAR)
        cr.paint()
        cr.restore()

        self.paint_lyrics(cr)
        cr.save()
        rrect(cr, x, y, w, h, rad)
        cr.clip()
        self.paint_strip(cr)
        self.paint_progress(cr)
        self.paint_toast(cr)
        cr.restore()
        rrect(cr, x + 0.5, y + 0.5, w - 1, h - 1, rad)
        cr.set_source_rgba(1, 1, 1, 0.09)
        cr.set_line_width(1)
        cr.stroke()

    def paint_interlude(self, cr, ox, mid, rtl, active, frac, remain, al):
        k = self.k
        scale = 1.0
        if active:
            scale = 1 + 0.06 * math.sin(time.monotonic() * 2.6)
            if remain < 0.45:
                scale *= max(0.0, remain / 0.45)
        for j in range(3):
            dx = j * 17 * k + 6 * k
            px = ox - dx if rtl else ox + dx
            b = 0.28 + 0.72 * max(0.0, min(1.0, frac * 3 - j)) if active else 0.28
            r = 5.5 * k * scale
            if active and b > 0.3:
                cr.set_source_rgba(1, 1, 1, 0.07 * b * al)
                cr.arc(px, mid, r * 1.9, 0, 2 * math.pi)
                cr.fill()
            cr.set_source_rgba(1, 1, 1, b * al)
            cr.arc(px, mid, max(0.1, r), 0, 2 * math.pi)
            cr.fill()

    def paint_lyrics(self, cr):
        k = self.k
        rx, ry, rw, rh = self.r_lyr
        cx, cy, cw, _ = self.card
        top, bottom = cy + 2 * k, ry + rh
        self.line_hits = []
        cr.save()
        cr.rectangle(cx, top, cw, bottom - top)
        cr.clip()
        msg = {ST_SEARCH: "מחפש מילים" + "." * int(time.monotonic() / 0.4 % 4), ST_NOTFOUND: "אין מילים לשיר הזה",
               ST_ERROR: "אין חיבור לאינטרנט", ST_INSTR: "קטע אינסטרומנטלי"}.get(self.status)
        if msg:
            lo = self.make_layout(msg, 22 * k, width=rw)
            cr.move_to(rx, ry + 36 * k)
            cr.set_source_rgba(1, 1, 1, 0.6)
            PangoCairo.show_layout(cr, lo)
            cr.restore()
            return
        if self.status != ST_OK or not self.lyrics:
            cr.restore()
            return
        lines = self.lyrics["lines"]
        t = self.cur_t
        feather = 7 * k
        karaoke_on = self.cfg["karaoke"] and self.lyrics["synced"]
        for i, lay in enumerate(self.lays):
            yy = ry + lay["y"] - self.scroll
            lh = lay["h"]
            if yy > bottom + 10 * k or yy + lh < top - 10 * k:
                continue
            mid = yy + lh / 2
            f = max(0.0, min(1.0, min((mid - top) / (26 * k), (bottom - mid) / (30 * k))))
            f = f * f * (3 - 2 * f)
            if f < 0.01:
                continue
            active = i == self.cur
            rtl_side = lay["rtl"] or (not lay["words"] and self.lyr_rtl)
            ox = rx + rw if rtl_side else rx
            cr.save()
            cr.translate(ox, mid)
            cr.scale(lay["s"], lay["s"])
            cr.translate(-ox, -mid)
            if not lay["words"]:
                frac, remain = 0.0, 10.0
                if active and i + 1 < len(lines):
                    span = lines[i + 1]["t"] - lines[i]["t"]
                    if span > 0:
                        frac = max(0.0, min(1.0, (t - lines[i]["t"]) / span))
                        remain = lines[i + 1]["t"] - t
                self.paint_interlude(cr, ox, mid, rtl_side, active, frac, remain, f * min(1.0, lay["a"] * 2))
            else:
                karaoke = active and karaoke_on
                for w in lay["words"]:
                    frac = 0.0
                    if karaoke:
                        if w["t1"] > w["t0"]:
                            frac = max(0.0, min(1.0, (t - w["t0"]) / (w["t1"] - w["t0"])))
                        elif t >= w["t0"]:
                            frac = 1.0
                    wx = rx + w["x"]
                    wy = yy + w["y"] - (2 * k * ease_out(frac) if karaoke else 0)
                    if not karaoke:
                        cr.set_source_rgba(1, 1, 1, f * lay["a"])
                        cr.move_to(wx, wy)
                        PangoCairo.show_layout(cr, w["lo"])
                        continue
                    on, off = (1, 1, 1, f * lay["a"]), (1, 1, 1, f * 0.36)
                    glow = 1.0 if 0 < frac < 1 else (max(0.0, 1 - (t - w["t1"]) / 0.7) if frac >= 1 else 0.0)
                    cr.new_path()
                    cr.move_to(wx, wy)
                    PangoCairo.layout_path(cr, w["lo"])
                    x0, x1 = wx, wx + w["w"]
                    if glow > 0.02:
                        cr.set_line_join(cairo.LINE_JOIN_ROUND)
                        for width, ga in ((7 * k, 0.07), (3.5 * k, 0.11)):
                            cr.set_source(sweep(x0, x1, frac, feather, w["rtl"], (1, 1, 1, ga * glow * f), (1, 1, 1, 0)))
                            cr.set_line_width(width)
                            cr.stroke_preserve()
                    if frac <= 0:
                        cr.set_source_rgba(*off)
                    elif frac >= 1:
                        cr.set_source_rgba(*on)
                    else:
                        cr.set_source(sweep(x0, x1, frac, feather, w["rtl"], on, off))
                    cr.fill()
            cr.restore()
            self.line_hits.append((i, (rx - 8 * k, yy - 4 * k, rw + 16 * k, lh + 8 * k)))
        cr.restore()

    def paint_strip(self, cr):
        k = self.k
        sx, sy, sw, sh = self.r_strip
        A = 1.0
        if self.compact():
            A = self.ctrl_a
            if A < 0.01:
                return
        g = cairo.LinearGradient(0, sy - 11 * k, 0, sy + 6 * k)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.32 * A)
        cr.set_source(g)
        cr.rectangle(sx, sy - 10 * k, sw, 16 * k)
        cr.fill()
        cr.set_source_rgba(0, 0, 0, 0.32 * A)
        cr.rectangle(sx, sy + 6 * k, sw, sh - 6 * k)
        cr.fill()
        ax, ay, aw, ah = self.r_art
        if self.art:
            pb, sf = self.art
            cr.save()
            rrect(cr, ax, ay, aw, ah, 4 * k)
            cr.clip()
            cr.translate(ax, ay)
            cr.scale(aw / pb.get_width(), ah / pb.get_height())
            Gdk.cairo_set_source_pixbuf(cr, pb, 0, 0)
            cr.paint_with_alpha(A)
            cr.restore()
        else:
            rrect(cr, ax, ay, aw, ah, 4 * k)
            cr.set_source_rgba(1, 1, 1, 0.16 * A)
            cr.fill()

        p = self.player
        tx, _, tw, _ = self.r_time
        bx, _, bw, _ = self.r_ctl
        sh2 = sh - 2 * k
        if self.mirror:
            left, right = max(tx + tw, bx + bw) + 10 * k, ax - 10 * k
        else:
            left, right = ax + aw + 10 * k, min(tx, bx) - 10 * k
        artist = p.artist
        if self.status == ST_OK and self.lyrics and not self.lyrics["synced"]:
            artist += " · לא מסונכרן"
        mk = f"<span weight='600'>{esc(p.title)}</span><span fgalpha='68%' weight='normal'>  ·  {esc(artist)}</span>"
        lo = self.make_layout(mk, 13 * k, weight="Normal", width=right - left, markup=True, ellipsize=True)
        th = lo.get_pixel_extents()[1].height
        cr.set_source_rgba(1, 1, 1, 0.97 * A)
        cr.move_to(left, sy + (sh2 - th) / 2)
        PangoCairo.show_layout(cr, lo)

        ta = (1 - self.ctrl_a) * A
        if ta > 0.01 and p.length > 0:
            lo = self.make_layout(f"{fmt_time(p.pos())} / {fmt_time(p.length)}", 11.5 * k, weight="Normal", width=tw,
                                  align=Pango.Alignment.LEFT if self.mirror else Pango.Alignment.RIGHT)
            h2 = lo.get_pixel_extents()[1].height
            cr.set_source_rgba(1, 1, 1, 0.62 * ta)
            cr.move_to(tx, sy + (sh2 - h2) / 2)
            PangoCairo.show_layout(cr, lo)
        if self.ctrl_a > 0.01:
            self.paint_controls(cr, self.ctrl_a * A)

    def paint_controls(self, cr, A):
        k = self.k
        for i, kind in enumerate(self.btn_kind):
            bx, by, bw, bh = self.r_btn[i]
            cx, cy = bx + bw / 2, by + bh / 2
            if self.hover_btn == i:
                rrect(cr, bx + 2 * k, by + 2 * k, bw - 4 * k, bh - 4 * k, 5 * k)
                cr.set_source_rgba(1, 1, 1, 0.13 * A)
                cr.fill()
            cr.set_source_rgba(1, 1, 1, 0.92 * A)
            if kind == "play":
                if self.player.playing:
                    cr.rectangle(cx - 4.2 * k, cy - 5 * k, 3 * k, 10 * k)
                    cr.rectangle(cx + 1.2 * k, cy - 5 * k, 3 * k, 10 * k)
                else:
                    cr.move_to(cx - 3.5 * k, cy - 5.5 * k)
                    cr.line_to(cx - 3.5 * k, cy + 5.5 * k)
                    cr.line_to(cx + 5.5 * k, cy)
                    cr.close_path()
            elif kind == "next":
                cr.move_to(cx - 4.5 * k, cy - 4.5 * k)
                cr.line_to(cx - 4.5 * k, cy + 4.5 * k)
                cr.line_to(cx + 2.5 * k, cy)
                cr.close_path()
                cr.rectangle(cx + 2.5 * k, cy - 4.5 * k, 2 * k, 9 * k)
            elif kind == "prev":
                cr.move_to(cx + 4.5 * k, cy - 4.5 * k)
                cr.line_to(cx + 4.5 * k, cy + 4.5 * k)
                cr.line_to(cx - 2.5 * k, cy)
                cr.close_path()
                cr.rectangle(cx - 4.5 * k, cy - 4.5 * k, 2 * k, 9 * k)
            else:
                for j in (-1, 0, 1):
                    cr.new_sub_path()
                    cr.arc(cx + j * 4.5 * k, cy, 1.5 * k, 0, 2 * math.pi)
            cr.fill()

    def paint_progress(self, cr):
        p = self.player
        if p.length <= 0:
            return
        k = self.k
        x, y, w, h = self.card
        frac = max(0.0, min(1.0, p.pos() / p.length))
        bh = 4 * k if self.hover_prog else 2 * k
        cr.set_source_rgba(0, 0, 0, 0.26)
        cr.rectangle(x, y + h - bh, w, bh)
        cr.fill()
        cr.set_source_rgba(1, 1, 1, 0.88)
        cr.rectangle(x, y + h - bh, w * frac, bh)
        cr.fill()
        if self.hover_prog:
            t = max(0.0, min(1.0, (self.mx - x) / w)) * p.length
            lo = self.make_layout(fmt_time(t), 11.5 * k, weight="Normal")
            ext = lo.get_pixel_extents()[1]
            bw2, bh2 = ext.width + 10 * k, 18 * k
            bx = max(x + 4 * k, min(self.mx - bw2 / 2, x + w - 4 * k - bw2))
            by = y + h - bh - 24 * k
            rrect(cr, bx, by, bw2, bh2, 3 * k)
            cr.set_source_rgba(0.05, 0.05, 0.06, 0.82)
            cr.fill()
            cr.set_source_rgba(1, 1, 1, 0.95)
            cr.move_to(bx + 5 * k, by + (bh2 - ext.height) / 2)
            PangoCairo.show_layout(cr, lo)

    def paint_toast(self, cr):
        now = time.monotonic()
        if now >= self.toast_until or not self.toast:
            return
        k = self.k
        a = max(0.0, min(1.0, (self.toast_until - now) / 0.3))
        lo = self.make_layout(self.toast, 12 * k, weight="Semibold")
        ext = lo.get_pixel_extents()[1]
        w, h = ext.width + 18 * k, 24 * k
        x, y, cw, _ = self.card
        bx = x + cw - 8 * k - w if self.mirror else x + 8 * k
        rrect(cr, bx, y + 8 * k, w, h, 4 * k)
        cr.set_source_rgba(0.04, 0.04, 0.05, 0.78 * a)
        cr.fill()
        cr.set_source_rgba(1, 1, 1, a)
        cr.move_to(bx + 9 * k, y + 8 * k + (h - ext.height) / 2)
        PangoCairo.show_layout(cr, lo)

    def show_toast(self, s):
        self.toast, self.toast_until, self.dirty = s, time.monotonic() + 1.5, True

    # -------------------------------------------------------------- input

    @staticmethod
    def inside(r, x, y):
        return r[0] <= x < r[0] + r[2] and r[1] <= y < r[1] + r[3]

    def hit_test(self):
        self.hover_btn, self.hover_line, self.hover_prog = -1, -1, False
        if not self.hover:
            return
        k = self.k
        live = not self.cfg["compact"] or self.ctrl_a > 0.3
        if live:
            for i, b in enumerate(self.r_btn):
                if self.inside(b, self.mx, self.my):
                    self.hover_btn = i
                    return
        x, y, w, h = self.card
        if self.player.length > 0 and self.inside((x, y + h - 7 * k, w, 9 * k), self.mx, self.my):
            self.hover_prog = True
            return
        if live and self.inside(self.r_strip, self.mx, self.my):
            return
        if self.status == ST_OK and self.lyrics and self.lyrics["synced"] and self.my < self.r_lyr[1] + self.r_lyr[3]:
            for i, r in self.line_hits:
                if self.inside(r, self.mx, self.my) and self.lyrics["lines"][i]["x"]:
                    self.hover_line = i
                    return

    def set_cursor(self):
        win = self.area.get_window()
        if win is None:
            return
        name = "pointer" if (self.hover_btn >= 0 or self.hover_line >= 0 or self.hover_prog) else "default"
        if getattr(self, "_cursor_name", None) != name:
            self._cursor_name = name
            win.set_cursor(Gdk.Cursor.new_from_name(win.get_display(), name))

    def on_enter(self, w, ev):
        self.hover = True
        self.dirty = True
        return False

    def on_leave(self, w, ev):
        if ev.detail == Gdk.NotifyType.INFERIOR:
            return False
        if self.drag is None:
            self.hover = False
            self.hit_test()
            self.dirty = True
        return False

    def on_motion(self, w, ev):
        if self.drag == "layer":
            self.drag_layer(ev)
            return True
        if self.drag == "x11" and not ev.state & Gdk.ModifierType.BUTTON1_MASK:
            self.drag = None
            self.press = None
        self.hover = True
        self.mx, self.my = ev.x, ev.y
        if self.press and self.press[0] in ("line", "prog") and math.hypot(ev.x - self.press[2], ev.y - self.press[3]) > 6:
            self.begin_drag(ev)
            return True
        self.hit_test()
        self.set_cursor()
        self.dirty = True
        return True

    def on_press(self, w, ev):
        if ev.type != Gdk.EventType.BUTTON_PRESS:
            return True
        self.mx, self.my = ev.x, ev.y
        if ev.button == 3:
            self.show_menu(ev)
            return True
        if ev.button != 1:
            return True
        self.hit_test()
        if self.hover_btn >= 0:
            self.press = ("btn", self.hover_btn, ev.x, ev.y)
        elif self.hover_prog:
            self.press = ("prog", 0, ev.x, ev.y)
        elif self.hover_line >= 0:
            self.press = ("line", self.hover_line, ev.x, ev.y)
        else:
            self.press = ("bg", 0, ev.x, ev.y)
            self.begin_drag(ev)
        return True

    def on_release(self, w, ev):
        if self.drag == "layer":
            self.end_drag()
            self.press = None
            return True
        pr, self.press = self.press, None
        if not pr or ev.button != 1:
            return True
        self.mx, self.my = ev.x, ev.y
        self.hit_test()
        kind, idx = pr[0], pr[1]
        p = self.player
        if kind == "btn" and self.hover_btn == idx:
            b = self.btn_kind[idx]
            if b == "play":
                p.toggle()
            elif b == "next":
                p.call("Next")
            elif b == "prev":
                p.call("Previous")
            else:
                self.show_menu(ev)
        elif kind == "prog" and p.length > 0:
            x, _, w, _ = self.card
            p.seek(max(0.0, min(1.0, (ev.x - x) / w)) * p.length)
        elif kind == "line" and self.lyrics and self.hover_line == idx:
            p.seek(self.lyrics["lines"][idx]["t"] - self.cfg["offset_ms"] / 1000 + 0.02)
        self.dirty = True
        return True

    def on_scroll(self, w, ev):
        if self.status != ST_OK or not self.lyrics or not self.lyrics["synced"]:
            return True
        dy = 0
        if ev.direction == Gdk.ScrollDirection.UP:
            dy = -1
        elif ev.direction == Gdk.ScrollDirection.DOWN:
            dy = 1
        elif ev.direction == Gdk.ScrollDirection.SMOOTH:
            ok, _, d = ev.get_scroll_deltas()
            if not ok or abs(d) < 0.5:
                return True
            dy = 1 if d > 0 else -1
        if dy:
            self.cfg["offset_ms"] += 100 if dy < 0 else -100
            self.cfg.save()
            off = self.cfg["offset_ms"] / 1000
            self.show_toast("סנכרון: 0.0 שנ׳" if off == 0 else f"סנכרון: {off:+.1f} שנ׳")
        return True

    # dragging: layer-shell windows move by changing their margins
    def begin_drag(self, ev):
        if LAYER is not None:
            self.drag = "layer"
            self.drag_anchor = (ev.x, ev.y)
            self.drag_applied = 0.0
            if self.cfg["mx"] is None:
                self.cfg["mx"] = self.cfg["my"] = 14 - self.m
        else:
            self.drag = "x11"
            self.begin_move_drag(1, int(ev.x_root), int(ev.y_root), ev.time)

    def drag_layer(self, ev):
        # pointer coords are window-relative; the window follows the pointer one frame later
        now = time.monotonic()
        if now - self.drag_applied < 0.03:
            return
        dx, dy = ev.x - self.drag_anchor[0], ev.y - self.drag_anchor[1]
        if abs(dx) < 1 and abs(dy) < 1:
            return
        self.drag_applied = now
        c = self.cfg["corner"]
        geo = self.monitor_geometry()
        mx = self.cfg["mx"] + (-dx if c in ("BR", "TR") else dx)
        my = self.cfg["my"] + (-dy if c in ("BR", "BL") else dy)
        self.cfg["mx"] = max(-self.m, min(mx, geo.width - self.W + self.m))
        self.cfg["my"] = max(-self.m, min(my, geo.height - self.H + self.m))
        self.place()

    def x11_drag_end(self):
        self._x11_timer = None
        if self.drag == "x11":
            self.drag = None
            self.press = None
            self.cfg.save()
        return False

    def end_drag(self):
        kind, self.drag = self.drag, None
        if kind == "layer":
            geo = self.monitor_geometry()
            c = self.cfg["corner"]
            # window position measured from the top-left
            x = geo.width - self.W - self.cfg["mx"] if c in ("BR", "TR") else self.cfg["mx"]
            y = geo.height - self.H - self.cfg["my"] if c in ("BR", "BL") else self.cfg["my"]
            right = x + self.W / 2 > geo.width / 2
            bottom = y + self.H / 2 > geo.height / 2
            nc = ("B" if bottom else "T") + ("R" if right else "L")
            mx = geo.width - self.W - x if right else x
            my = geo.height - self.H - y if bottom else y
            snap = 56
            gap = 14 - self.m
            if mx - gap < snap:
                mx = gap
            if my - gap < snap:
                my = gap
            self.cfg["corner"], self.cfg["mx"], self.cfg["my"] = nc, mx, my
            self.place()
        self.cfg.save()

    # -------------------------------------------------------------- menu

    def show_menu(self, ev):
        menu = Gtk.Menu()
        menu.set_direction(Gtk.TextDirection.RTL)

        def item(label, cb=None, check=None, sub=None, sensitive=True):
            if check is None:
                it = Gtk.MenuItem(label=label)
            else:
                it = Gtk.CheckMenuItem(label=label)
                it.set_active(check)
                it.set_draw_as_radio(False)
            it.set_sensitive(sensitive)
            if sub is not None:
                it.set_submenu(sub)
            elif cb is not None:
                it.connect("activate", lambda *_: cb())
            return it

        def radio_menu(options, current, setter):
            m = Gtk.Menu()
            m.set_direction(Gtk.TextDirection.RTL)
            for value, label in options:
                it = Gtk.CheckMenuItem(label=label)
                it.set_draw_as_radio(True)
                it.set_active(value == current)
                it.connect("activate", lambda _w, v=value: setter(v))
                m.append(it)
            return m

        def set_corner(v):
            self.cfg.update(corner=v, mx=None, my=None, x=None, y=None)
            self.place()
            self.cfg.save()

        def set_size(v):
            self.cfg["size"] = v
            self.cfg.save()
            self.layout()

        def set_op(v):
            self.cfg["idle_opacity"] = v
            self.cfg.save()

        def sync(delta):
            self.cfg["offset_ms"] = 0 if delta is None else self.cfg["offset_ms"] + delta
            self.cfg.save()
            off = self.cfg["offset_ms"] / 1000
            self.show_toast("סנכרון: 0.0 שנ׳" if off == 0 else f"סנכרון: {off:+.1f} שנ׳")

        def toggle(key, relayout=False):
            self.cfg[key] = not self.cfg[key]
            self.cfg.save()
            if relayout:
                self.layout()
            self.dirty = True

        sync_menu = Gtk.Menu()
        sync_menu.set_direction(Gtk.TextDirection.RTL)
        off = self.cfg["offset_ms"] / 1000
        sync_menu.append(item(f"סנכרון: {off:+.1f} שנ׳" if off else "סנכרון: 0.0 שנ׳", sensitive=False))
        sync_menu.append(Gtk.SeparatorMenuItem())
        sync_menu.append(item("מוקדם יותר", lambda: sync(250)))
        sync_menu.append(item("מאוחר יותר", lambda: sync(-250)))
        sync_menu.append(item("איפוס", lambda: sync(None)))

        menu.append(item("מיקום", sub=radio_menu(
            [("BR", "ימין למטה"), ("BL", "שמאל למטה"), ("TR", "ימין למעלה"), ("TL", "שמאל למעלה")],
            self.cfg["corner"], set_corner)))
        menu.append(item("גודל", sub=radio_menu([("S", "קטן"), ("M", "רגיל"), ("L", "גדול")], self.cfg["size"], set_size)))
        menu.append(item("שקיפות", sub=radio_menu([(v, f"{int(v * 100)}%") for v in (1.0, 0.9, 0.75, 0.6, 0.45)],
                                                  min((1.0, 0.9, 0.75, 0.6, 0.45), key=lambda v: abs(v - self.cfg["idle_opacity"])),
                                                  set_op)))
        menu.append(item("סנכרון", sub=sync_menu))
        menu.append(Gtk.SeparatorMenuItem())
        def toggle_over():
            toggle("over_fullscreen")
            if LAYER is not None:
                LAYER.set_layer(self, LAYER.Layer.OVERLAY if self.cfg["over_fullscreen"] else LAYER.Layer.TOP)

        menu.append(item("מילה אחר מילה", lambda: toggle("karaoke"), check=self.cfg["karaoke"]))
        menu.append(item("קומפקטי", lambda: toggle("compact", True), check=self.cfg["compact"]))
        menu.append(item("מעל משחקים ומסך מלא", toggle_over, check=self.cfg["over_fullscreen"]))
        menu.append(item("להשאיר מוצג בהשהיה", lambda: toggle("stay_paused"), check=self.cfg["stay_paused"]))
        menu.append(item("הפעלה עם ההתחברות", self.toggle_autostart, check=os.path.exists(autostart_path())))
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(item("הסתרה (מפעילים שוב כדי להחזיר)", lambda: self.set_hidden(True)))
        menu.append(item("יציאה", self.app.quit))
        menu.show_all()
        menu.attach_to_widget(self.area, None)
        menu.connect("deactivate", lambda *_: self.on_menu_closed())
        menu.popup_at_pointer(ev)

    def on_menu_closed(self):
        self.hover = False
        self.hit_test()
        self.dirty = True

    def set_hidden(self, v):
        self.cfg["hidden"] = v
        self.cfg.save()
        self.dirty = True

    def toggle_autostart(self):
        p = autostart_path()
        if os.path.exists(p):
            os.remove(p)
        else:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            installed = os.path.join(HOME, ".local", "bin", "shura")
            target = installed if os.path.exists(installed) else os.path.abspath(__file__)
            with open(p, "w") as f:
                f.write(desktop_entry(target))


def autostart_path():
    return os.path.join(HOME, ".config", "autostart", "shura.desktop")


# ------------------------------------------------------------------ app

class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.win = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.hold()

    def do_activate(self):
        if self.win is None:
            self.win = Overlay(self)
        else:
            # launched again: bring it back if it was hidden
            self.win.set_hidden(False)
            if not self.win.player.ok:
                n = Gio.Notification.new("Shura")
                n.set_body("פועל ומחכה לספוטיפיי.")
                self.send_notification("waiting", n)


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)
    app = App()
    try:
        app.run([sys.argv[0]])
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
