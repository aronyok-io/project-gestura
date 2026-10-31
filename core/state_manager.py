from dataclasses import dataclass


@dataclass
class StateManager:
    enabled: bool = False
    mode: str = "Mouse"

    def set_mode(self, mode):
        if mode not in ("Mouse", "Media"):
            raise ValueError("Unknown control mode")
        self.mode = mode
        self.enabled = False
