from . import physics

def init(obj):
    for entity in obj.anchored:
        entity.init()

def setSprite(obj, sprite, spriteOffset=(0, 0)):
    obj.sprite = sprite
    obj.spriteOffset = spriteOffset
    updateSpritePosition(obj)

def anchorTo(obj, anchor):
    """anchors the GameObject to another GameObject -
    any movement of the anchor is copied to the object"""
    # if we lose the anchor, keep it for the children
    if anchor == obj.anchor:
        return

    if not anchor:
        for other in obj.anchored:
            other.anchorTo(obj.anchor)
    # exchange the anchor
    obj.vx = physics.absVx(obj)
    obj.vy = physics.absVy(obj)
    if obj.anchor:
        obj.anchor.anchored.remove(obj)
    obj.anchor = anchor
    if anchor:
        anchor.anchored.append(obj)
        obj.vx -= physics.absVx(anchor)
        obj.vy -= physics.absVy(anchor)

def on_map_exit(obj, direction):
    if direction == Direction.DOWN:
        kill(obj)

def kill(obj):
    obj.anchorTo(None)
    obj.updateChunks()
    if obj.sprite:
        obj.sprite.die()

def update(obj, ms, frameIndex):
    obj.frameIndex = frameIndex

    obj.on_ground = False
    if obj.gravity:
        simulate_gravity(obj, ms)

    for other in self.anchored:
        update(other, ms, frameIndex)

def updateChunks(obj):
    if obj.anchor:
        newChunks = obj.world.chunkRange(obj)
    else:
        newChunks = []

    for chunk in newChunks:
        if chunk not in obj.chunks:
            chunk.add(obj)

    for chunk in obj.chunks:
        if chunk not in newChunks:
            chunk.discard(obj)

    obj.chunks = newChunks

def updateSpritePosition(obj):
    if obj.sprite:
        obj.sprite.rect.topleft = physics.toPixel(obj).move(*obj.spriteOffset).topleft
        obj.sprite.orientation = obj.orientation
    for other in obj.anchored:
        updateSpritePosition(other)
