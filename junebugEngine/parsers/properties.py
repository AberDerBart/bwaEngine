from junebugEngine.util import relativePath

def parseProperties(propertyData, path):
    properties = {}
    for prop in propertyData:
        if prop.get("type") == "file":
            properties[prop["name"]] = relativePath(prop["value"], path)
        else:
            properties[prop["name"]] = prop["value"]
    
    return properties
