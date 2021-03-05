import pandas as pd
import time, re
from Masking import CreditCardValidation as credit

ts = time.time()
timestr = time.strftime("%Y%m%d-%H%M%s")


# start point
def pciMask(location_of_excel):
    data = pd.read_excel(location_of_excel, dtype=str)

    # for docx
    # my_text = docx2txt.process(Main.location_of_excel)
    # with open("MaskedFile/doc_text.txt", "w+") as writer:
    #     writer.write(my_text)
    # writer.close()
    # data = pd.read_csv("MaskedFile/doc_text.txt", dtype=str, delimiter="|")

    header_names = list(data.head(0))
    print(header_names)
    mainDataFrame = pd.DataFrame(data, dtype=str)
    mainDataFrame = mainDataFrame.astype(str)
    arrofUnmasked = []
    binNumbers = []
    noOfRowsMarked = 0

    for header in header_names:
        header = str(header)
        print("column begins:"+header+"--------------")
        newdata = pd.DataFrame(data, columns=[header])
        for ind, row in newdata.iterrows():
            columnsentence = row[header]
            re_list = [
                r"(?=(54\d{14}))",
                r"(?=(55\d{14}))",
                r"(?=(4\d{15}))",
                r"(?=(51\d{14}))",
                r"(?=(34\d{13}))",
                r"(?=(37\d{13}))",
                r"(?=(622\d{13}))",
                r"(?=(622\d{14}))",
                r"(?=(622\d{16}))",
                r"(?=(300\d{11}))",
                r"(?=(305\d{11}))",
                r"(?=(36\d{12}))",
                r"(?=(6\d{15}))",
                r"(?=(3528\d{12}))",
                r"(?=(3589\d{12}))",
                r"(?=(5018\d{8}))",
                r"(?=(5018\d{9}))",
                r"(?=(5018\d{10}))",
                r"(?=(5018\d{11}))",
                r"(?=(5018\d{12}))",
                r"(?=(5018\d{13}))",
                r"(?=(5018\d{14}))",
                r"(?=(5018\d{15}))",
                r"(?=(5020\d{8}))",
                r"(?=(5020\d{9}))",
                r"(?=(5020\d{10}))",
                r"(?=(5020\d{11}))",
                r"(?=(5020\d{12}))",
                r"(?=(5020\d{13}))",
                r"(?=(5020\d{14}))",
                r"(?=(5020\d{15}))",
            ]
            matches = []
            strcolumnsentence = str(columnsentence)
            for r in re_list:
                matches += re.findall(r, strcolumnsentence)
                # print(matches)
            for match in matches:
                value, maskedCard, binNumber = credit.CreditCardValidation(match, strcolumnsentence).startValidation()
                if value:
                    # if len(binNumber) > 1:
                    #     binNumber.append(binNumber)
                    print(maskedCard)
                    if match not in columnsentence:
                        continue
                    indextoSplit = columnsentence.find(match)
                    columnsentence = columnsentence[:indextoSplit] + maskedCard + columnsentence[indextoSplit+len(maskedCard):]
                    noOfRowsMarked += 1
                    mainDataFrame.at[ind, str(header)] = columnsentence
            mainDataFrame.at[ind, str(header)] = columnsentence
    path = "/Users/sanaydevi/PycharmProjects/KafkaHCL/output/PCIMaskedFile"+timestr+".xlsx"
    mainDataFrame.to_excel(path)
    print("-----Finished Masking Successfully-----")
    return path




