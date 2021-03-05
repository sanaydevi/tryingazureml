from flask import Flask, request, render_template,redirect,url_for
from azure.storage.blob import BlobServiceClient
import imaplib
import email
from email.header import decode_header
import os
from azureml.core.workspace import Workspace, Webservice
import json
import pdfanalysis as pd
import collections
import webbrowser

import textile


app = Flask(__name__)

connect_str = 'DefaultEndpointsProtocol=https;AccountName=sdmfilesystem;AccountKey=g7/AXgzgF9qCzE1cR+f3buGWIRT4nkCsWsbakAWh4fhXRxtrw/+vQ7ZJScPmIF0FNMaTNWXsMF1FkzdPJzJdTQ==;EndpointSuffix=core.windows.net'
# print(connect_str)
account_name = 'sdmfilesystem'
# Create the BlobServiceClient object which will be used to create a container client
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
local_path = "./uploads"
username = "sanaydevi@gmail.com"
password = "M@nu121227"

dictOfLinks = collections.defaultdict(list)
mainArrSent = []

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def readd(emailName):
    # create an IMAP4 class with SSL
    text = ''
    imap = imaplib.IMAP4_SSL("imap.gmail.com",993)
    # authenticate
    imap.login(username, password)
    status, messages = imap.select('"[Gmail]/Sent Mail"')
    # number of top emails to fetch
    N = 10
    # total number of emails
    messages = int(messages[0])
    mainArr  = []
    mainDetails = []
    uniqueIdentifier = 0

    for i in range(messages, messages-N, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        stringforAttachement  = "0 Attachements Found"
        uniqueIdentifier += 1
        for response in msg:
            if isinstance(response, tuple):
                emailFilename = "emailFolder/Email"+str(uniqueIdentifier)+".txt"
                emailfile = open(emailFilename, "w")

                details = []
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])

                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]

                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)

                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                to,encoding = decode_header(msg.get("To"))[0]

                if isinstance(to, bytes):
                    to = to.decode(encoding)
                if isinstance(From, bytes):
                    From = From.decode(encoding)

                #text = subject + " " + From + " " + to
                text = subject
                metadata = "Subject = "+subject+ " \n From: " + From + "\n To : "+ to

                emailfile.write(metadata)


                details.append(subject)
                details.append(From)
                details.append(to)
                attachmentScore = 0

                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    attachementCount = 0

                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            # print(body)
                            text = text + " " + body
                            emailfile.write(text)
                        elif "attachment" in content_disposition:
                            # download attachment
                            filename = part.get_filename()
                            attachementCount += 1
                            stringforAttachement = str(attachementCount)+ " Attachements found"
                            #attachementCount += 1
                            if filename:
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(folder_name)
                                print(filename)
                                print(folder_name)
                                print(filename)

                                filepath = os.path.join(folder_name, filename)
                                xfilepath = os.path.join(folder_name, filename)
                                print(filepath)
                                # download attachment and save it
                                open(filepath, "wb").write(part.get_payload(decode=True))
                                textfilescore,scoreImageinPDF = pd.seperatePDF(filepath)
                                attachmentScore += scoreImageinPDF
                                dictOfLinks[uniqueIdentifier] = [xfilepath]
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()

                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    text = text + " " + body
                    emailfile.write(text)

                    stringforAttachement = "0 Attachements Found"

                        # open in the default browser
                        #webbrowser.open(filepath)

                emailfile.close()
                dictOfLinks[uniqueIdentifier].append(emailFilename)
                editedTex = "1 | " + text
                stringg = {"Column1": editedTex}
                mainArr.append(stringg)

                if attachmentScore > 0:
                    details.append(stringforAttachement)
                    details.append("Possible Fraud Detected in Attachement")
                else:
                    if stringforAttachement == "0 Attachements Found":
                        details.append(stringforAttachement)
                        details.append("#N/A")
                    else:
                        details.append(stringforAttachement)
                        details.append("Attachement Scan Successful")


                mainDetails.append(details)
                print(mainDetails)
    # close the connection and logout
    imap.close()
    imap.logout()
    return mainArr,mainDetails

