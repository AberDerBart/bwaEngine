

class Feature:
    name = "feature";

    onUpdate = None
    onDeath = None

    def __init__(self):
        pass

    def onAdd(self,obj):
        pass

    def onRemove(self,obj):
        pass

    def onControl(self,obj, control):
        pass

    def onUpdate(self,obj,ms):
        pass

    def onDeath(self,obj):
        pass

    def onCollision(self,obj, other, direction):
        pass
