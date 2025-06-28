from dataclasses import dataclass

@dataclass
class PhysicsSettings:
    physicsUpdateRate : int
    gravity : float

    bottomPadding : int
    floorReleaseOffset : int
    velocitySmoothingInt : int

    throwForceMultiplier : int
    bouncinessConstant : float
    frictionConstant : float

# Physics simulation settings:
vpetPhysics = PhysicsSettings(
    physicsUpdateRate = 10,
    gravity = 9810,

    bottomPadding = 50,
    floorReleaseOffset = 250,
    velocitySmoothingInt = 10,

    throwForceMultiplier = 1,
    bouncinessConstant = 0.2,
    frictionConstant = 4
)

# physicsSettings = PhysicsSettings(
#     physicsUpdateRate = 1,
#     gravity = 9810,

#     bottomPadding = 100,
#     floorReleaseOffset = 250,
#     velocitySmoothingInt = 10,

#     throwForceMultiplier = 1,
#     bouncinessConstant = 0.2,
#     frictionConstant = 0.999
# )

deltaTime = vpetPhysics.physicsUpdateRate / 1000