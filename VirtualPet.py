from PhysicsObject import PhysicsObject
from PIL import Image, ImageTk
from Utility import CallIfNotNone, localPath, GenerateDefaultAnimationDataFile, GenerateDefaultVpetDataFile
import random
import pathlib
from copy import deepcopy
import re
from Logger import Logger, MessageLevel
from DataFileReader import DataFileReader

validAnimationFileTypes = [".jpg",".gif",".png",".tga"]

class Animation(DataFileReader):

    def __init__(self, pathToAnimation : pathlib.Path, animation = None):
        if animation != None:
            return self.Initialise(animation)

        self.pathToAnimation = pathToAnimation
        self.name = pathToAnimation.parts[-1].lower().split('.')[0]
        self.updateCount = 0
        self.currentFrameIndex = 0
        self.images = []
        self.frames = []
        self.imagePaths = []

        self.animationDataFileFound = False
        self.scale = 1
        self.holdLastFrame = False
        self.updatesPerFrame = 0
        self.specifiedUpdatesPerFrame = []

        potentialDataFilePaths = []
        self.dataFilePath = None

        if pathToAnimation.suffix == "": # it's a directory, try to load all images inside

            Logger.instance.Log(MessageLevel.MESSAGE, f"| Loading animation {self.name}...")
            
            for item in pathToAnimation.iterdir():
                if item.suffix.lower() not in validAnimationFileTypes:
                    if item.suffix.lower() == ".txt" and not self.animationDataFileFound: # try and load data from data file
                        potentialDataFilePaths.append(item)
                        
                    continue

                self.imagePaths.append(pathToAnimation.joinpath(item))
            
            Logger.instance.Log(MessageLevel.MESSAGE, f"| | Found {len(self.imagePaths)} frames!")

        elif pathToAnimation.suffix.lower() == ".gif":  # it's a gif, load it as an animation with the filename as the name
            #TODO FIGURE THIS OUT
            pass

        for file in potentialDataFilePaths:
            self.ReadAnimationDataFile(file)

        for path in self.imagePaths:
            self.images.append(GetFixedImage(path, self.scale))
        
        if not self.animationDataFileFound:
            GenerateDefaultAnimationDataFile(self.name, pathToAnimation)
            self.updatesPerFrame = 1
        pass

    def Initialise(self, animation):
        self.pathToAnimation = animation.pathToAnimation
        self.name = animation.name
        self.updateCount = animation.updateCount
        self.currentFrameIndex = animation.currentFrameIndex
        self.images = animation.images
        self.frames = animation.frames

        self.animationDataFileFound = animation.animationDataFileFound
        self.scale = animation.scale
        self.holdLastFrame = animation.holdLastFrame
        self.updatesPerFrame = animation.updatesPerFrame
        self.specifiedUpdatesPerFrame = animation.specifiedUpdatesPerFrame

        self.dataFilePath = None
        pass

    def Clone(self):
        return Animation(None, self)

    def UpdateAnimation(self):
        lastFrameIndex = len(self.frames) - 1
        
        self.updateCount += 1

        # if we have a specified value for this frame, then use it
        if len(self.specifiedUpdatesPerFrame) > self.currentFrameIndex:

            if self.updateCount >= self.specifiedUpdatesPerFrame[self.currentFrameIndex]:
                self.currentFrameIndex += 1
                self.updateCount = 0

        # otherwise take the default value
        elif self.updateCount == self.updatesPerFrame:
            self.currentFrameIndex += 1
            self.updateCount = 0

        if self.currentFrameIndex > lastFrameIndex:

            if self.holdLastFrame:
                self.currentFrameIndex = lastFrameIndex
            else:
                self.currentFrameIndex = 0
        
        return self.images[self.frames[self.currentFrameIndex]]
    
    def AnimationEnd(self):
        return self.currentFrameIndex == len(self.frames) - 1

    def ReadAnimationDataFile(self, path):
        Logger.instance.Log(MessageLevel.MESSAGE, f"| | Found {self.name} animation data file at {path}")
        self.holdLastFrame = False
        self.updatesPerFrame = 0
        self.specifiedUpdatesPerFrame = []
        self.animationDataFileFound = True
        self.dataFilePath = path

        super().ReadAnimationDataFile(self.dataFilePath)

        if self.updatesPerFrame == 0: # if we still don't have a value for updates a frame
            self.updatesPerFrame = 1 # then use 1 as default

        if len(self.frames) == 0:
            self.frames = [x for x in range(0, len(self.imagePaths))]

        pass

    def HandleDataFromDataFile(self, command, value):
        if command == "holdlastframe":
            value = re.sub(r"[^\w\d]", "", value.lower())
            self.holdLastFrame = True if value == "1" or value == "true" else False
        elif command == "updatesperframe":
            values = re.sub(r"[^\d:,x]", "", value.lower())
            userValues = values.split(',')

            for value in userValues:
                # if it's just a number
                if len(re.sub(r"\d", "", value)) == 0:
                    if self.updatesPerFrame == 0: # and we don't have a default value yet
                        self.updatesPerFrame = int(value) # then take this value as the default value
                    
                    else: # otherwise we've found another value, which means the user is listing every delay per frame
                        if len(self.specifiedUpdatesPerFrame) == 0: # if we haven't added the first value we found, add it now
                            self.specifiedUpdatesPerFrame.append(self.updatesPerFrame)
                        
                        self.specifiedUpdatesPerFrame.append(int(value))

                # if the user has given a delay for a specific frame
                elif ':' in value:
                    valueParts = value.split(':')
                    index = int(valueParts[0])
                    if len(self.specifiedUpdatesPerFrame) > index:
                        self.specifiedUpdatesPerFrame[index] = int(valueParts[1])
                    else:
                        while len(self.specifiedUpdatesPerFrame) < index:
                            self.specifiedUpdatesPerFrame.append(self.updatesPerFrame)
                        self.specifiedUpdatesPerFrame.append(int(valueParts[1]))
                
                # if the user wants to add the same delay multiple times
                elif 'x' in value:
                    valueParts = value.split('x')
                    valueToAppend = int(valueParts[0])
                    timesToAppend = int(valueParts[1])
                    for _ in range(0, timesToAppend):
                        self.specifiedUpdatesPerFrame.append(valueToAppend)

        elif command == "frames":
            values = re.sub(r"[^\d,]", "", value.lower()) # remove all non digits and commas
            userValues = values.split(',')

            for value in userValues:
                if value == '':
                    continue
                self.frames.append(int(value))

        elif command == "scale":
            value = re.sub(r"[^\d.]", "", value.lower()) # remove all non digits
            self.scale = float(value)


        elif command != "":
            Logger.instance.Log(MessageLevel.WARNING, f"| | Unknown command: \"{command}\" in {self.name}'s animation data file.  Use # to write comments")

