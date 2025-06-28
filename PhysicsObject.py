from PhysicsWindow import PhysicsObjectWindow

class PhysicsObject:

    def __init__(self) -> None:
        self.window : PhysicsObjectWindow = PhysicsObjectWindow()
        self.window.SetEvents()
        pass