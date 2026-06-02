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
from actions.speak import Speak
from actions.wave import Wave
from actions.hands_up import HandsUp
from actions.high_five import HighFiveAction
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
    "flexible":      Flexible,
    "salute":        Salute,
    "shrug":         Shrug,
    "t_position":    TPosition,
    "test":          Test,
    "speak":         Speak,
    "wave":          Wave,
    "hands_up":      HandsUp,
    "high_five":     HighFiveAction,
    # Recorded (real robot)
    "face_wave":     WaveRecorded,
    "hands_up_rec":  HandsUpRecorded,
    "shake_hand":    ShakeHand,
    "show_hand":     ShowHand,
    "do_payment":    DoPayment,
    "down_payment":  DownPayment,
}


def _build_high_five(argv):
    """Parse high_five-specific CLI flags and construct the action.

    Flags:
      --target X Y Z   explicit pelvis-frame target position (metres)
      --camera         open the depth camera and scan for a raised hand
      --left           force left arm
      --right          force right arm
    """
    target_pos = None
    camera     = None
    side       = "auto"

    if "--target" in argv:
        i = argv.index("--target")
        try:
            target_pos = [float(argv[i+1]), float(argv[i+2]), float(argv[i+3])]
        except (IndexError, ValueError):
            print("Usage: --target X Y Z  (three floats, pelvis-frame metres)")
            sys.exit(1)

    if "--camera" in argv:
        from perception.camera import DepthCamera
        camera = DepthCamera(show=True)

    if "--left" in argv:
        side = "left"
    elif "--right" in argv:
        side = "right"

    action = HighFiveAction(target_pos=target_pos, camera=camera, side=side)

    if camera is not None:
        camera.stop()

    return action


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "salute"
    loop = "--loop" in sys.argv

    action_cls = ACTIONS.get(name)
    if action_cls is None:
        print(f"Unknown action '{name}'. Available: {list(ACTIONS)}")
        sys.exit(1)

    if name == "high_five":
        action = _build_high_five(sys.argv[2:])
    else:
        try:
            action = action_cls(loop=loop)
        except TypeError:
            action = action_cls()

    sim = Simulator()
    controller = Controller(sim.model, action)
    sim.run(controller)


if __name__ == "__main__":
    main()
