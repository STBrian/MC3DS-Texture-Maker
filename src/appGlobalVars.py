class appGlobalVars:
    def __init__(self, allowed_attributes: list[tuple]):
        self.__dict__["allowed_attributes"] = [element[0] for element in allowed_attributes]
        self.__dict__["allowed_attributes_types"] = [element[1] for element in allowed_attributes]

    def __setattr__(self, name, value):
        if name in self.allowed_attributes:
            if isinstance(value, self.allowed_attributes_types[self.allowed_attributes.index(name)]):
                self.__dict__[name] = value
            else:
                raise TypeError(f"{name} attribute must be type {self.allowed_attributes_types[self.allowed_attributes.index(name)]} not {type(value)}")
        else:
            raise AttributeError(f"{name} is not a valid member for this instance")