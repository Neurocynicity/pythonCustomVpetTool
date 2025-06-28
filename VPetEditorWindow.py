import tkinter as tk
from VirtualPet import VPetData, Animation
from Logger import Logger, MessageLevel
from Utility import ScrollableFrame
import re

class VPetEditorWindow(tk.Toplevel):

    def __init__(self, vpetData : VPetData, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.title = "Vpet Editor"
        self.vpetData = vpetData
        self.currentAnimation = None
        self.loopPreview : bool = False
        self.previewPlaying = False
        self.previewCurrentFrameIndex = 0
        self.ReGenerateWindowContents()
        pass

    def ReGenerateWindowContents(self):

        for i in range(128):
            self.columnconfigure(i,weight=1)

        for i in range(128):
            self.rowconfigure(i,weight=1)

        lbl_petName = tk.Label(master=self, text=f"Editing: {self.vpetData.vpetName}")
        lbl_petName.grid(row=0, column=0)

        lbl_animationsHeader = tk.Label(master=self, text="Animations:")
        lbl_animationsHeader.grid(row=1, column=1, columnspan=2, sticky="we")

        row = 2

        for animation in self.vpetData.animations:
            btn_animationSelect = tk.Button(master=self, text=animation.name, command=lambda anim=animation: self.SetCurrentAnimation(anim))
            btn_animationSelect.grid(row=row, column=1, sticky="we")

            btn_animationDelete = tk.Button(master=self, text="delete", command=lambda anim=animation: self.SetCurrentAnimation(anim))
            btn_animationDelete.grid(row=row, column=2, sticky="we")

            row += 1

        txt_newAnimationName = tk.Text(master=self, height=1, width=20)
        txt_newAnimationName.insert(1.0, "New Animation Name")
        txt_newAnimationName.grid(row=row, column=1, sticky="nsew")

        btn_createNewAnimation = tk.Button(master=self, text=" + ", command=lambda: self.CreateNewAnimation(txt_newAnimationName.get('1.0', 'end')))
        btn_createNewAnimation.grid(row=row, column=2, sticky="nsew")
        
        row += 1

        txt_spawnableObjectsTitle = tk.Label(master=self, text="Spawnable Objects:")
        txt_spawnableObjectsTitle.grid(row=row, column=1)

        row += 1

        for spawnable in self.vpetData.spawnableObjects:
            btn_spawnableSelect = tk.Button(master=self, text=spawnable.name, command=lambda anim=spawnable: self.SetCurrentAnimation(anim))
            btn_spawnableSelect.grid(row=row, column=1, sticky="we")

            btn_spawnableDelete = tk.Button(master=self, text="delete", command=lambda anim=spawnable: self.SetCurrentAnimation(anim))
            btn_spawnableDelete.grid(row=row, column=2, sticky="we")

            row += 1

        # create the animation editor widgets ungridded so we can add/ remove them later
        self.lbl_currentlyEditingText = tk.Label(master=self, text="Currently Editing:")
        self.lbl_currentlyEditingAnimName = tk.Label(master=self, text="")

        self.val_currAnimHoldLastFrame = tk.BooleanVar()
        self.lbl_currAnimHoldLastFrame = tk.Label(master=self, text="Hold Last Frame?")
        self.chk_currAnimHoldLastFrame = tk.Checkbutton(master=self, variable=self.val_currAnimHoldLastFrame)
        
        self.lbl_currAnimUpdatesPerFrame = tk.Label(master=self, text="Updates Per Frame")
        self.txt_currAnimUpdatesPerFrame = tk.Text(master=self, height=1, width=20)

        self.lbls_frames : list[tk.Label] = []
        self.txts_frames : list[tk.Text]  = []

        self.btn_saveAnimationEdits = tk.Button(master=self, text="Save changes", command=self.WriteCurrentAnimationEditsToDataFile)

        self.lbl_previewText = tk.Label(master=self, text="Preview:")
        self.lbl_previewImage = tk.Label(master=self, bd=0)
        self.btn_playPreview = tk.Button(master=self, text="Play", command=self.PlayPreview)
        self.btn_loopPreview = tk.Button(master=self, text="Loop", command=self.ToggleLoop)
        pass

    def CreateNewAnimation(self, newAnimationName : str):
        print(newAnimationName)
        pass
        
    def ToggleLoop(self):
        self.loopPreview = not self.loopPreview
        self.btn_loopPreview.configure(text="looping" if self.loopPreview else "loop")
        pass

    def PlayPreview(self):
        if self.previewPlaying:
            return
        
        self.previewPlaying = True
        self.previewCurrentFrameIndex = -1
        self.UpdatePreviewAnimationFrame(self.currentAnimation)
        pass

    def UpdatePreviewAnimationFrame(self, animation):
        if not self.previewPlaying or animation != self.currentAnimation:
            return
        
        self.previewCurrentFrameIndex += 1

        if self.previewCurrentFrameIndex > len(self.currentAnimation.images) - 1:
            if not self.loopPreview:
                self.previewPlaying = False
                return
            
            self.previewCurrentFrameIndex = 0

        self.lbl_previewImage.configure(image=self.currentAnimation.images[self.currentAnimation.frames[self.previewCurrentFrameIndex]])
        
        waitTimeMs = self.vpetData.updateRateMs

        # if we have a specified value for this frame, then use it
        if len(self.currentAnimation.specifiedUpdatesPerFrame) > self.previewCurrentFrameIndex:
            waitTimeMs *= self.currentAnimation.specifiedUpdatesPerFrame[self.previewCurrentFrameIndex]
        else:
            waitTimeMs *= self.currentAnimation.updatesPerFrame

        self.after(waitTimeMs, lambda anim=self.currentAnimation: self.UpdatePreviewAnimationFrame(anim))
        pass

    def SetCurrentAnimation(self, animation : Animation):

        self.previewPlaying = False

        for x in self.lbls_frames:
            x.destroy()
        for x in self.txts_frames:
            x.destroy()

        # to make the editing section toggle off if the same animation is selected
        if self.currentAnimation == animation:
            self.currentAnimation = None
            self.HideAnimationEditingWidgets()
            return
        
        self.currentAnimation = animation
        self.lbl_currentlyEditingText.grid(row=1, column=4)

        self.lbl_currentlyEditingAnimName.config(text=animation.name)
        self.lbl_currentlyEditingAnimName.grid(row=1, column=5)
        
        self.lbl_currAnimHoldLastFrame.grid(row=2, column=5)
        self.chk_currAnimHoldLastFrame.grid(row=2, column=6)
        self.val_currAnimHoldLastFrame.set(animation.holdLastFrame)
        
        self.lbl_currAnimUpdatesPerFrame.grid(row=3, column=5)
        self.txt_currAnimUpdatesPerFrame.grid(row=3, column=6)
        self.txt_currAnimUpdatesPerFrame.delete('1.0', 'end')
        self.txt_currAnimUpdatesPerFrame.insert('1.0', animation.updatesPerFrame)

        self.btn_saveAnimationEdits.grid(row = 5, column=5, columnspan=2, sticky='nesw')

        self.lbl_previewText.grid(row=5, column=8)
        self.btn_loopPreview.grid(row=6, column=9)
        self.btn_playPreview.grid(row=7, column=8)

        self.lbl_previewImage.configure(image=animation.images[0])
        self.lbl_previewImage.grid(row=6, column=8)
        
        self.lbls_frames = []
        self.txts_frames = []

        col = 0

        self.scr_framesScrollFrame = ScrollableFrame(self)
        self.frm_scrollContents = tk.Frame(self.scr_framesScrollFrame)

        for i in range(len(animation.frames)):
            lbl_frame = tk.Label(self.frm_scrollContents, bd=0, image=animation.images[animation.frames[i]])
            lbl_frame.grid(row=0, column=col)

            txt_frame = tk.Text(master=self.frm_scrollContents, height=1, width=5)

            # if we have a specified value for this frame, then use it
            if len(animation.specifiedUpdatesPerFrame) > i:
                txt_frame.insert('1.0', animation.specifiedUpdatesPerFrame[i])
            else:
                txt_frame.insert('1.0', animation.updatesPerFrame)

            txt_frame.grid(row=1, column=col, sticky='nesw')

            self.lbls_frames.append(lbl_frame)
            self.txts_frames.append(txt_frame)

            col += 1

        self.frm_scrollContents.pack()
        self.scr_framesScrollFrame.grid(column=7, row=3, columnspan=3, sticky='nesw')

        pass

    def HideAnimationEditingWidgets(self):
        self.lbl_currentlyEditingText.grid_forget()

        self.lbl_currentlyEditingAnimName.grid_forget()
        
        self.lbl_currAnimHoldLastFrame.grid_forget()
        self.chk_currAnimHoldLastFrame.grid_forget()

        self.lbl_currAnimUpdatesPerFrame.grid_forget()
        self.txt_currAnimUpdatesPerFrame.grid_forget()

        self.btn_saveAnimationEdits.grid_forget()

        self.lbl_previewText.grid_forget()
        self.btn_loopPreview.grid_forget()
        self.btn_playPreview.grid_forget()
        pass

    def WriteCurrentAnimationEditsToDataFile(self):

        holdLastFrame = self.val_currAnimHoldLastFrame.get()
        updatesPerFrame = (int)(self.txt_currAnimUpdatesPerFrame.get('1.0', 'end'))
        
        specifiedUpdatesPerFrame : list[int] = []
        specifyUpdatesPerFrame = False

        for i in range(len(self.currentAnimation.images)):
            value = (int)(re.sub(r"\D", "", self.txts_frames[i].get('1.0', 'end')))
            specifiedUpdatesPerFrame.append(value)

        # if the specified individual frame counts aren't just the same number in every slot then we use them as specified
        specifyUpdatesPerFrame = any(i != specifiedUpdatesPerFrame[0] for i in specifiedUpdatesPerFrame)

        data : list[(str, str)] = []

        data.append(("holdLastFrame", (str)(holdLastFrame)))

        if specifyUpdatesPerFrame:
            data.append(("UpdatesPerFrame", (str)(specifiedUpdatesPerFrame)[1:-1]))
        else:
            data.append(("UpdatesPerFrame", updatesPerFrame))

        # now we write the data we have to the file
        self.AmendDataFile(self.currentAnimation.dataFilePath, data)

        # now have the animation read its new data from the new file
        self.currentAnimation.ReadAnimationDataFile()

        # calling set current animation with the current animation closes the tab
        # this ensures it refreshes the data without closing the tab
        temp = self.currentAnimation
        self.currentAnimation = None
        self.SetCurrentAnimation(temp)

        pass

    def AmendDataFile(self, pathToDataFile, data : list[(str, str)]):
        datafile = pathToDataFile.open()
        if datafile is None:
            for (var, value) in data:
                amendedData += var + ':' + str(value)

            datafile = pathToDataFile.open('w')
            datafile.write(amendedData)
            pass

        readLine = datafile.readline()
        amendedData = ""

        while readLine != "":
            splitComments = readLine.split("#")
            parts = splitComments[0].split(":", 1)
            # match case statements are python 3.10 and higher
            command = re.sub(r"[^\w\d]", "", parts[0].lower()) # small regex to remove non letter/ word characters

            for (var, value) in data:
                if command.lower() == var.lower():
                    parts[1] = value
                    data.remove((var, value))
                    break
            
            rebuiltLine = parts[0]
            if len(parts) > 1:
                rebuiltLine += ':' + str(parts[1])
            if len(splitComments) > 1:
                rebuiltLine += " #" + splitComments[1]
            
            if rebuiltLine[-1] != '\n':
                rebuiltLine += '\n'

            amendedData += rebuiltLine
            readLine = datafile.readline()

        for (var, value) in data:
            amendedData += var + ':' + str(value)

        datafile = pathToDataFile.open('w')
        datafile.write(amendedData)

        Logger.instance.Log(MessageLevel.MESSAGE, f"Updated animation data of {self.currentAnimation.name}")
    
    pass