class VPetData:

    def __init__(self, name, application, vPetEvents : list):
        self.vpetName = name
        self.application = application
        self.spawnableObjects = []

        self.frameRate = 20
        self.updateRateMs = int(1000 / self.frameRate)
        self.deltaTime = self.updateRateMs / 1000


        # Load vpet data
        self.TryFindVpetDataFile()

        # Load events
        self.events : list[VPetEvent] = [vpetEvent for vpetEvent in vPetEvents\
            if (self.vpetName in vpetEvent.allowedVpetArgs and vpetEvent.vpetArgsExclusive)\
            or ('-' + self.vpetName not in vpetEvent.allowedVpetArgs and not vpetEvent.vpetArgsExclusive)]

        # Load animations
        self.animations : list[Animation] = []
        self.LoadVpetAnimations()
        pass

    def TryFindVpetDataFile(self):

        foundDataFile = False
        vpetFolderPath = localPath.joinpath(self.vpetName)
        
        for subpath in vpetFolderPath.iterdir():
                
            if subpath.suffix == ".txt":
                foundDataFile = True
                Logger.instance.Log(MessageLevel.MESSAGE, f"| Found potential text file for {self.vpetName}: {subpath.parts[-1]}")
                self.LoadVpetDataFile(subpath)

        if not foundDataFile:
            GenerateDefaultVpetDataFile(self.vpetName, vpetFolderPath)
            self.frameRate = 20
            self.updateRateMs = int(1000 / self.frameRate)
            self.deltaTime = self.updateRateMs / 1000

        pass

    def LoadVpetDataFile(self, pathToDataFile : pathlib.Path):
        datafile = pathToDataFile.open()
        readLine = datafile.readline()
        while readLine != "":
            removedComments = readLine.split("#")[0]
            parts = removedComments.split(":", 1)
            # match case statements are python 3.10 and higher
            command = re.sub(r"[^\w\d]", "", parts[0].lower()) # small regex to remove non letter/ word characters

            if command == "vpetframerate":
                value = re.sub(r"[\D]", "", parts[1].lower())
                self.frameRate = float(value)
                self.updateRateMs = int(1000 / self.frameRate)
                self.deltaTime = self.updateRateMs / 1000
            
            elif command != "":
                Logger.instance.Log(MessageLevel.WARNING, f"| Unknown command: \"{command}\" in {self.vpetName}'s animation data file.  Use # to write comments")

            readLine = datafile.readline()

        pass

    def LoadVpetAnimations(self):

        vpetFolderPath = localPath.joinpath(self.vpetName)
        
        for pathToItem in vpetFolderPath.iterdir():
            if pathToItem.suffix != "":
                continue

            if pathToItem.parts[-1].lower() == "objects":
                self.LoadVpetSpawnableObjects(pathToItem)
                continue

            animation = Animation(pathToItem)

            if animation is not None:
                self.animations.append(animation)

        pass

    def LoadVpetSpawnableObjects(self, pathToObjectsFolder : pathlib.Path):
        for pathToObject in pathToObjectsFolder.iterdir():
            if pathToObject.suffix != "":
                continue

            spawnableObject = VPetSpawnableObjectData(pathToObject)

            if spawnableObject is not None:
                self.spawnableObjects.append(spawnableObject)
        pass

    def CreateNewInstance(self):
        return VPet(self)

    pass

