import re
import unicodedata
from knowledgegraph.controller.data.arxiv import Data
from knowledgegraph.models import Entity
from .pdfx import PDFx
from .undesirable_char import undesirable_char_replacements


class Textprocessed:
    url = None
    raw_text = None

    def __init__(self, url):
        self.url = url

    def get_references_part(self, Pdf_Readed):

        for bad_char, replacement in undesirable_char_replacements.items():
            Pdf_Readed = Pdf_Readed.replace(bad_char, replacement)
        result = ""
        try:
            temp = (
                unicodedata.normalize("NFKD", Pdf_Readed)
                .encode("ascii", "ignore")
                .decode("unicode_escape")
                .encode("ascii", "ignore")
                .decode()
            )
        except:
            temp = Pdf_Readed

        # TODO inclure
        """[u'references',u'r\u00C9f\u00E9rences',u'r\u00C9f\u00C9rences',u'r\xb4ef\xb4erences',u'bibliography',u'bibliographie',u'literaturverzeichnis',u'citations',u'refs',u'publications',u'r\u00E9fs',u'r\u00C9fs',u'reference',u'r\u00E9f\u00E9rence',u'r\u00C9f\u00C9rence']"""

        keyword_list = [
            "\n\nReferences\n\n",
            "\nReferences\n",
            "\nREFERENCES\n",
            "\nreferences\n",
            "REFERENCES",
            "References\n",
            "References",
        ]  # TODO voir les cas où c'est juste " Reference " exeple => https://arxiv.org/pdf/2202.03954v1.pdf
        forbidden_part = [
            "Appendices",
            "Appendix",
            "Supplementary Material",
            "Supplementary material",
        ]
        keyword = [ele for ele in keyword_list if (ele in temp)]
        if keyword != None:
            if len(keyword) == 1:
                keyword = str(keyword[0])
                indexstart = temp.index(
                    keyword
                )  # check ici parcequ'il y a plusieurs versions de références
                indexend = [temp[indexstart:].find(ele) for ele in forbidden_part]
                indexend = [ele for ele in indexend if ele != -1]
                result = (
                    temp[indexstart + len(keyword) : indexend[0]]
                    if len(indexend) > 0
                    else temp[indexstart + len(keyword) :]
                )
                return result
            else:
                if len(keyword) != 0:
                    index_keyword = [temp.index(ele) for ele in keyword]
                    delta = max(index_keyword) - min(index_keyword)
                    if delta < 14:
                        keyword = str(keyword[0])
                        indexstart = temp.index(
                            keyword
                        )  # check ici parcequ'il y a plusieurs versions de références
                        indexstartstring = temp[indexstart:]
                        indexend = [
                            indexstartstring.find(ele) for ele in forbidden_part
                        ]
                        indexend = [ele for ele in indexend if ele != -1]
                        result = (
                            temp[indexstart + len(keyword) : indexstart + indexend[0]]
                            if len(indexend) > 0
                            else temp[indexstart + len(keyword) :]
                        )
                        return result
                    else:  # cas où il y a plusieurs références dans le texte avec des formats diffférents
                        keyword = str(keyword[-1])
                        indexstart = temp.index(
                            keyword
                        )  # check ici parcequ'il y a plusieurs versions de références
                        indexstartstring = temp[indexstart:]
                        indexend = [
                            indexstartstring.find(ele) for ele in forbidden_part
                        ]
                        indexend = [ele for ele in indexend if ele != -1]
                        result = (
                            temp[indexstart + len(keyword) : indexstart + indexend[0]]
                            if len(indexend) > 0
                            else temp[indexstart + len(keyword) :]
                        )
                        return result
                else:
                    if temp.count("Reference") == 1:
                        indexstart = temp.index(
                            "Reference"
                        )  # check ici parcequ'il y a plusieurs versions de références
                        indexend = [
                            temp[indexstart:].find(ele) for ele in forbidden_part
                        ]
                        indexend = [ele for ele in indexend if ele != -1]
                        result = (
                            temp[indexstart + len(keyword) : indexend[0]]
                            if len(indexend) > 0
                            else temp[indexstart + len(keyword) :]
                        )
                        return result
                    else:
                        indexstart = temp.find("\nBibliography\n")
                        if indexstart != -1:
                            return temp[indexstart:]
                        else:
                            return temp

    def clean_references_part(self, data):
        temp = re.sub(" +", " ", data)
        temp = temp.replace("-\n", "")  # reconstruire les retours à la ligne
        temp = temp.replace("\n", " ")  # rajout d'espace
        return temp

    def find_entities_in_raw_text(self):

        named_re = re.compile(
            "(?:\(|\[)((?:[ a-zA-Z\.,\n-]+(?:\(|\[)*(?:19|20)[0-9]{2}(?:\)|\])*[; \n]*)+)(?:\)|\])"
        )
        result = named_re.findall(self.raw_text)
        return result

    def find_regex_style(self, regexstyle, text):
        regexp = re.compile(regexstyle)
        return regexp.findall(text)

    def check_doublon(self, listcorrect, listaverifier):
        for i in range(len(listaverifier)):
            for j in range(len(listcorrect)):
                if listaverifier[i] in listcorrect[j]:
                    listaverifier[i] = "TOREMOVE"
        listaverifier = [x for x in listaverifier if x != "TOREMOVE"]
        return listaverifier
    
    def filter_entities(self, entity):
        check_forbidden_word = False
        stop =False
        index = 0
        forbidden_list =['Analysis','Pattern','Recognition','Vision','Computer','Learning','Machine','Artificial','Intelligence','Computer','Science','Representation','Continuous','Facilities','Council','Dominican','Republic','Multiagent','Systems','Autonomous','Agents','Biometrics','Lab','Physics','Neural','Systems','Mathematics','Mathematical','Computational','Meta-Learning',"Parameter","Available","Online","Practical","Momentum","AGCN","AGCN","Engineering","Data","Retrieval","Programming","Research","Verification","Network"]
        while index < len(forbidden_list) or stop == False: 
            if entity.get_nom == forbidden_list[index]:
                check_forbidden_word = True
            if entity.get_prenom == forbidden_list[index]:
                check_forbidden_word = True
            if index ==len(forbidden_list)-1:
                stop = True
            index +=1
        return check_forbidden_word

    def get_format_ieee(
        self, text
    ):  # IEEE #liste of styles => https://dal.ca.libguides.com/csci/writing/examples

        Entitylist = []
        fithformat = self.find_regex_style(
            "[A-Z][a-z]+\s[a-zA-Z]\.\s[a-zA-Z]\.\s[a-zA-Z]+[,.]", text
        )  # James J. H. Little,
        fithformat2 = self.find_regex_style(
            "[A-Z][a-z]+\s[a-zA-Z]\.\s[a-zA-Z]\.\s[a-zA-Z]+\sand", text
        )  # James J. H. Little and
        fithformat = [x[:-1] for x in fithformat] if len(fithformat) > 0 else []
        fithformat2 = [x[:-4] for x in fithformat2] if len(fithformat2) > 0 else []
        Style_one = fithformat + fithformat2
        Style_one = list(set(Style_one))

        fourformat = self.find_regex_style(
            "[A-Z][a-z]+\s[a-zA-Z]\.\s[a-zA-Z]+[,.]", text
        )  # James J. Little,
        fourformat2 = self.find_regex_style(
            "[A-Z][a-z]+\s[a-zA-Z]\.\s[a-zA-Z]+\sand", text
        )  # James J. Little and
        fourformat3 = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z]\s[a-zA-Z]+[,.]", text
        )  # James J Little
        fourformat4 = self.find_regex_style(
            "[A-Z]\.\s[A-Z][a-z]+\s[A-Z][a-z]+[,.]", text
        )  # E. Mark Glod,
        fourformat = [x[:-1] for x in fourformat] if len(fourformat) > 0 else []
        fourformat2 = [x[:-4] for x in fourformat2] if len(fourformat2) > 0 else []
        fourformat3 = [x[:-1] for x in fourformat3] if len(fourformat3) > 0 else []
        fourformat4 = [x[:-1] for x in fourformat4] if len(fourformat4) > 0 else []
        Style_two = fourformat + fourformat2 + fourformat3 + fourformat4
        Style_two = list(set(Style_two))

        thirdformat = self.find_regex_style(
            "[A-Z]\. [A-Z]\.\s[A-Z]\.\s[a-zA-Z]+[,.]", text
        )  # J. F. P. Kooijffrr,
        thirdformat2 = self.find_regex_style(
            "[A-Z]\. [A-Z]\.\s[A-Z]\.\s[a-zA-Z]+\sand", text
        )  # J. F. P. Kooijffrr and
        thirdformat = [x[:-1] for x in thirdformat] if len(thirdformat) > 0 else []
        thirdformat2 = [x[:-4] for x in thirdformat2] if len(thirdformat2) > 0 else []
        Style_three = thirdformat + thirdformat2
        Style_three = list(set(Style_three))

        result = Style_one + Style_two + Style_three
        result = list(set(result))

        specific_format_german = self.find_regex_style(
            "[A-Z][a-z]+\svan\s[A-Z][a-z]+", text
        )  # Prenom van Zantman
        specifc_format_exception = self.find_regex_style(
            "and\s[A-Z][a-z]+\s[A-Z][a-z]+[,.]", text
        )  # and Romain Gernett, ou .
        specifc_format_exception = (
            [x[3:-1] for x in specifc_format_exception]
            if len(specifc_format_exception) > 0
            else []
        )
        # TODO A voir car ils sont à l'origine de pleins de problème
        specific_format_exception2 = self.find_regex_style(
            "[A-Z][a-z]+-[A-Z][a-z]+\s[A-Z][a-z]+[,.]", text
        )  # Minh-Thong Luang
        specific_format_exception2 = (
            [x[3:-1] for x in specific_format_exception2]
            if len(specific_format_exception2) > 0
            else []
        )
        specific_format_exception3 = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-z]+-[A-Z][a-z]+[,.]", text
        )  # Luang Minh-Thong
        specific_format_exception3 = (
            [x[3:-1] for x in specific_format_exception3]
            if len(specific_format_exception3) > 0
            else []
        )
        result += specific_format_german
        result += specifc_format_exception
        result += specific_format_exception2
        result += specific_format_exception3
        result = list(set(result))

        firstformat = self.find_regex_style("[A-Z]\. [a-zA-Z]+[,.]", text)  # E. Behjat
        firstformat2 = self.find_regex_style(
            "[A-Z]\. [a-zA-Z]+\sand", text
        )  # E. Behjat and
        firstformat = [x[:-1] for x in firstformat] if len(firstformat) > 0 else []
        firstformat2 = [x[:-4] for x in firstformat2] if len(firstformat2) > 0 else []
        firstformat = firstformat + firstformat2
        firstformat = list(set(firstformat))

        secondformat = self.find_regex_style(
            "[A-Z]\.\s+[A-Z]\. [a-zA-Z]+[,.]", text
        )  #  B. K. Jang
        secondformat2 = self.find_regex_style(
            "[A-Z]\.\s+[A-Z]\. [a-zA-Z]+\sand", text
        )  # B. K. Jang  and
        secondformat2 = (
            [x[:-4] for x in secondformat2] if len(secondformat2) > 0 else []
        )
        secondformat = [x[:-1] for x in secondformat] if len(secondformat) > 0 else []
        secondformat = secondformat + secondformat2
        secondformat = list(set(secondformat))

        if len(secondformat) > 0:
            if len(result) > 0:
                secondformat = self.check_doublon(result, secondformat)
            secondformat = list(set(secondformat))
            result = result + secondformat

        if len(firstformat) > 0:
            if len(result) > 0:
                firstformat = self.check_doublon(result, firstformat)
            firstformat = list(set(firstformat))
            result = result + firstformat

        result_full_name = self.get_format_full_name(result, text)
        if len(result_full_name) > 0:
            result = result_full_name
        result_full_name2 = self.get_format_full_name_two(result, text)
        if len(result_full_name2) > 0:
            result = result_full_name2

        if len(result) > 0:
            regex_remove = re.compile("^[A-Z]\. [A-Z]\.$")
            regex_remove2 = re.compile("^[A-Z]\. [A-Z]$")
            result = [x for x in result if regex_remove.match(x) == None]  # remove "A. R "  part
            result = [x for x in result if regex_remove2.match(x) == None]
            result = Data(1).process_authors(result)
            result =[x for x in result if self.filter_entities(x)==False] #filter wrong found based on a specific format guilhem maillebuau, and pettter brown 
            Entitylist.extend(result)
        else:
            # print("liste nulle")
            pass
        return Entitylist

    def get_format_full_name(self, listofreference, text):  # ACM

        result = listofreference
        thirteenformat = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\sand\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+",
            text,
        )  # 7 noms + and
        if len(thirteenformat) > 0:
            newsevenformat = []
            for item in thirteenformat:
                temp = item.split(", ")
                newsevenformat.append(temp[0])
                newsevenformat.append(temp[1])
                newsevenformat.append(temp[2])
                newsevenformat.append(temp[3])
                newsevenformat.append(temp[4])
                newsevenformat.append(temp[5])
                newsevenformat.append(temp[6])
                newsevenformat.append(temp[7][4:])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        twelveformat = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\sand\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+",
            text,
        )  # 6 noms + and
        if len(twelveformat) > 0:
            newsevenformat = []
            for item in twelveformat:
                temp = item.split(", ")
                newsevenformat.append(temp[0])
                newsevenformat.append(temp[1])
                newsevenformat.append(temp[2])
                newsevenformat.append(temp[3])
                newsevenformat.append(temp[4])
                newsevenformat.append(temp[5])
                newsevenformat.append(temp[6][4:])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        tenformat = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\sand\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+",
            text,
        )  # 5 noms + and
        if len(tenformat) > 0:
            newsevenformat = []
            for item in tenformat:
                temp = item.split(", ")
                newsevenformat.append(temp[0])
                newsevenformat.append(temp[1])
                newsevenformat.append(temp[2])
                newsevenformat.append(temp[3])
                newsevenformat.append(temp[4])
                newsevenformat.append(temp[5][4:])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        eightformat = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\sand\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+",
            text,
        )  # 4 noms + and
        if len(eightformat) > 0:
            newsevenformat = []
            for item in eightformat:
                temp = item.split(", ")
                newsevenformat.append(temp[0])
                newsevenformat.append(temp[1])
                newsevenformat.append(temp[2])
                newsevenformat.append(temp[3])
                newsevenformat.append(temp[4][4:])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        nineformat = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\sand\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+",
            text,
        )  # 3 noms + and
        if len(nineformat) > 0:
            newsevenformat = []
            for item in nineformat:
                temp = item.split(", ")
                newsevenformat.append(temp[0])
                newsevenformat.append(temp[1])
                newsevenformat.append(temp[2])
                newsevenformat.append(temp[3][4:])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        sevenformat = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\sand\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+",
            text,
        )  # Alan Akbik, Duncan Blythe, and Roland Vollgraf
        if len(sevenformat) > 0:
            newsevenformat = []
            for item in sevenformat:
                temp = item.split(", ")
                newsevenformat.append(temp[0])
                newsevenformat.append(temp[1])
                newsevenformat.append(temp[2][4:])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        elevenformat = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-zA-Z]+\sand\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+[,.]", text
        )  # Duncan Blythe and Roland Vollgraf,
        if len(elevenformat) > 0:
            newsevenformat = []
            for item in elevenformat:
                temp = item.split(" and ")
                newsevenformat.append(temp[0])
                newsevenformat.append(temp[1][:-1])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        fifteenformat = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+[,.]",
            text,
        )  # Duncan Blythe, Roland Vollgraf, guilhem maillebuau
        if len(fifteenformat) > 0:
            newsevenformat = []
            for item in fifteenformat:
                temp = item.split(", ")
                newsevenformat.append(temp[0])
                newsevenformat.append(temp[1])
                newsevenformat.append(temp[2][:-1])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        ########################################### Exception ############################################################################################

        e1 = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-zA-Z]+,\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+[,.]", text
        )  # Orial Vinyals, and Jeffery Deano.
        if len(e1) > 0:
            newsevenformat = []
            for item in e1:
                temp = item.split(", ")
                newsevenformat.append(temp[0])
                newsevenformat.append(temp[1][:-1])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        e2 = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-z]+,\s[A-Z]\.\s[A-Z][a-z]+[,.]", text
        )  # Guilhem Maillebuau, T. Bennanine, pour choper guilhem maillebuau dans le cas d'une exception  impaire
        e3 = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-z]+,\s[A-Z][a-z]+\s[A-Z]\.\s[A-Z][a-z]+[,.]", text
        )  ##Guilhem Maillebuau, james T. Bennanine, pour choper guilhem maillebuau dans le cas d'une exception  impaire
        e4 = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-z]+,\sand\s[A-Z][a-z]+\s[A-Z]\.\s[A-Z][a-z]+", text
        )  # Guilhem Maillebuau, and James T. Bennanine pour choper guilhem maillebuau dans le cas d'une exception  impaire
        e5 = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-z]+,\sand\s[A-Z]\.\s[A-Z][a-z]+", text
        )  # Guilhem Maillebuau, and T. Bennanine , pour choper guilhem maillebuau dans le cas d'une exception  impaire
        exceptionlist = e2 + e3 + e4 + e5
        if len(exceptionlist) > 0:
            newsevenformat = []
            for item in exceptionlist:
                temp = item.split(", ")
                newsevenformat.append(temp[0])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        return result

    def get_format_full_name_two(self, listofreference, text):  # ACM 2
        result = listofreference
        # Entitylist =[]
        tenformat = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-zA-Z]+,[A-Z][a-z]+\s[A-Z][a-zA-Z]+,[A-Z][a-z]+\s[A-Z][a-zA-Z]+,[A-Z][a-z]+\s[A-Z][a-zA-Z]+,[A-Z][a-z]+\s[A-Z][a-zA-Z]+,and\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+",
            text,
        )  # 5 noms + and
        if len(tenformat) > 0:
            newsevenformat = []
            for item in tenformat:
                temp = item.split(", ")
                newsevenformat.append(temp[0])
                newsevenformat.append(temp[1])
                newsevenformat.append(temp[2])
                newsevenformat.append(temp[3])
                newsevenformat.append(temp[4])
                newsevenformat.append(temp[5][4:])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        eightformat = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-zA-Z]+,[A-Z][a-z]+\s[A-Z][a-zA-Z]+,[A-Z][a-z]+\s[A-Z][a-zA-Z]+,[A-Z][a-z]+\s[A-Z][a-zA-Z]+,and\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+",
            text,
        )  # 4 noms + and
        if len(eightformat) > 0:
            newsevenformat = []
            for item in eightformat:
                temp = item.split(", ")
                newsevenformat.append(temp[0])
                newsevenformat.append(temp[1])
                newsevenformat.append(temp[2])
                newsevenformat.append(temp[3])
                newsevenformat.append(temp[4][4:])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        nineformat = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-zA-Z]+,[A-Z][a-z]+\s[A-Z][a-zA-Z]+,[A-Z][a-z]+\s[A-Z][a-zA-Z]+,and\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+",
            text,
        )  # 3 noms + and
        if len(nineformat) > 0:
            newsevenformat = []
            for item in nineformat:
                temp = item.split(", ")
                newsevenformat.append(temp[0])
                newsevenformat.append(temp[1])
                newsevenformat.append(temp[2])
                newsevenformat.append(temp[3][4:])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        sevenformat = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-zA-Z]+,[A-Z][a-z]+\s[A-Z][a-zA-Z]+,and\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+",
            text,
        )  # Alan Akbik, Duncan Blythe, and Roland Vollgraf
        if len(sevenformat) > 0:
            newsevenformat = []
            for item in sevenformat:
                temp = item.split(", ")
                newsevenformat.append(temp[0])
                newsevenformat.append(temp[1])
                newsevenformat.append(temp[2][4:])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        elevenformat = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-zA-Z]+\sand\s[A-Z][a-z]+\s[A-Z][a-zA-Z]+[,.]", text
        )  # Duncan Blythe and Roland Vollgraf,
        if len(elevenformat) > 0:
            newsevenformat = []
            for item in elevenformat:
                temp = item.split(" and ")
                newsevenformat.append(temp[0])
                newsevenformat.append(temp[1][:-1])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        fourteen = self.find_regex_style(
            "[A-Z][a-z]+\s[A-Z][a-z]+,\sand\s[A-Z][a-z]+\s[A-Z][a-z]+[,.]", text
        )  # Orial Vinyals, and Jeffrey Deans
        if len(fourteen) > 0:
            newsevenformat = []
            for item in fourteen:
                temp = item.split(", and ")
                newsevenformat.append(temp[0])
                newsevenformat.append(temp[1][:-1])
            if len(result) > 0:
                newsevenformat = self.check_doublon(result, newsevenformat)
            newsevenformat = list(set(newsevenformat))
            result = result + newsevenformat

        if len(result) > 0:
            regex_remove = re.compile("^[A-Z]\. [A-Z]\.$")
            regex_remove2 = re.compile("^[A-Z]\. [A-Z]$")
            result = [x for x in result if regex_remove.match(x) == None]  # remove "A. R "  part
            result = [x for x in result if regex_remove2.match(x) == None]
        else:
            pass
        return result

    def get_format_apa(self, text):  # APA style ,
        result = []
        result2 = []
        Entitylist = []

        template_one = self.find_regex_style(
            "[A-Z][a-z]+,\s[A-Z]\.\s[A-Z]\.\s[A-Z]\.", text
        )  # Johnson, D. D. P.
        template_two = self.find_regex_style(
            "[A-Z][a-z]+,\s[A-Z]\.\s[A-Z]\.", text
        )  # Johnson, D. D.
        template_three = self.find_regex_style(
            "[A-Z][a-z]+,\s[A-Z]\.", text
        )  # Johnson, D.

        if len(template_one) > 0:
            result += template_one
        if len(template_two) > 0:
            if len(result) > 0:
                template_two = self.check_doublon(result, template_two)
                template_two = list(set(template_two))
                result = result + template_two
            else:
                result += template_two

        if len(template_three) > 0:
            if len(result) > 0:
                template_three = self.check_doublon(result, template_three)
                template_three = list(set(template_three))
                result = result + template_three
            else:
                result += template_three

        template_four = self.find_regex_style(
            "[A-Z][a-z]+,\s[A-Z]\.[A-Z]\.[A-Z]\.", text
        )  # Johnson, D.D.P.
        template_five = self.find_regex_style(
            "[A-Z][a-z]+,\s[A-Z]\.[A-Z]\.", text
        )  # Johnson, D.D.
        template_six = self.find_regex_style(
            "[A-Z][a-z]+,\s[A-Z]\.", text
        )  # Johnson, D.

        if len(template_four) > 0:
            result += template_four
        if len(template_five) > 0:
            if len(result) > 0:
                template_five = self.check_doublon(result, template_five)
                template_five = list(set(template_five))
                result = result + template_five
            else:
                result += template_four

        if len(template_six) > 0:
            if len(result) > 0:
                template_six = self.check_doublon(result, template_six)
                template_six = list(set(template_six))
                result = result + template_six
            else:
                result += template_six

        if len(result) > 0:
            for item in result:
                temp = item.split(",")
                p = Entity()
                p.set_prenom(temp[1].strip())
                p.set_nom(temp[0].strip())
                p.set_name(str(temp[0].strip() + temp[1].strip()))
                if self.filter_entities(p) == False: 
                    Entitylist.append(p)

        index_end_apa = len(result) - 1
        result_full_name = self.get_format_full_name(result, text)
        result_full_name2 = self.get_format_full_name_two(result, text)
        if len(result_full_name) > 0:
            result2 += result_full_name
        if len(result_full_name2) > 0:
            result2 += result_full_name2
        if len(result2) > 0:
            result2 = Data(1).process_authors(result2[index_end_apa:])
            Entitylist.extend(result2)

        return Entitylist

    def find_entites_based_on_regex(self, text):
        final_entity_list = []
        check_apa_style = self.find_regex_style(
            "[A-Z][a-z]+,\s[A-Z]\.+[,;]\s[A-Z][a-z]+,\s[A-Z]\.", text
        )
        if len(check_apa_style) > 0:
            result_second_format = self.get_format_apa(text)
            print("inside APA")
            # result_format_full_name = self.get_format_full_name(text)
            # result_format_full_name_two = self.get_format_full_name_two(text)
            final_entity_list = result_second_format  # result_format_full_name + result_format_full_name_two + result_second_format
        else:
            result_format_ieee = self.get_format_ieee(text)
            print("inside IEEE")
            # result_format_full_name = self.get_format_full_name(text)
            # result_format_full_name_two = self.get_format_full_name_two(text)
            final_entity_list = result_format_ieee  # + result_format_full_name + result_format_full_name_two

        if len(final_entity_list) == 0:  # TODO gérer le cas où ya pas de nom et prenom
            p = Entity()
            p.set_prenom("guilhem")
            p.set_nom("maillebuau")
            p.set_name("guilhemaillebuau")
            final_entity_list.append(p)

        # listevide =[]
        return final_entity_list

    def find_url_in_text(self):
        url_regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""  # noqa: E501
        res = re.findall(url_regex, self.raw_text, re.IGNORECASE)
        return list(dict.fromkeys([r.strip(".") for r in res]))

    def find_doi_in_text(self):
        arxiv_regex = r"""arxiv:\s?([^\s,]+)"""
        arxiv_regex2 = r"""arxiv.org/abs/([^\s,]+)"""
        doi_regex = r"""DOI:\s?([^\s,]+)"""
        res = set(
            re.findall(doi_regex, self.raw_text, re.IGNORECASE)
            + re.findall(arxiv_regex, self.raw_text, re.IGNORECASE)
            + re.findall(arxiv_regex2, self.raw_text, re.IGNORECASE)
        )
        return list(dict.fromkeys([r.strip(".") for r in res]))

    def get_data_from_pdf(self):

        pdf = PDFx(self.url)
        textfrompdf = pdf.get_text()
        self.raw_text = textfrompdf
        textfrompdf = self.clean_references_part(self.get_references_part(textfrompdf))
        return textfrompdf

    def get_data_from_file(self, file_localisation):
        pdf = PDFx(file_localisation)
        textfrompdf = pdf.get_text()
        textfrompdf = self.clean_references_part(self.get_references_part(textfrompdf))
        return textfrompdf

    def __getattr__(self):
        return self.raw_text
