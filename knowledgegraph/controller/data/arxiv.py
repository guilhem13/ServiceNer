import arxiv
from knowledgegraph.models import Entity, Papier


class Data:

    count = 10

    def __init__(self, count):
        self.count = count

    def get_doi(self, entry_doi):
        doi = entry_doi.split("/")[-1]
        return doi

    def process_authors(self, list_authors):
        if len(list_authors) > 0:
            result = []
            for i in range(len(list_authors)):
                auteur = str(list_authors[i])
                seperate_name = auteur.split(" ")

                if (
                    len(seperate_name) > 2
                ):  # Prend en compte les noms du type David A. Strubbe
                    p = Entity()
                    p.set_prenom(" ".join(seperate_name[0:-1]).strip())
                    p.set_nom(seperate_name[-1].strip())
                    if len(p.nom) > 2:
                        p.set_name(p.nom + p.prenom)
                        result.append(p)
                else:
                    if len(seperate_name) > 1:  # cas normal nom prénom
                        p = Entity()
                        p.set_prenom(seperate_name[0].strip())
                        p.set_nom(seperate_name[1].strip())
                        if len(p.nom) > 2:
                            p.set_name(p.nom + p.prenom)
                            result.append(p)
                    else:
                        p = Entity()  # cas pas normal juste nom ou erreur
                        p.set_prenom("Nofirstname")
                        p.set_nom(seperate_name[0].strip())
                        p.set_name(p.nom + p.prenom)
                        if len(p.nom) > 2:
                            result.append(p)
            return result
        else:
            print("No authors on this paper")
            return None
