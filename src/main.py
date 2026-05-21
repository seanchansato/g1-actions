import sys
from simulator import Simulator
from controller import Controller
from actions.salute import Salute
from actions.wave import Wave
from actions.hands_up import HandsUp

ACTIONS = {
    "salute":    Salute,
    "wave":      Wave,
    "hands_up":  HandsUp,
}


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "salute"
    action_cls = ACTIONS.get(name)
    if action_cls is None:
        print(f"Unknown action '{name}'. Available: {list(ACTIONS)}")
        sys.exit(1)

    sim = Simulator()
    controller = Controller(sim.model, action_cls())
    sim.run(controller)


if __name__ == "__main__":
    main()
