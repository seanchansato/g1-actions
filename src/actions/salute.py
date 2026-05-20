from actions.base import Action

class Salute(Action):

    def update(self, t):

        progress = min(
            t / 2.0,
            1.0
        )

        shoulder = (
            0.8 * progress
        )

        return {
            "right_shoulder":
            shoulder
        }