class VPet(PhysicsObject):

    def OnGrab(self):
        if self.currentAnimation.name != "grabbed" or self.currentAnimation.name != "falling":
            self.pausedAnimation = self.currentAnimation

        self.SetAnimation("grabbed")
        self.UpdateAnimation()
        pass

    def OnGrabEnd(self):
        self.SetAnimation("falling")
        self.UpdateAnimation()
        pass

    def OnPettingStart(self, event):
        if self.window.applyingPhysics or self.window.grabbed:
            return
        elif self.currentAnimation.name == "happy":
            return
        
        self.pausedAnimation = self.currentAnimation
        self.updatesSinceLastPet = 0
        self.SetAnimation("Happy")
        pass

    def OnPettingEnd(self, event):
        pass

    def WhilePetting(self, event):
        self.updatesSinceLastPet = 0
        pass

    def __init__(self, VpetData : VPetData) -> None:
        super().__init__()
        self.vpetName = VpetData.vpetName
        self.application = VpetData.application

        self.spawnableObjects : list[VPetSpawnableObjectData] = VpetData.spawnableObjects
        self.spawnedObjects = []

        self.frameRate = VpetData.frameRate
        self.updateRateMs = VpetData.updateRateMs
        self.deltaTime = VpetData.deltaTime

        # Load events
        self.events : list[VPetEvent] = VpetData.events
        self.currentEvent : VPetEvent = None
        self.updatesUntilEvent : int = 0
        self.ResetTimeUntilEvent()

        self.frameCount = 0
        self.updatesSinceLastPet = 0

        # Load animations
        self.animations : list[Animation] = VpetData.animations
        self.currentAnimation : Animation = self.GetAnimation("Idle")
        
        self.UpdateAnimation()
        self.pausedAnimation = self.GetAnimation("Idle")

        self.window.SetEvents(GrabStartEvent=self.OnGrab, GrabEndEvent=self.OnGrabEnd,\
                              PettingStartEvent=self.OnPettingStart, PettingEndEvent=self.OnPettingEnd, WhilePettingEvent=self.WhilePetting)

        self.window.after(self.updateRateMs, self.Update)
        self.window.update()
        pass

    def ResetTimeUntilEvent(self):
        # 5 - 20 seconds worth of updates
        self.updatesUntilEvent = int(((random.random() * 5) + 5) / self.deltaTime)
        pass

    def Update(self):
        self.frameCount += 1
        self.updatesSinceLastPet += 1

        # update spawnables first so they don't stick around post destruction for long
        for spawned in self.spawnedObjects:
            if spawned.Update():
                spawned.window.destroy()
                self.spawnedObjects.remove(spawned)

        # if we're grabbed we don't do anything, transitioning into/ out of grab animation is handled elsewhere
        if self.window.grabbed:
            pass
        elif self.window.velocity.y != 0: # if we're falling/ bouncing
            # if we've just started falling/ bouncing then start animation
            if self.currentAnimation.name != "falling":
                if self.currentAnimation.name != "grabbed" or self.currentAnimation.name != "falling":
                    self.pausedAnimation = self.currentAnimation
                self.SetAnimation("falling")
                self.UpdateAnimation()

        elif self.currentAnimation.name == "happy":
            if self.updatesSinceLastPet > self.frameRate * 3:
                    self.currentAnimation = self.pausedAnimation
            
        else: # update state machine

            if self.currentAnimation.name == "grabbed" or self.currentAnimation.name == "falling":
                self.currentAnimation = self.pausedAnimation                

            self.updatesUntilEvent -= 1
            if not self.currentEvent and self.updatesUntilEvent < 0:

                # if we're affected by physics then skip this event
                if self.window.applyingPhysics:
                    self.ResetTimeUntilEvent()
                # otherwise start a random event
                else:
                    newEvent : VPetEvent = random.choice(self.events)
                    self.currentEvent = newEvent.Clone()
                    self.currentEvent.Start(self)

            if self.currentEvent:
                if self.currentEvent.Update(self): # returns True when finished
                    self.currentEvent = None
                    self.SetAnimation("Idle")
                    self.ResetTimeUntilEvent()

        # update vpet state
        self.UpdateAnimation()

        self.window.after(self.updateRateMs, self.Update)
        pass

    def UpdateAnimation(self):
        nextImage = self.currentAnimation.UpdateAnimation()
        if nextImage != self.window.labelBaseImage:
            self.window.UpdateImage(image=nextImage)
        pass

    def SetAnimation(self, name : str):
        animation = self.GetAnimation(name)
        self.currentAnimation = animation.Clone()
        self.currentAnimation.currentFrameIndex = 0
        self.currentAnimation.updateCount = 0

    def GetAnimation(self, name : str):
        animation = next((animation for animation in self.animations if animation.name==name.lower()), None)

        if animation == None:

            text : str = f"ERROR: Could not find animation {name} for vpet {self.vpetName}, valid animations for this pet are:"

            for anim in self.animations:
                text = text + '\n' + anim.name

            Logger.instance.Log(MessageLevel.ERROR, text)

            return self.animations[0]

        return animation

    def SpawnSpawnableObject(self, objectName : str):
        for spawnable in self.spawnableObjects:
            if spawnable.name.lower() == objectName.lower():
                newObject = spawnable.SpawnNew(self, None)
                newObject.window.SetPos(self.window.position)
                self.spawnedObjects.append(newObject)
        
        return newObject

