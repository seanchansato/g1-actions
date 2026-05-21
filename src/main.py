import sys
from simulator import Simulator
from controller import Controller
from actions.arms_up import ArmsUp
from actions.come_closer import ComeCloser
from actions.heart import Heart
from actions.speaking2 import Speaking2
from actions.flexible import Flexible
from actions.salute import Salute
from actions.shrug import Shrug
from actions.t_position import TPosition
from actions.test import Test
from actions.speak import Speak
from actions.wave import Wave
from actions.hands_up import HandsUp
from actions.wave_recorded import (
    WaveRecorded,
    HandsUpRecorded,
    ShakeHand,
    ShowHand,
    DoPayment,
    DownPayment,
)

ACTIONS = {
    # Scripted (keyframe)
    "arms_up":       ArmsUp,
    "come_closer":   ComeCloser,
    "heart":         Heart,
    "speaking2":     Speaking2,
    "flexible":      Flexible,
    "salute":        Salute,
    "shrug":         Shrug,
    "t_position":    TPosition,
    "test":          Test,
    "speak":         Speak,
    "wave":          Wave,
    "hands_up":      HandsUp,
    # Recorded (real robot)
    "face_wave":     WaveRecorded,
    "hands_up_rec":  HandsUpRecorded,
    "shake_hand":    ShakeHand,
    "show_hand":     ShowHand,
    "do_payment":    DoPayment,
    "down_payment":  DownPayment,
}


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "salute"
    loop = "--loop" in sys.argv

    action_cls = ACTIONS.get(name)
    if action_cls is None:
        print(f"Unknown action '{name}'. Available: {list(ACTIONS)}")
        sys.exit(1)

    try:
        action = action_cls(loop=loop)
    except TypeError:
        action = action_cls()

    sim = Simulator()
    controller = Controller(sim.model, action)
    sim.run(controller)


if __name__ == "__main__":
    main()
