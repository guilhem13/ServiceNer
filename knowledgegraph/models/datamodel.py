class DataPaper:

    """
    Data model witch represent a paper with its information found in its body
    """

    doi = None
    link = None
    entities_from_reference = None
    entities_include_in_text = None
    url_in_text = None
    doi_in_text = None

    def __init__(self, link):
        self.link = link
        self.doi = link.split("/")[-1]
