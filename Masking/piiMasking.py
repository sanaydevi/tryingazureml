import pandas as pd
import xlrd
from openpyxl import Workbook
import re, Masking.database as db
import Masking
import os
import time
from pathlib import Path

def piiMask(filePath):
    AutoRedact(filePath)

class AutoRedact:
    # def __init__(self,filePath):
    #     print("starting...")
    #     xls = xlrd.open_workbook(filePath, on_demand=True)
    #     self.sheetnames = xls.sheet_names()
    #     self.location = pd.ExcelFile(filePath)
    #     for sheet in self.sheetnames:
    #         if sheet in Main.sheetToEliminate:
    #             continue
    #         self.sheetname = sheet
    #         self.arrOfColumns = []
    #         for val in Main.columns:
    #             self.arrOfColumns.append(str(val))
    #         print(str(sheet))
    #         self.x = pd.read_excel(self.location, str(sheet))
    #         self.readFile()

    def readFile(self,filePath,fileName):
        print("Starting ....")
        data = pd.read_csv(filePath,sep='\t', header=None)
        self.df = pd.DataFrame(data)
        print(self.df)


        self.redactdf = pd.DataFrame(columns=["Redacted Words"])
        self.df.dropna()

        # for col in self.arrOfColumns:
        #     print("redacting"+col)
        for ind, row2 in self.df.iterrows():

            self.listofredactedwords = []
            self.index_row = ind
            sentence = str(row2[0])
            print(sentence)
            arrofWords = sentence.split()
            print(arrofWords)
            redactNameSentence = self.extractName(AutoRedact,arrofWords)
            otherrequiredSentence = self.redactOthers(AutoRedact,redactNameSentence)
            redactedEmail = self.extractEmail(AutoRedact,otherrequiredSentence)
            finalRedactedSentence = self.redactingSSN(AutoRedact,redactedEmail)
            finalAddRedactedSentence = self.check_address(AutoRedact,finalRedactedSentence)
            finalNumRedactedSentence = self.checkNumber(AutoRedact,finalAddRedactedSentence)
            finalSentence = " ".join(finalNumRedactedSentence)
            print(finalSentence)
            self.df.at[ind,0]=finalSentence
            self.redactdf.at[ind, 'Redacted Words'] = "".join(self.listofredactedwords)

        # filePath = Main.destination_folder + os.sep + self.sheetname + "_PIIRedactedFile.xlsx"
        # if os.path.exists(filePath):
        #     timestr = time.strftime("%Y%m%d-%H%M%S")
        #     newName = Main.destination_folder + os.sep + self.sheetname + "_PIIRedactedFile_" + timestr + '_.xlsx'
        #     filePath = os.path.join(Path().absolute(), newName)
        #
        # filePath_redaction = Main.destination_folder + os.sep + self.sheetname + "_PIIRedactedWords.xlsx"
        # if os.path.exists(filePath_redaction):
        #     timestr = time.strftime("%Y%m%d-%H%M%S")
        #     newName = Main.destination_folder + os.sep + self.sheetname + "_PIIRedactedWords_" + timestr + '_.xlsx'
        #     filePath = os.path.join(Path().absolute(), newName)

            # uncomment bellow 
        # print("Creating new sheet......")
        self.df.to_csv("../emailFolder/masked/masked"+fileName)
        self.redactdf.to_csv("../emailFolder/masked/maskedanalysis"+fileName)

    def createHonorifics(self, setOfH):
        for x in setOfH:
            if str(x).lower() not in setOfH:
                setOfH.add(str(x).lower())
            elif str(x).upper() not in setOfH:
                setOfH.add(str(x).upper())
            elif not str(x).endswith("."):
                setOfH.add(str(x) + ".")

    def checkForPrefix(self, arrayOfWords) -> set:
        listOfPrefix = set()
        # print("Checking Prefix......") 
        for word in arrayOfWords:
            if word in db.honorifics:
                listOfPrefix.add(str(word))
        return listOfPrefix

    def add_punc(self, name_to_punc):
        if (name_to_punc.endswith(".")):
            return [".", name_to_punc[:-1]]
        elif name_to_punc.endswith(","):
            return [",", name_to_punc[:-1]]
        elif (name_to_punc.endswith(";")):
            return [";", name_to_punc[:-1]]
        else:
            return ["", name_to_punc]

            # extracting names by separating honorifics and punctuation 

    def extractName(self, arrayOfWords) -> list:
        names = set()
        # print("Extracting Name......") 
        for i, name in enumerate(arrayOfWords):
            if str(name).lower() in db.honorifics and i != len(arrayOfWords) - 1:
                xx = self.add_punc(str(arrayOfWords[i + 1]))
                pre_fix = xx[0]
                new_name = xx[1]
                names.add(new_name)
                arrayOfWords[i + 1] = self.redaction(new_name) + pre_fix
            elif name in names:
                arrayOfWords[i] = self.redaction(name)
            elif str(name).lower() in db.names:
                arrayOfWords[i] = self.redaction(name)
        return arrayOfWords

    def checkNumber(self, arrayWords) -> list:
        for i, digi in enumerate(arrayWords):
            if str(digi[0]) == "$":
                continue
            elif len(digi) < 3:
                continue
            elif str(digi).isdigit():
                arrayWords[i] = self.redaction(AutoRedact,digi)
            elif str(digi[:3]).isdigit():
                newStr = ""
                for index, eachDig in enumerate(digi):
                    if str(eachDig).isdigit():
                        newStr = newStr + "X"
                    else:
                        newStr = newStr + eachDig
                arrayWords[i] = newStr
        return arrayWords

    def extractName2(self, arrayOfWords) -> list:
        names = set()
        # print("Extracting Name......") 
        for i, name in enumerate(arrayOfWords):
            if (str(name).lower() == "member" or str(name).lower() == "MBR" or str(name).lower() == "account" or str(
                    name).lower() == "acct") and i + 1 != len(arrayOfWords) and str(
                    arrayOfWords[i + 1]).lower() == "number" and i + 2 != len(arrayOfWords):
                if len(arrayOfWords[i + 2]) == 1 and arrayOfWords[i + 2] == "#":
                    if i + 3 != len(arrayOfWords):
                        arrayOfWords[i + 3] = self.redaction(arrayOfWords[i + 3])
                else:
                    arrayOfWords[i + 2] = self.redaction(arrayOfWords[i + 2])

            elif (str(name).lower() == "mbr" or str(name).lower() == "acct") and i + 1 != len(arrayOfWords):
                if len(arrayOfWords[i + 1]) == 1 and arrayOfWords[i + 1] == "#":
                    if i + 2 != len(arrayOfWords):
                        arrayOfWords[i + 2] = self.redaction(arrayOfWords[i + 2])
                else:
                    arrayOfWords[i + 1] = self.redaction(arrayOfWords[i + 1])
        return arrayOfWords

        # if str(name).lower() in db.honorifics2 and i != len(arrayOfWords) - 1: 
        #     xx = self.add_punc(str(arrayOfWords[i + 1])) 
        #     pre_fix = xx[0] 
        #     new_name = xx[1] 
        #     names.add(new_name) 
        #     if len(arrayOfWords[i+1]) == 1 and len(arrayOfWords[i+1]) == "#": 
        #         if 
        #     arrayOfWords[i + 1] = self.redaction(new_name) + pre_fix 
        # elif name in names: 
        #     arrayOfWords[i] = self.redaction(name) 

    def redactOthers(self, redactNameSentence):

        for i, name in enumerate(redactNameSentence):
            xx = self.add_punc(AutoRedact,name)
            pre_fix = xx[0]
            new_name = xx[1]
            if str(new_name).lower() in db.other_required:
                redactNameSentence[i] = self.redaction(AutoRedact,new_name) + pre_fix

        return redactNameSentence

    def redaction(self, stringToRedact):
        if len(stringToRedact) == 0:
            return stringToRedact
        elif stringToRedact[0] == "X" and len(set(stringToRedact)) == 1:
            return "X" * len(stringToRedact)
            # TO CHANGE 
        elif stringToRedact.lower() in db.do_not_mask:
            return stringToRedact
        elif str(stringToRedact) not in self.listofredactedwords:
            self.listofredactedwords.append(stringToRedact)
            # elif len(stringToRedact) >= 3 and str(stringToRedact[:2]).isnumeric(): 
        #     if str(stringToRedact) not in self.listOfRedactedWords: 
        #       self.listOfRedactedWords.append(stringToRedact) 
        #     return "X" * len(stringToRedact) 
        return "X" * len(stringToRedact)
        # return stringToRedact 

    def extractEmail(self, redactNameSentence) -> list:
        # print("Extracting Emails......") 
        pattern = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?"
        for i, words in enumerate(redactNameSentence):
            if re.match(pattern, str(words)):
                splitEmail = str(words).rsplit("@", maxsplit=1)
                redactNameSentence[i] = self.redaction(AutoRedact,splitEmail[0]) + "@" + splitEmail[1]
        return redactNameSentence

    def check_address(self, sentenceToCheck):
        # print("Checking Address.......") 
        flag = 0
        for i, words in enumerate(sentenceToCheck):
            xx = self.add_punc(AutoRedact,words)
            prefix = xx[0]
            new_name = xx[1]
            setOfZipIndices = []

            if (i < len(sentenceToCheck) - 1):
                sw = self.add_punc(AutoRedact,sentenceToCheck[i + 1])
                secondword = sw[1]
                secondwordprefix = sw[0]

            if (i < len(sentenceToCheck) - 2):
                tw = self.add_punc(AutoRedact,sentenceToCheck[i + 2])
                thirdword = tw[1]
                thirdwordprefix = tw[0]

            if new_name.lower() in db.before and i > 0:
                sentenceToCheck[i - 1] = self.redaction(AutoRedact,sentenceToCheck[i - 1])

            if new_name.lower() in db.after and i < len(sentenceToCheck) - 1:
                sentenceToCheck[i + 1] = self.redaction(AutoRedact,sentenceToCheck[i + 1])

            if str(new_name) in db.zipcodes:
                setOfZipIndices.append(i)

            if new_name.lower() in db.cities or new_name.lower() in db.states or new_name in db.abbreviations:
                sentenceToCheck[i] = self.redaction(AutoRedact,new_name) + prefix
                flag = 1

            elif i < len(sentenceToCheck) - 1 and new_name.lower() + " " + secondword.lower() in db.cities:
                sentenceToCheck[i] = self.redaction(AutoRedact,new_name) + prefix
                sentenceToCheck[i + 1] = self.redaction(AutoRedact,secondword) + secondwordprefix
                flag = 1

            elif (i < len(
                    sentenceToCheck) - 2 and new_name.lower() + " " + secondword.lower() + " " + thirdword.lower() in db.cities):
                sentenceToCheck[i] = self.redaction(new_name) + prefix
                sentenceToCheck[i + 1] = self.redaction(secondword) + secondwordprefix
                sentenceToCheck[i + 2] = self.redaction(thirdword) + thirdwordprefix
                flag = 1

            elif (i < len(sentenceToCheck) - 1 and new_name.lower() + " " + secondword.lower() in db.states):
                sentenceToCheck[i] = self.redaction(new_name) + prefix
                sentenceToCheck[i + 1] = self.redaction(secondword) + secondwordprefix
                flag = 1

            elif (i < len(
                    sentenceToCheck) - 2 and new_name.lower() + " " + secondword.lower() + " " + thirdword.lower() in db.states):
                sentenceToCheck[i] = self.redaction(new_name) + prefix
                sentenceToCheck[i + 1] = self.redaction(secondword) + secondwordprefix
                sentenceToCheck[i + 2] = self.redaction(thirdword) + thirdwordprefix
                flag = 1

            if flag == 1 and len(setOfZipIndices) > 0:
                while (setOfZipIndices):
                    x = setOfZipIndices.pop()
                    xx = self.add_punc(AutoRedact,sentenceToCheck[x])
                    prefix2 = xx[0]
                    new_redacted_zip2 = xx[1]
                    sentenceToCheck[x] = self.redaction(AutoRedact,new_redacted_zip2) + prefix2

        return sentenceToCheck

    def redactingSSN(self, sentenceToCheck):
        for inds, word in enumerate(sentenceToCheck):
            if len(word) > 9 and str(word).isnumeric():
                xx = self.add_punc(AutoRedact,word)
                prefix = xx[0]
                new_name = xx[1]
                if re.match("^(?!219-09-9999|078-05-1120)(?!666|000|9\d{2})\d{3}-(?!00)\d{2}-(?!0{4})\d{4}$",
                            new_name) or re.match(
                    "^(?!219099999|078051120)(?!666|000|9\d{2})\d{3}(?!00)\d{2}(?!0{4})\d{4}$", new_name):
                    sentenceToCheck[inds] = self.redaction(AutoRedact,new_name) + prefix
        return sentenceToCheck 

AutoRedact.readFile(AutoRedact,r'../emailFolder/Email1.txt',"Email1.txt")


