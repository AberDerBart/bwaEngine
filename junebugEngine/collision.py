def collisionCandidates(obj, rect, _branch=None):
    candidates = []
    for chunk in obj.world.chunkRange(rect):
        for other in chunk:
            if other not in candidates and other != obj:
                candidates.append(other)
    return candidates

    if _branch:
        for c in obj.anchored:
            if c != _branch:
                candidates += [c]
                candidates += c.collisionCandidates(rect, obj)
    if obj.anchor is not None and _branch != obj.anchor:
        candidates.append(obj.anchor)
        candidates += obj.anchor.collisionCandidates(rect, obj)

    return candidates

def collideRectX(obj, other, dx, block=True):
    collisionRect = obj.move(dx, 0)
    collision = collisionRect.colliderect(other)

    dirX = Direction.NONE

    if collision:
        if other.centerx > obj.centerx:
            dirX = Direction.RIGHT
            if block:
                obj.vx = 0
                dx = other.left - obj.right
        else:
            dirX = Direction.LEFT
            if block:
                obj.vx = 0
                dx = other.right - obj.left
    return dx, dirX

def collideRectY(obj, other, dy, block=True):
    collisionRect = obj.move(0, dy)
    collision = collisionRect.colliderect(other)

    dirY = Direction.NONE

    if collision:
        if other.centery > obj.centery:
            dirY = Direction.DOWN
            if block:
                obj.vy = 0
                dy = other.top - obj.bottom
        else:
            dirY = Direction.UP
            if block:
                obj.vy = 0
                dy = other.bottom - obj.top
    return dy, dirY

def on_collision(obj, direction, other=None):
    if direction == Direction.DOWN:
        if not other:
            obj.on_ground = True
            obj.anchorTo(self.world)
        elif other.blocks and obj.blocks:
            obj.on_ground = True
            obj.anchorTo(other)
