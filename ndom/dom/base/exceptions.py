class AttributeExistsError(BaseException):
    pass

class MissingRequiredInstanceAttribute(Exception):
    pass

class RendererAlreadyRegistredError(Exception):
    pass