def GetFixedImage(path, scale):
    image = Image.open(path)
    image = image.resize((int(image.size[0] * scale), int(image.size[1] * scale)), Image.Resampling.NEAREST)

    image = image.convert("RGBA")

    pixdata = image.load()

    # Clean the background noise, if color != white, then set to black
    # e^e^e% of this code's revenue goes to Falco Moon
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            if pixdata[x, y] == (0, 0, 0, 255):
                pixdata[x, y] = (0, 0, 1, 255)

    return ImageTk.PhotoImage(image)
    
class AnimationTransition():
    def __init__(self, animation : str = None, secondsUntilFinished : int = 0, finishWithAnimation : bool = False, 
                 OnStart : callable = None, WhileAnimation : callable = None, OnEnd : callable = None,
                 IsFinished : callable = None, GetCurrentAnimation : callable = None):
        
        self.animation = animation
        self.finishWithAnimation = finishWithAnimation

        self.updatesCount = 0
        self.secondsUntilFinished = secondsUntilFinished
        self.updatesUntilFinished = 0

        self.OnStart = OnStart
        self.WhileAnimation = WhileAnimation
        self.OnEnd = OnEnd

        self.GetCurrentAnimation = GetCurrentAnimation
        self.IsFinished = IsFinished

        if self.IsFinished is None and self.secondsUntilFinished == 0 and not self.finishWithAnimation:
            self.finishWithAnimation = True
        pass

    def Clone(self):
        return AnimationTransition(self.animation, self.secondsUntilFinished, self.finishWithAnimation, self.OnStart,\
                                   self.WhileAnimation, self.OnEnd, self.IsFinished, self.GetCurrentAnimation)

    def Finished(self, vpet : VPet):
        if self.IsFinished:
            return self.IsFinished(vpet)

        if self.finishWithAnimation:
            return vpet.currentAnimation.AnimationEnd()
        
        if self.updatesUntilFinished == 0: # if updates until finished isn't calculated, then calculate it
            self.updatesUntilFinished = int(self.secondsUntilFinished / vpet.deltaTime)
        
        return self.updatesCount >= self.updatesUntilFinished

