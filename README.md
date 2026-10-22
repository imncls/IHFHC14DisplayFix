# HC14 Display Fix

A small Windows tool that makes **IHF Handball Challenge 14** start in fullscreen at your screen's resolution. Use it if the game opens:
- in a small window with black bars,
- in a window bigger than your screen, cut off at the edges,
- or spilling onto your second monitor.

## Download and use
Download `HC14DisplayFix-<version>.exe` from the repository's Releases page.

1. Start the game at least once and close it. The game creates its settings file the first time it runs.
2. With the game closed, run `HC14DisplayFix.exe`. It shows your main monitor, the game's current settings and the new ones, and asks before changing anything. If Windows shows "Windows protected your PC", see [below](#windows-protected-your-pc).
3. Type `y` and press Enter. Start the game: it opens fullscreen.

The first time it changes the settings, it keeps a copy of the original next to them (`game.cfg.displayfix.bak`). To put it back, run it from a command prompt with `--restore`:

```
HC14DisplayFix.exe --restore
```

Other options: `--yes` changes the settings without asking; `--help` lists them all.

The game always uses the monitor Windows marks as main. To play on another monitor, make it the main one (Windows Settings ▸ System ▸ Display ▸ "Make this my main display") and run the tool again.

### "Windows protected your PC"
The `.exe` is not code-signed, so Windows SmartScreen shows this warning for it, as it does for any new unsigned program. Click **More info** ▸ **Run anyway**.

You can first check that your download is the published one. Each release lists the SHA-256 checksum of the `.exe` and includes it as `SHA256SUMS.txt`. In a command prompt, in the folder with the download, run:

```
certutil -hashfile HC14DisplayFix-<version>.exe SHA256
```

If the result does not match the release's checksum, delete the file and do not run it.

## What goes wrong, and what the tool changes
The game keeps its display settings in `Documents\neutron games\HandballChallenge14\game.cfg`. Two things make it open in the wrong size:

- **`RefreshRate` at 0.** With 0, the game cannot switch to fullscreen and falls back to a 1024x768 window.
- **Windows display scaling.** The game predates display scaling. If your screen is set above 100% (Settings ▸ Display ▸ Scale), Windows enlarges the game's window by that amount: at 125%, a 1920x1080 window becomes 2400x1350, wider than the screen. Fullscreen is not affected.

The tool sets three values in that file and leaves everything else as it is:

| Setting | Set to |
|---|---|
| `Fullscreen` | `1` |
| `Resolution` | your main monitor's resolution, as the game numbers it |
| `RefreshRate` | your main monitor's current refresh rate (60 if Windows reports none) |

`Resolution` is a position in the game's list of resolutions: every resolution the main monitor offers from 800 pixels wide, smallest first, counting from 0. On a typical 1920x1080 screen it is `15`. The tool reads the list the same way the game does (Direct3D 9).

It changes nothing else: no game files, no registry, no Windows settings. It needs no installation and no internet.

## Doing it by hand
1. Close the game and open `Documents\neutron games\HandballChallenge14\game.cfg` with Notepad.
2. In the `<Graphics>` section, set `<Fullscreen>1</Fullscreen>` and `<RefreshRate>60</RefreshRate>` (or another rate your main monitor supports, such as 75, 120 or 144; anything but 0).
3. Set `<Resolution>` to your screen's resolution in the game's list (see above): `15` on a typical 1920x1080 screen. If the size is wrong, try one number up or down.
4. Save and start the game.

If you change the resolution in the game's options menu and fullscreen stops working, check whether `RefreshRate` went back to 0.

## How it was made
This tool was developed with the help of AI coding assistants. Every change was tested, including in the game itself, and the code of each release was reviewed by hand before it was published.

## Legal notice
- This is an unofficial, fan-made tool. It is not affiliated with, endorsed by or connected to Bigben Interactive, Neutron Games or the IHF. "IHF Handball Challenge 14" and its names belong to their owners and are used here only to say which game the tool works with.
- The repository and the program contain no part of the game. The tool only edits the settings file the game keeps in your Documents folder.
- Use it at your own risk. It keeps a copy of your original settings, which `--restore` puts back.
- The code is licensed under the [MIT License](LICENSE).

## Contributing
The code is open: fork it and change it as you like (MIT License). To run it from the source, run the tests or build the `.exe`, see [CONTRIBUTING.md](CONTRIBUTING.md).
