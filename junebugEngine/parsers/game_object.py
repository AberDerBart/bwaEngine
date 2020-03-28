from ..game_object import Alignment
from ..physics import PHYSICS_SCALE
from ..game import anchorTo
from ..tileset import EntityData
from .properties import parseProperties
from ..sprite import AnimSprite
from ..text import RenderedText

# TODO: refactor to return the GameObject, not the sprite. this needs refactoring elsewhere
def parseGameObject(obj, gamemap, setDict):
    x = obj["x"]
    y = obj["y"]
    width = obj["width"]
    height = obj["height"]
    typeName = obj.get("type")
    objName = obj.get("name")
    size = (width, height)
    align = Alignment.TOPLEFT
    properties = parseProperties(obj.get('properties', {}), gamemap.path)

    # look up, if this is a tile object
    if "gid" in obj:
        # mask out vertical and horizontal flipping
        entityIndex = obj["gid"] & 0x0fffffff
        mirror_h = True if (obj["gid"] & 0x80000000) else False
        entityData = setDict.get(entityIndex)

        if entityData:
            align = Alignment.BOTTOMLEFT

            properties["mirror_h"] = mirror_h

            if not typeName:
                typeName = entityData.entityType

            for prop, value in entityData.properties.items():
                properties.setdefault(prop, value)

    if "polyline" in obj:
        polyline =  []
        for point in obj["polyline"]:
            px = point["x"] * PHYSICS_SCALE
            py = point["y"] * PHYSICS_SCALE
            polyline.append((px, py))
        properties["polyline"] = polyline

    generator = EntityData.generators.get(typeName)
    if generator:
        entity = generator(
            position=(x * PHYSICS_SCALE, y * PHYSICS_SCALE),
            size=size,
            align=align,
            world=gamemap,
            **properties)
        anchorTo(entity, gamemap)
        if objName:
            gamemap.namedEntities[objName] = entity
        if properties.get("player"):
            gamemap.player = entity
        return entity.sprite
    # if no type is given, but the parameter sprite is set,
    # generate the corresponding sprite
    elif properties.get("sprite"):
        sprite = AnimSprite(properties.get("sprite"), mirror_h=mirror_h)
        sprite.rect.bottomleft = (x, y)
        return sprite
    elif "text" in obj:
        return RenderedText((x, y), obj["text"])
    else:
        print("Failed to generate", typeName)
