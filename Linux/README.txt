Shura (Linux)
=============
Spotify lyrics in a corner of the screen. Tested target: CachyOS / Arch, KDE Plasma (Wayland).
Also works on other wlroots/Hyprland/Sway setups, and on X11.

1. Packages (once):
     sudo pacman -S --needed python-gobject python-cairo gtk3 gtk-layer-shell

2. Run it:
     python3 shura.py

3. Optional - add it to the app menu:
     python3 shura.py --install        (remove with --uninstall)

Hover for controls, click a line to jump to it, scroll to fix the sync,
drag to move, right-click for settings. Running it again brings it back if hidden.
Works with the official Spotify app (also the Flatpak) through MPRIS.
