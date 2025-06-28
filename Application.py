from PhysicsObject import PhysicsObject
from VirtualPet import VPet, VPetData
from VirtualPetEvents import vPetEvents
from VPetEditorWindow import VPetEditorWindow
from Utility import localPath
import tkinter as tk
from Logger import Logger, MessageLevel, LoggingLevel

# if folders are incorrectly found as vpets, add their names here:
nonVpetFolders : list[str] = ["NonVpets", "__pycache__", "build", "dist", "_tcl_data", "_tk_data", "numpy", "PIL", "psutil", "tcl8"]

# TODO probably load in the animations & vpets data here so it doesn't reload every spawn
# idk though it means you can edit it without restarting the app

class Application:
    def __init__(self) -> None:
        self.logger : Logger = Logger(LoggingLevel.ALL)
        self.editorWindows : list[VPetEditorWindow] = []
        self.physicsObjects : list[PhysicsObject] = []
        self.vpets : list[VPet] = []
        self.loadableVpets : list[VPetData] = []
        self.btn_destroyVpetsButtons : list[tk.Button] = []

        self.window = tk.Tk()

        self.LoadData()
        self.CreateWindowElements()

        pass

    def LoadData(self):
        for dir in localPath.iterdir():
            if dir.suffix != "" or dir.parts[-1] in nonVpetFolders:
                continue

            Logger.instance.Log(MessageLevel.MESSAGE, "Loading Vpet Data: " + dir.parts[-1])
            self.loadableVpets.append(VPetData(dir.parts[-1], self, vPetEvents))

        # self.animations : list[Animation] = [Animation(a, scale) for a in os.listdir(animationsPath)]

        pass

    def Update(self): # returns false when program ended
        try:
            self.window.update()

            for physicsObj in self.physicsObjects:
                physicsObj.window.update()

            for editorWindow in self.editorWindows:
                editorWindow.update()
            
        except tk.TclError:
            return False

        return True

    def SpawnVpet(self, vpetData : VPetData):
        Logger.instance.Log(MessageLevel.MESSAGE, "Spawning new Vpet: " + vpetData.vpetName)
        newVPet = vpetData.CreateNewInstance()
        newVPet.vpetName = newVPet.vpetName + str(len(self.vpets))
        self.vpets.append(newVPet)

        btn_destroyPet = tk.Button(master=self.window, text=newVPet.vpetName)
        btn_destroyPet.configure(command=lambda vpet=newVPet, btn_destroyPet=btn_destroyPet: self.DestroyVPet(vpet, btn_destroyPet))
        self.btn_destroyVpetsButtons.append(btn_destroyPet)
        self.ReOrderDestroyButtons()
        pass

    def ReOrderDestroyButtons(self):
        column = 1

        for destroyButton in self.btn_destroyVpetsButtons:
            destroyButton.grid(row=2, column=column)
            column += 1
        
        pass

    def DestroyVPet(self, vpet : VPet, btn_destroyPet : tk.Button):
        vpet.window.destroy()
        for spawnedObject in vpet.spawnedObjects:
            spawnedObject.destroy()
            
        self.vpets.remove(vpet)
        btn_destroyPet.destroy()
        self.btn_destroyVpetsButtons.remove(btn_destroyPet)
        self.ReOrderDestroyButtons()

    def CreateWindowElements(self):
        lbl_spawn = tk.Label(master=self.window, text="Spawn a new pet:")
        lbl_spawn.grid(row=0, column=0)

        lbl_edit = tk.Label(master=self.window, text="Edit a new pet:")
        lbl_edit.grid(row=1, column=0)

        xPos = 1

        for vpet in self.loadableVpets:
            btn_vpetSpawnButton = tk.Button(master=self.window, text=vpet.vpetName, command=lambda vpet=vpet: self.SpawnVpet(vpet))
            btn_vpetSpawnButton.grid(row=0, column=xPos)

            btn_vpetEditButton = tk.Button(master=self.window, text="Edit", command=lambda vpet=vpet: self.OpenEditorWindow(vpet))
            btn_vpetEditButton.grid(row=1, column=xPos)
            xPos += 1
        
        lbl_destroy = tk.Label(master=self.window, text="Destroy a pet:")
        lbl_destroy.grid(row=2, column=0)

    def OpenEditorWindow(self, vpetData : VPetData):
        self.editorWindows.append(VPetEditorWindow(vpetData, self.window))

        pass

application = Application()

# only continues while the application has not been destroyed
while application.Update():
    continue