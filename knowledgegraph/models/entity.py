class Entity:

    prenom = (None,)
    nom = None
    name = (
        None,
    )  

    def __init__(self):

        pass

    # setter method
    def set_prenom(self, x):
        self.prenom = x

    def set_nom(self, x):
        self.nom = x

    def set_name(self, x):
        self.name = x
    
    def get_prenom(self):
        return self.prenom

    def get_nom(self):
        return self.nom

    def __eq__(self, other):
        equals = False
        if not isinstance(other, Entity):
            return NotImplemented
        if self.nom == other.nom:
            equals = True

        return equals
