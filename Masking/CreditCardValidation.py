class CreditCardValidation:
    def __init__(self, inputString, sentence):
        self.cardnumber = str(inputString)
        self.strippedcardnum = self.cardnumber.replace("-", "")
        self.sentence = sentence
        self.binNumber = "0"

    def checkLength(self):
        if len(self.cardnumber) < 12 or len(self.cardnumber) > 19:
            return False
        else:
            return True

    def checkFirstNumber(self):
        if int(self.cardnumber[0]) < 1 or int(self.cardnumber[0]) >9:
            return False
        else:
            return True

    def checkAmex(self):
        if int(self.cardnumber[:2]) == 34 or int(self.cardnumber[:2] == 37):
            if len(self.cardnumber) == 15:
                if self.luhn:
                    return True
                else:
                    return False
            else:
                return False

    def chinaUnionPay(self):
        if int(self.cardnumber[:3]) == 622:
            if 16>=len(self.cardnumber) <= 19:
                if self.luhn:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def diners(self):
        if int(self.cardnumber[:3]) == 300 or int(self.cardnumber[:3]) == 305:
            if len(self.cardnumber) == 14:
                if self.luhn:
                    return True
                else:
                    return False
            else:
                return False
        return False

    def dinerClubInternational(self):
        if int(self.cardnumber[:2]) == 36:
            if len(self.cardnumber) == 14:
                if self.luhn:
                    return True
                else:
                    return False
            else:
                return False
        return False

    def dinerUSCA(self):
        if int(self.cardnumber[:2]) == 54 or int(self.cardnumber[:2]) == 55:
            if len(self.cardnumber) == 16:
                if self.luhn:
                    return True
                else:
                    return False
            else:
                return False
        return False

    def discover(self):
        if int(self.cardnumber[:4]) == 6011 or (622126 <= int(self.cardnumber[:7]) <= 622925) or int(self.cardnumber[:2] == 65):
            if len(self.cardnumber) == 16:
                if self.luhn:
                    return True
                else:
                    return False
            else:
                return False
        return False

    def luhn(self):
        r = [int(ch) for ch in str(self.cardnumber)][::-1]
        return (sum(r[0::2]) + sum(sum(divmod(d*2, 10)) for d in r[1::2])) % 10 == 0

    def maskNumber(self):
        if str(self.cardnumber[:6]) == "556940":
            return self.cardnumber
        # Separate Entity Rule
        elif str(self.cardnumber[6]) == "3" or str(self.cardnumber[6]) == "4":
            return self.cardnumber
        else:
            lengthOfCard = len(self.cardnumber)
            numberOfX = lengthOfCard - 10
            stringOfX = numberOfX * "x"
            self.binNumber = self.cardnumber[:6]
            return self.cardnumber[:6] + stringOfX + self.cardnumber[-4:]

    def startValidation(self):
        if self.checkLength() and self.checkFirstNumber():
            #  or self.JCB() or self.Maestro() or self.MasterCard() or self.Visa()
            if self.checkAmex() or self.chinaUnionPay() or self.dinerClubInternational() or self.diners() or\
                    self.dinerUSCA() or self.discover():
                if self.luhn():
                    return True, self.maskNumber(), self.binNumber
        return False, self.cardnumber, self.binNumber

