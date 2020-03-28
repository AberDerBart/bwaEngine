from pygame.rect import Rect

PHYSICS_SCALE = 1024

def resetPhysics(obj):
    obj.blocks = type(obj).blocks
    obj.gravity = type(obj).gravity
    obj.collides = type(obj).collides

def absVx(obj):
    if obj.anchor:
        return obj.vx + obj.anchor.absVx()
    else:
        return obj.vx

def absVy(obj):
    if obj.anchor:
        return obj.vy + obj.anchor.absVy()
    else:
        return obj.vy

def simulate_gravity(obj, ms):
    obj.vy = obj.vy + config.gravity * (ms / 1000.)

    if obj.vy >= config.max_vertical_speed / 1000.:
        obj.vy = config.max_vertical_speed / 1000.

def physicsX(obj, ms):

    lastTruncX = obj.truncate().x

    dx = obj.absDx(obj.vx * ms)

    if obj.collides:
        # collide with map in x direction
        collisionTiles = obj.world.tileRange(obj.move(dx, 0))

        for tile, tileRect in collisionTiles:
            if tile.collide:
                dx, dirX = obj.collideRectX(tileRect, dx, obj.collides)

                if dirX != Direction.NONE:
                    obj.on_collision(dirX, None)

    # collide with entities in x direction
    collision_list = obj.collisionCandidates(obj.union(obj.move(dx, 0)))

    for block in collision_list:
        dx, dirX = obj.collideRectX(block,
                                     dx,
                                     obj.blocks and block.blocks and obj.collides)
        if dirX != Direction.NONE:
            if obj.collides and block.collides:
                if block.collides:
                    obj.on_collision(dirX, block)
                    block.on_collision(dirX * -1, obj)

    obj.x += dx
    obj.truncDx = obj.truncate().x - lastTruncX

    obj.updateSpritePosition()
    obj.updateChunks()

    if not obj.colliderect(obj.world):
        if obj.top > obj.world.bottom:
            obj.on_map_exit(Direction.DOWN)
        elif obj.bottom < obj.world.top:
            obj.on_map_exit(Direction.UP)
        elif obj.left > obj.world.right:
            obj.on_map_exit(Direction.RIGHT)
        elif obj.right < obj.world.left:
            obj.on_map_exit(Direction.LEFT)

    for other in obj.anchored:
        other.physicsX(ms)

def physicsY(obj, ms):

    lastTruncY = obj.truncate().y

    dy = obj.absDy(obj.vy * ms)

    if obj.collides:
        # collide with map in y direction
        collisionTiles = obj.world.tileRange(obj.move(0, dy))

        for tile, tileRect in reversed(collisionTiles):
            if tile.collide:
                dy, dirY = obj.collideRectY(tileRect, dy, obj.collides)
                if dirY != Direction.NONE:
                    obj.on_collision(dirY, None)

    # collide with entities in y direction
    collision_list = obj.collisionCandidates(obj.union(obj.move(0, dy)))

    for block in collision_list:
        dy, dirY = obj.collideRectY(block,
                                     dy,
                                     obj.blocks and block.blocks and obj.collides)
        if dirY != Direction.NONE:
            if obj.collides and block.collides:
                    obj.on_collision(dirY, block)
                    block.on_collision(dirY * -1, obj)

    if not obj.on_ground:
        obj.anchorTo(obj.world)

    obj.y += dy
    obj.truncDy = obj.truncate().y - lastTruncY

    obj.updateSpritePosition()
    obj.updateChunks()

    if not obj.colliderect(obj.world):
        if obj.top > obj.world.bottom:
            obj.on_map_exit(Direction.DOWN)
        elif obj.bottom < obj.world.top:
            obj.on_map_exit(Direction.UP)
        elif obj.left > obj.world.right:
            obj.on_map_exit(Direction.RIGHT)
        elif obj.right < obj.world.left:
            obj.on_map_exit(Direction.LEFT)

    for other in obj.anchored:
        other.physicsY(ms)

def boundingBox(obj):
    return obj.unionall(obj.anchored)

def absDx(obj, dx=0):
    if obj.anchor:
        return obj.anchor.absDx(dx) + obj.anchor.truncDx
    else:
        return dx

def absDy(obj, dy=0):
    if obj.anchor:
        return obj.anchor.absDy(dy) + obj.anchor.truncDy
    else:
        return dy

def truncate(obj):
    x = obj.rect.x - obj.rect.x % PHYSICS_SCALE
    y = obj.rect.y - obj.rect.y % PHYSICS_SCALE
    w = obj.rect.w - obj.rect.w % PHYSICS_SCALE
    h = obj.rect.h - obj.rect.h % PHYSICS_SCALE
    return Rect(x, y, w, h)

def toPixel(obj):
    x = obj.rect.x // PHYSICS_SCALE
    y = obj.rect.y // PHYSICS_SCALE
    w = obj.rect.w // PHYSICS_SCALE
    h = obj.rect.h // PHYSICS_SCALE
    return Rect(x, y, w, h)
