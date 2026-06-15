import sys
from simulator import Simulator
from controller import Controller
from actions.arms_up import ArmsUp
from actions.come_closer import ComeCloser
from actions.come_closer2 import ComeCloser2
from actions.handspin import HandSpin
from actions.heart import Heart
from actions.push import Push
from actions.stop import Stop
from actions.speaking2 import Speaking2
from actions.flexible import Flexible
from actions.salute import Salute
from actions.shrug import Shrug
from actions.t_position import TPosition
from actions.test import Test
from actions.talking_2s import Talking2s
from actions.talking_4s import Talking4s
from actions.talking_6s import Talking6s
from actions.talking_8s import Talking8s
from actions.talking_10s import Talking10s
from actions.talking_12s import Talking12s
from actions.talking_14s import Talking14s
from actions.talking_16s import Talking16s
from actions.talking_18s import Talking18s
from actions.talking_20s import Talking20s
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
    "come_closer2":  ComeCloser2,
    "handspin":      HandSpin,
    "heart":         Heart,
    "push":          Push,
    "stop":          Stop,
    "speaking2":     Speaking2,
    "talking_2s":    Talking2s,
    "talking_4s":    Talking4s,
    "talking_6s":    Talking6s,
    "talking_8s":    Talking8s,
    "talking_10s":   Talking10s,
    "talking_12s":   Talking12s,
    "talking_14s":   Talking14s,
    "talking_16s":   Talking16s,
    "talking_18s":   Talking18s,
    "talking_20s":   Talking20s,
    "flexible":      Flexible,
    "salute":        Salute,
    "shrug":         Shrug,
    "t_position":    TPosition,
    "test":          Test,
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
