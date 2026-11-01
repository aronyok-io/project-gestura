# Windows acceptance test

automated logic tests do not replace them.

- Install into a fresh Python virtual environment using requirements.txt.
- Verify the included model is present in models/, then launch from a different working directory as well.
- Start tracking: preview and landmarks appear; desktop controls remain disabled.
- Enable Mouse mode. Point to move, including edges, with no initial jump to the top-left.
- Hold a pinch for 2 seconds: exactly one click. Release and pinch again: one more click.
- Begin tracking with a pinch already held: no crash.
- Victory scrolls in both directions without moving the pointer.
- Remove the hand: no actions. Reintroduce it: fresh gesture confirmation.
- Make a fist: Mouse mode pauses without clicking. Point/pinch while paused: no actions. Open palm: movement resumes after confirmation.
- Switch modes: controls disable until explicitly re-enabled.
- In Media mode verify +/-5%, held-gesture debouncing, mute and unmute.
- Press Stop while controls are active; camera releases and actions stop.
- Move the physical pointer into a PyAutoGUI fail-safe corner: tracking stops; no automatic restart.
- Unplug webcam and close/restart application; no stale camera or repeated commands.
- If audio is unavailable, verify Mouse mode remains usable.

Record Python/package versions, failures and a short successful backup demo.