@app.route("/")
def hello():
    return render_template('indexLanding.html')
    #return "Hello, World!"

@app.route('/discoverNav',methods=['GET'])
def test():
    if request.method == 'GET':
        return render_template('eDiscoveryNavigation.html')

@app.route('/readEmail',methods=['GET','POST'])
def test2():
    if request.method == 'GET':
        return render_template('readEmail.html')
    if request.method == 'POST':

        return render_template('readEmail.html')

@app.route('/dropbox',methods=['GET','POST'])
def test3():
    if request.method == 'GET':
        return render_template('dropbox.html')
    if request.method == 'POST':
        return render_template('dropbox.html')

@app.route('/dropboxresult',methods=['GET','POST'])
def test4():
    if request.method == 'GET':
        return render_template('eFileScanResult.html')
    if request.method == 'POST':
        return render_template('eFileScanResult.html')

@app.route('/displayFile', methods=['POST'])
def openFile():
    if request.method == "POST":
        emailNumber = request.form.get('comp_select')
        print(emailNumber)

        listOfpaths  = dictOfLinks[int(emailNumber)]
        mainArr= request.form.getlist('item_id')

        for x in listOfpaths:

            # f = open(x, 'r')
            # file_contents = f.read()
            # print(file_contents)
            webbrowser.open('file://' + os.path.realpath(x))
            #webbrowser.open(x)
        return render_template('eDiscoveryResult.html', var=mainArrSent[0],numberOfEmails = len(dictOfLinks))


@app.route('/button', methods=["GET", "POST"])
def button():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == "POST":
        ButtonPressed = 0
        arr = []
        return render_template("result.html", var = arr)

        # I think you want to increment, that case ButtonPressed will be plus 1.

@app.route('/uploader', methods=['GET', 'POST'])
def upload_files():
    def ls_files(client, path, recursive=False):
        '''
        List files under a path, optionally recursively
        '''
        if not path == '' and not path.endswith('/'):
            path += '/'

        blob_iter = client.list_blobs(name_starts_with=path)
        files = []
        for blob in blob_iter:
            relative_path = os.path.relpath(blob.name, path)
            if recursive or not '/' in relative_path:
                files.append(relative_path)
        return files

    if request.method == 'GET':
        return render_template('eDiscoveryResult.html')

    if request.method == 'POST':
        arr = []
        emailName = request.form.get('nameofemail')
        print(emailName)
        mainArr,mainDetails = readd(emailName)
        # [["from","to,"subject"],]
        # editedTex  = "1 | "+t
        # stringg = [{"Column1":editedTex}]
        ini_string = json.dumps(mainArr)
        service_name = 'scoredfraudmodel'
        ws = Workspace.get(
            name='sdmMachineLearning',
            subscription_id='efe60ef5-a4f3-4c91-8037-2f6c88c97246',
            resource_group='T12-SDM'
        )
        service = Webservice(ws, service_name)
        # print(ini_string)
        score_result = service.run(ini_string)

        # print(f'Inference result = {score_result}')
        res = json.loads(score_result)

        results = (res["Results"])
        tempArr = []
        i = 0
        for x in results:

            if float(x) >= 0.6:
                x = str(round(float(x), 2) * 100)
                mainDetails[i].append("High(" + str(x) + "% )")
            elif float(x) >= 0.5 and float(x) < 0.6:
                x = str(round(float(x),1 ) * 100)
                mainDetails[i].append("Medium(" + str(x) + "% )")
            if float(x) < 0.5:
                x = str(round(float(x), 2) * 100)

                mainDetails[i].append("Low(" + str(x) + "% )")
            i += 1

        arr = mainDetails
        print(mainDetails)
        mainArrSent.append(arr)

        return render_template('eDiscoveryResult.html', var=arr,numberOfEmails = len(dictOfLinks))




