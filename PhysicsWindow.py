import tkinter as tk
from PIL import ImageOps, ImageTk
from random import randint
from Utility import Vector2, Clamp, CallIfNotNone
from Settings import vpetPhysics, deltaTime

class PhysicsObjectWindow(tk.Toplevel):
    def __init__(self, OnClick : callable = None,  *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        
        self.configure(cursor="hand2")

        self.labelBaseImage = None
        self.flipped = False

        self.onClick : callable = OnClick

        self.applyingPhysics = True
        self.applyingGravity = True
        self.frictionEnabled = True
        self.grabbed = False
        self.size = Vector2(0, 0)
        self.position = Vector2(0,0)
        self.velocity = Vector2(0, 0)
        self.lastMovements = []

        self.overrideredirect(True)

        self.config(highlightbackground='black')
        self.wm_attributes('-transparentcolor','black')
        
        self.attributes('-topmost', True)

        self.label = tk.Label(self,bd=0,bg='black')
        self.label.pack()

        # randomise our position
        self.bounds = self.GetBounds()
        self.SetPos(Vector2(randint(0, self.bounds.x), randint(0, int(self.bounds.y / 3))))

        self.after(vpetPhysics.physicsUpdateRate, self.PhysicsUpdate)

    def SetEvents(self, GrabStartEvent : callable = None, GrabEndEvent : callable = None, WhileGrabbedEvent : callable = None,\
                  PettingStartEvent : callable = None, PettingEndEvent : callable = None, WhilePettingEvent : callable = None,):
        self.GrabStartEvent = GrabStartEvent
        self.WhileGrabbedEvent = WhileGrabbedEvent
        self.GrabEndEvent = GrabEndEvent

        self.PettingStartEvent = PettingStartEvent
        self.WhilePettingEvent = WhilePettingEvent
        self.PettingEndEvent = PettingEndEvent

        # bind left mouse events
        self.label.bind("<ButtonPress-1>", self.OnGrabStart)
        self.label.bind("<ButtonRelease-1>", self.OnGrabEnd)
        self.label.bind("<B1-Motion>", self.WhileGrabbed)
        
        # bound right mouse events
        self.label.bind("<ButtonPress-3>", self.PettingStartEvent)
        self.label.bind("<ButtonRelease-3>", self.PettingEndEvent)
        self.label.bind("<B3-Motion>", self.WhilePettingEvent)
        pass

    def OnGrabStart(self, event):
        CallIfNotNone(self.GrabStartEvent)
        self.grabbed = True
        self.velocity = Vector2(0, 0)
        self.lastMovements = []

        self.x = event.x
        self.y = event.y

    def OnGrabEnd(self, event):
        CallIfNotNone(self.GrabEndEvent)
        self.grabbed = False
        self.applyingPhysics = True
        self.applyingGravity = True
        self.x = None
        self.y = None

        if len(self.lastMovements) < 2:
            if self.onClick:
                self.onClick()

            self.lastMovements = []
            return

        averageVelocityPerFrame = Vector2.AverageVector(self.lastMovements)
        # convert velocity from pixels per frame to pixels per second
        self.velocity = averageVelocityPerFrame * vpetPhysics.throwForceMultiplier / deltaTime
        self.StartPhysicsLoop()

    def WhileGrabbed(self, event):
        CallIfNotNone(self.WhileGrabbedEvent)
        deltax = event.x - self.x
        deltay = event.y - self.y

        self.lastMovements.append(Vector2(deltax, deltay))

        self.SetPos(Vector2(self.winfo_x() + deltax, self.winfo_y() + deltay))

        # x = self.winfo_x() + deltax
        # y = self.winfo_y() + deltay
        # self.geometry(f"+{x}+{y}")

        if len(self.lastMovements) > vpetPhysics.velocitySmoothingInt:
            self.lastMovements.pop(0)
        pass

    def GetBounds(self):
        return Vector2(self.winfo_screenwidth() - self.winfo_width(),
                       self.winfo_screenheight() - self.winfo_height() - vpetPhysics.bottomPadding)

    def SetPos(self, position : Vector2):
        position.x = Clamp(position.x, 0, self.bounds.x)
        position.y = Clamp(position.y, 0, self.bounds.y)

        self.position = position
        self.geometry(f"+{int(self.position.x)}+{int(self.position.y)}")
        pass

    def StartPhysicsLoop(self):
        self.applyingPhysics = True
        self.applyingGravity = True
        
        bounds = self.GetBounds()
        newPosition = Vector2(0, 0)
        newPosition.x = Clamp(self.position.x, 0, bounds.x)
        newPosition.y = Clamp(self.position.y, 0, bounds.y)
        self.SetPos(newPosition)

        self.PhysicsUpdate()

    def PhysicsUpdate(self):

        if self.grabbed:
            pass

        bounds = self.GetBounds()

        if self.applyingGravity:
            self.velocity += Vector2(0, vpetPhysics.gravity * deltaTime)
        elif self.frictionEnabled:
            self.velocity -= (self.velocity * vpetPhysics.frictionConstant) * deltaTime
        newPos : Vector2 = self.position + self.velocity * deltaTime

        # if we're colliding with the left or right wall
        if newPos.x < 0 or newPos.x > bounds.x:
            self.velocity.x = -(self.velocity.x * vpetPhysics.bouncinessConstant)

            if abs(self.velocity.x) < 20:
                self.velocity.x = 0
            
            # recalculate newpos
            newPos = self.position + self.velocity * deltaTime
        
        # if we're colliding with the ceiling or floor
        if newPos.y < 0 or newPos.y > bounds.y:
            self.velocity.y = -(self.velocity.y * vpetPhysics.bouncinessConstant)
            
            if abs(self.velocity.y) < 20:
                self.velocity.y = 0
            
                if newPos.y >= 0: # if collision is with the floor
                    self.applyingGravity = False
            
            # recalculate newpos
            newPos = self.position + self.velocity * deltaTime

        self.SetPos(newPos)

        if self.velocity.magnitude > 1 or self.applyingGravity:
            self.after(vpetPhysics.physicsUpdateRate, self.PhysicsUpdate)
        else:
            self.applyingPhysics = False
            self.velocity = Vector2(0, 0)

    def ApplyForce(self, force : Vector2):
        self.velocity += force / deltaTime
        self.StartPhysicsLoop()
        pass

    def HandleResize(self, newSize : Vector2):
        difference = newSize - self.size

        newPosition = self.position - difference / 2
        self.SetPos(newPosition)
        self.size = newSize
        pass

    def UpdateImage(self, image):
        self.labelBaseImage = image
        newSize = Vector2(self.labelBaseImage.width(), self.labelBaseImage.height())
        if newSize != self.size:
            self.HandleResize(newSize)

        if self.flipped:
            image = ImageTk.getimage(self.labelBaseImage)
            flippedImage = ImageOps.mirror(image)
            self.labelFinalImage = ImageTk.PhotoImage(flippedImage)
        else:
            self.labelFinalImage = self.labelBaseImage
        
        self.label.configure(image=self.labelFinalImage)

    def SetFlipped(self, flipped : bool):
        self.flipped = flipped
        self.UpdateImage(self.labelBaseImage)