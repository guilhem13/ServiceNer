# from __future__ import absolute_import, division, print_function, unicode_literals


import logging
import os
from io import BytesIO
from urllib.request import Request, urlopen

import regex as re
from pdfminer.pdfparser import PDFSyntaxError

# from .extractor import extract_urls
from .backends import PDFMinerBackend
from .exceptions import FileNotFoundError, PDFInvalidError

unicode = str

logger = logging.getLogger(__name__)


class PDFx(object):

    # Available after init
    uri = None  # Original URI
    fn = None  # Filename part of URI
    is_url = False  # False if file
    is_pdf = True

    stream = None  # ByteIO Stream
    reader = None  # ReaderBackend
    summary = {}

    def __init__(self, uri):
        """
        Open PDF handle and parse PDF metadata
        - `uri` can bei either a filename or an url
        """
        logger.debug("Init with uri: %s" % uri)

        self.uri = uri

        # URL
        URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""  # noqa: E501

        def extract_urls(text):
            return set(re.findall(URL_REGEX, text, re.IGNORECASE))

        # Find out whether pdf is an URL or local file
        url = extract_urls(uri)
        self.is_url = len(url)

        # Grab content of reference
        if self.is_url:
            logger.debug("Reading url '%s'..." % uri)
            self.fn = uri.split("/")[-1]
            try:
                content = urlopen(Request(uri)).read()
                self.stream = BytesIO(content)
            except Exception as e:
                print("Pas bon ")
            """
            try:
                name = self.fn.replace(".pdf", "")
                with open(str("knowledgegraph/file/" + name + ".pdf"), "wb") as f:
                    f.write(content)
            except Exception as e:
                print("N'enregistre pas le fichier")"""

        else:
            if not os.path.isfile(uri):
                raise FileNotFoundError("Invalid filename and not an url: '%s'" % uri)
            self.fn = os.path.basename(uri)
            self.stream = open(uri, "rb")

        # Create ReaderBackend instance
        try:
            self.reader = PDFMinerBackend(self.stream)
        except PDFSyntaxError as e:
            raise PDFInvalidError("Invalid PDF (%s)" % unicode(e))
        except Exception as e:
            raise

    def get_text(self):
        return self.reader.get_text()

    def get_uri(self):
        return self.fn
