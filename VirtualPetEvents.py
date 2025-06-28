from VirtualPet import VPet, AnimationTransition, VPetEvent
from Settings import deltaTime
from Utility import Vector2
import random as r

VPetWalkSpeed = 80

def VPetSetFlipped(vpet : VPet, flipped : bool):
    vpet.window.SetFlipped(flipped)

def VPetClimb(vpet : VPet):
    vpet.window.SetPos(vpet.window.position + Vector2(0, -160) * deltaTime)

def EnableVpetPhysics(vpet : VPet):
    vpet.window.StartPhysicsLoop()

def VPetWalk(vpet : VPet, walkingRight : bool):
    movement = Vector2(40 if walkingRight else -40, 0)
    vpet.window.SetPos(vpet.window.position + movement * deltaTime)

def VPetWalkRandomly(vpet : VPet):
    if r.randint(0, int(vpet.frameRate)) == 0:
        vpet.window.SetFlipped(not vpet.window.flipped)

    movement = Vector2(-40 if vpet.window.flipped else 40, 0)
    vpet.window.SetPos(vpet.window.position + movement * deltaTime)

def EndOfRopeJump(vpet : VPet):
    jumpDirection = r.choice([-1 ,1])
    vpet.window.ApplyForce(Vector2(jumpDirection * r.randrange(5, 20), -10))
    vpet.window.SetFlipped(True if jumpDirection == -1 else False)

def Jump(vpet : VPet):
    jumpDirection = r.choice([-1 ,1])
    vpet.window.ApplyForce(Vector2(jumpDirection * r.randrange(5, 20), r.randrange(-40, -10)))
    vpet.window.SetFlipped(True if jumpDirection == -1 else False)

def PenguinSlide(vpet : VPet):
    jumpDirection = r.choice([-1 ,1])
    vpet.window.frictionEnabled = False
    vpet.window.ApplyForce(Vector2(jumpDirection * 10, -10))
    vpet.window.SetFlipped(True if jumpDirection == -1 else False)

def EnableFriction(vpet : VPet):
    vpet.window.frictionEnabled = True

def FoodBowlToVPetsRight(vpet : VPet):
    return vpet.application.foodBowl.window.position.x - vpet.window.position.x > 0

def ArrivedAtFoodBowl(vpet : VPet):
    return (vpet.application.foodBowl.window.position.x - vpet.window.position.x) <= 50

def GetWalkAnimation(vpet : VPet) -> str:

    if FoodBowlToVPetsRight(vpet):
        return 'Walk Right'
    else:
        return 'Walk Left'

def WalkToFoodBowl(vpet : VPet):
    if FoodBowlToVPetsRight(vpet):
        VPetWalk(vpet, True)
    else:
        VPetWalk(vpet, False)
    pass

def FoodInBowlEaten(vpet : VPet):
    return not vpet.application.foodBowl.hasFood or vpet.currentAnimation.AnimationEnd()

def ThrowBomb(vpet : VPet):
    bomb = vpet.SpawnSpawnableObject("bomb")
    force = Vector2(-15 if vpet.window.flipped else 15, -15)
    bomb.window.ApplyForce(force)
    pass


vPetEvents = [
    # fall asleep event
    VPetEvent([AnimationTransition('Idle to Sleep', finishWithAnimation=True),
                AnimationTransition('Sleep', secondsUntilFinished=20),
                AnimationTransition('Sleep to Idle', finishWithAnimation=True)
                ], ["Cat"]),

    # walk left event
    VPetEvent([AnimationTransition('Walk', secondsUntilFinished=5,\
                OnStart=lambda vpet: VPetSetFlipped(vpet, True), WhileAnimation=lambda vpet: VPetWalk(vpet, False))],
                ["-Tenna"]),
    # walk right event
    VPetEvent([AnimationTransition('Walk', secondsUntilFinished=5,\
                OnStart=lambda vpet: VPetSetFlipped(vpet, False), WhileAnimation=lambda vpet: VPetWalk(vpet, True))],
                ["-Tenna"]),

    # Jump event
    VPetEvent([AnimationTransition('idle', OnStart=Jump, secondsUntilFinished=2)], ["-PenguinSpelunky2"]),

    # Penguin Spelunky 2 Slide event
    VPetEvent([AnimationTransition('slide', OnStart=PenguinSlide, OnEnd=EnableFriction, secondsUntilFinished=3)], ["PenguinSpelunky2"]),

    # Lise Project Scan event
    VPetEvent([AnimationTransition('scan', finishWithAnimation=True)], ["LiseProject"]),

    # Lise Project Sit event
    VPetEvent([AnimationTransition('sit', secondsUntilFinished=10)], ["LiseProject"]),

    # Lise Project Warning event
    VPetEvent([AnimationTransition('warning', secondsUntilFinished=10)], ["LiseProject"]),

    # Lise Project Climb event
    VPetEvent([AnimationTransition('climb', secondsUntilFinished=10, WhileAnimation=VPetClimb, OnEnd=EndOfRopeJump)], ["LiseProject"]),

    # Lise Project Crouch Walk event
    VPetEvent(
        [AnimationTransition('idleToCrouch'),
         AnimationTransition("crouchWalk", secondsUntilFinished=10, WhileAnimation=VPetWalkRandomly),
         AnimationTransition("crouchToIdle")], ["LiseProject"]),
         
    # Lise Throw Bomb event
    VPetEvent([AnimationTransition('idle', OnStart=ThrowBomb)], ["LiseProject"])

    # walk to and eat from food bowl event
    # VPetEvent([
    #     AnimationTransition(GetCurrentAnimation=GetWalkAnimation, WhileAnimation=WalkToFoodBowl, IsFinished=ArrivedAtFoodBowl),
    #     AnimationTransition(animation='Idle', finishWithAnimation=True, IsFinished=FoodInBowlEaten)
    #     ])
]