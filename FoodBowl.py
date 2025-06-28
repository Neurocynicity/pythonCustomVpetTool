from PhysicsObject import PhysicsObject
from Utility import LoadImage, localPath

class FoodBowl(PhysicsObject):

    def __init__(self, scale : float = 1):
        super().__init__()
        self.hasFood = False
        self.bowlEmptyImage = LoadImage(localPath.joinpath("Objects", "foodBowlEmpty.png"), scale)
        self.bowlFullImage = LoadImage(localPath.joinpath("Objects", "foodBowlFull.png"), scale)
        
        self.window.UpdateImage(self.bowlEmptyImage)
        self.window.onClick = self.OnClick

    def OnClick(self):
        if self.hasFood:
            return
        
        self.hasFood = True
        self.window.UpdateImage(self.bowlFullImage)

    def EatFood(self):
        if not self.hasFood:
            return
        
        self.hasFood = False
        self.window.UpdateImage(self.bowlEmptyImage)