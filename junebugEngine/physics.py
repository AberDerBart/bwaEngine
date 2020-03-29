from pygame.rect import Rect
from . import config, collision, game
from .game import Direction

PHYSICS_SCALE = 1024

def resetPhysics(obj):
    obj.blocks = type(obj).blocks
    obj.gravity = type(obj).gravity
    obj.collides = type(obj).collides

def absVx(obj):
    if obj.anchor:
        return obj.vx + absVx(obj.anchor)
    else:
        return obj.vx

def absVy(obj):
    if obj.anchor:
        return obj.vy + absVy(obj.anchor)
    else:
        return obj.vy

def simulate_gravity(obj, ms):
    obj.vy = obj.vy + config.gravity * (ms / 1000.)

    if obj.vy >= config.max_vertical_speed / 1000.:
        obj.vy = config.max_vertical_speed / 1000.

def physicsX(obj, ms):

    lastTruncX = truncate(obj).x

    dx = absDx(obj, obj.vx * ms)

    if obj.collides:
        # collide with map in x direction
        collisionTiles = obj.world.tileRange(obj.rect.move(dx, 0))

        for tile, tileRect in collisionTiles:
            if tile.collide:
                dx, dirX = obj.collideRectX(tileRect, dx, obj.collides)

                if dirX != Direction.NONE:
                    obj.on_collision(dirX, None)

    # collide with entities in x direction
    collision_list = collision.collisionCandidates(obj, obj.rect.union(obj.rect.move(dx, 0)))

    for block in collision_list:
        dx, dirX = obj.collideRectX(block,
                                     dx,
                                     obj.blocks and block.blocks and obj.collides)
        if dirX != Direction.NONE:
            if obj.collides and block.collides:
                if block.collides:
                    obj.on_collision(dirX, block)
                    block.on_collision(dirX * -1, obj)

    obj.rect.x += dx
    obj.truncDx = truncate(obj).x - lastTruncX

    game.updateSpritePosition(obj)
    game.updateChunks(obj)

    if not obj.rect.colliderect(obj.world):
        if obj.rect.top > obj.world.rect.bottom:
            game.on_map_exit(obj, Direction.DOWN)
        elif obj.rect.bottom < obj.world.rect.top:
            game.on_map_exit(obj, Direction.UP)
        elif obj.rect.left > obj.world.rect.right:
            game.on_map_exit(obj, Direction.RIGHT)
        elif obj.rect.right < obj.world.rect.left:
            game.on_map_exit(obj, Direction.LEFT)

    for other in obj.anchored:
        other.physicsX(ms)

def physicsY(obj, ms):

    lastTruncY = truncate(obj).y

    dy = absDy(obj, obj.vy * ms)

    if obj.collides:
        # collide with map in y direction
        collisionTiles = obj.world.tileRange(obj.rect.move(0, dy))

        for tile, tileRect in reversed(collisionTiles):
            if tile.collide:
                dy, dirY = collision.collideRectY(obj, tileRect, dy, obj.collides)
                if dirY != Direction.NONE:
                    collision.on_collision(obj, dirY, None)

    # collide with entities in y direction
    collision_list = collision.collisionCandidates(obj, obj.rect.union(obj.rect.move(0, dy)))

    for block in collision_list:
        dy, dirY = collision.collideRectY(obj,
                                          block,
                                          dy,
                                          obj.blocks and block.blocks and obj.collides)
        if dirY != Direction.NONE:
            if obj.collides and block.collides:
                    obj.on_collision(dirY, block)
                    block.on_collision(dirY * -1, obj)

    if not obj.on_ground:
        game.anchorTo(obj, obj.world)

    obj.rect.y += dy
    obj.truncDy = truncate(obj).y - lastTruncY

    game.updateSpritePosition(obj)
    game.updateChunks(obj)

    if not obj.rect.colliderect(obj.world):
        if obj.rect.top > obj.world.rect.bottom:
            game.on_map_exit(obj, Direction.DOWN)
        elif obj.rect.bottom < obj.world.rect.top:
            game.on_map_exit(obj, Direction.UP)
        elif obj.rect.left > obj.world.rect.right:
            game.on_map_exit(obj, Direction.RIGHT)
        elif obj.rect.right < obj.world.rect.left:
            game.on_map_exit(obj, Direction.LEFT)

    for other in obj.anchored:
        other.physicsY(ms)

def boundingBox(obj):
    return obj.rect.unionall(obj.anchored)

def absDx(obj, dx=0):
    if obj.anchor:
        return absDx(obj.anchor, dx) + obj.anchor.truncDx
    else:
        return dx

def absDy(obj, dy=0):
    if obj.anchor:
        return absDy(obj.anchor, dy) + obj.anchor.truncDy
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
