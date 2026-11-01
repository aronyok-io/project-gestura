# Controls

| Mode | Gesture | Action |
|---|---|---|
| Mouse | Pointing index | Move pointer with smoothing |
| Mouse | Thumb/index pinch | Click once; release before another click |
| Mouse | Victory | Scroll using vertical hand movement; cursor stays in place |
| Mouse | Fist / open palm | Pause / resume cursor control |
| Media | Thumb up/down | Volume +/-5% once per gesture |
| Media | Fist / open palm | Mute / unmute |

A held volume gesture acts once. Relax the hand before repeating it.
Pinch freezes movement to keep clicks on target. Missing hands immediately clear pending actions.
Start/stop and enable are explicit GUI controls. Fist/palm pause/resume in Mouse mode and retain mute/unmute in Media mode.
Esc is local to the application window, not a global hotkey. Windows PyAutoGUI corner fail-safe remains enabled and stops the worker on exception.