class VPetEvent:
    def __init__(self, transitions : list[AnimationTransition], allowedVpetArgs : list[str] = []) -> None:
        self.allowedVpetArgs = allowedVpetArgs
        # the vpet args are "exclusive" if the list doesn't contain any disallowed vpets
        # if the list is only additions then it's interpreted as those being the only vpets allowed
        # to do that action
        self.vpetArgsExclusive = len([arg for arg in self.allowedVpetArgs if '-' not in arg]) > 0
        self.transitions = transitions
        self.currentIndex = -1
        self.currentTransition = None
        pass

    def Clone(self):
        return VPetEvent([x.Clone() for x in self.transitions], self.allowedVpetArgs)

    def Start(self, vpet : VPet):
        self.currentIndex = -1
        self.currentTransition = None
        self.UpdateState(vpet)
        pass

    def GetVPetAnimation(self, vpet : VPet):
        if self.currentTransition.animation:
            return vpet.GetAnimation(self.currentTransition.animation).Clone()
        
        return vpet.GetAnimation(self.currentTransition.GetCurrentAnimation(vpet)).Clone()

    def UpdateState(self, vpet : VPet) -> bool:
        
        if self.currentTransition is not None:
            CallIfNotNone(self.currentTransition.OnEnd, vpet)
        
        self.currentIndex += 1

        if self.currentIndex >= len(self.transitions):
            return True

        self.currentTransition = self.transitions[self.currentIndex]
        self.currentTransition.updatesCount = 0
        CallIfNotNone(self.currentTransition.OnStart, vpet)

        vpet.currentAnimation = self.GetVPetAnimation(vpet)
        vpet.currentAnimation.currentFrameIndex = 0
        return False

    def Update(self, vpet : VPet) -> bool:
        self.currentTransition.updatesCount += 1

        CallIfNotNone(self.currentTransition.WhileAnimation, vpet)

        transitionFinished = self.currentTransition.Finished(vpet)
        if not transitionFinished:
            if self.currentTransition.WhileAnimation is not None:
                self.currentTransition.WhileAnimation(vpet)
            return False        

        return self.UpdateState(vpet)

class VPetSpawnableObjectData(Animation):
    def SpawnNew(self, vpetOwner : VPet, position):
        return VPetSpawnedObject(self)

    pass

class VPetSpawnedObject(PhysicsObject):
    def __init__(self, data : VPetSpawnableObjectData):
        super().__init__()
        self.animation = data.Clone()
        self.DestroyNextFrame = False
        pass

    def Update(self):
        if self.DestroyNextFrame:
            return True

        self.DestroyNextFrame = self.animation.AnimationEnd()

        nextImage = self.animation.UpdateAnimation()
        if nextImage != self.window.labelBaseImage:
            self.window.UpdateImage(image=nextImage)
        
        return False