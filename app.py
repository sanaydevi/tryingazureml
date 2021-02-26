# from flask import Flask, request, render_template
# from azureml.core import Workspace, Webservice
# import json
#
# app = Flask(__name__)
# @app.route("/")
# def hello():
#     return render_template('LandingPage.html')
#
# @app.route('/uploader', methods=['GET', 'POST'])
# def upload_files():
#
#     if request.method == 'GET':
#         return render_template('index.html')
#     if request.method == 'POST':
#         service_name = 'scoredfraudmodel'
#         ws = Workspace.get(
#             name='sdmMachineLearning',
#             subscription_id='efe60ef5-a4f3-4c91-8037-2f6c88c97246',
#             resource_group='T12-SDM'
#         )
#         service = Webservice(ws, service_name)
#         with open('uploads/trial.json', 'r') as f:
#             sample_data = json.load(f)
#         score_result = service.run(json.dumps(sample_data))
#         res = json.loads(score_result)
#         raw_scores = res["Results"]
#         print(raw_scores)
#         returnString = " ".join(str(x) for x in raw_scores)
#         return render_template('result.html', var=raw_scores)

from flask import Flask, request, render_template
from azure.storage.blob import BlobServiceClient
import imaplib
import email
from email.header import decode_header
import os
from azureml.core.workspace import Workspace, Webservice
import json
import pdfanalysis as pd

app = Flask(__name__)

connect_str = 'DefaultEndpointsProtocol=https;AccountName=sdmfilesystem;AccountKey=g7/AXgzgF9qCzE1cR+f3buGWIRT4nkCsWsbakAWh4fhXRxtrw/+vQ7ZJScPmIF0FNMaTNWXsMF1FkzdPJzJdTQ==;EndpointSuffix=core.windows.net'
# print(connect_str)
account_name = 'sdmfilesystem'
# Create the BlobServiceClient object which will be used to create a container client
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
local_path = "./uploads"
username = "sanaydevi@gmail.com"
password = "M@nu121227"


def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def readd():
    # create an IMAP4 class with SSL
    text = ''
    imap = imaplib.IMAP4_SSL("imap.gmail.com",993)
    # authenticate
    imap.login(username, password)
    status, messages = imap.select('"[Gmail]/Sent Mail"')
    # number of top emails to fetch
    N = 2
    # total number of emails
    dic = {}
    messages = int(messages[0])
    mainArr  = []
    mainDetails = []
    for i in range(messages, messages-N, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        stringforAttachement  = "0 Attachements Found"
        for response in msg:
            if isinstance(response, tuple):
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
                text = subject + " " +From + " " + to
                details.append(subject)
                details.append(From)
                details.append(to)
                emailDetails = subject + " " +From + " " + to
                # print("Subject:", subject)
                # print("From:", From)
                # if the email message is multipart
                attachmentScore = 0
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

                                filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                open(filepath, "wb").write(part.get_payload(decode=True))
                                textfilescore,scoreImageinPDF = pd.seperatePDF(filepath)
                                attachmentScore += scoreImageinPDF
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    text = text + " " + body
                    stringforAttachement = "0 Attachements Found"
                    # if content_type == "text/plain":
                    #
                        # print only text email parts
                        # print(body)
                    # if content_type == "text/html":
                    #     # if it's HTML, create a new HTML file and open it in browser
                    #     folder_name = clean(subject)
                    #     if not os.path.isdir(folder_name):
                    #         # make a folder for this email (named after the subject)
                    #         os.mkdir(folder_name)
                    #     filename = "index.html"
                    #     filepath = os.path.join(folder_name, filename)
                    #     # write the file
                    #     open(filepath, "w").write(body)
                        # open in the default browser
                        #webbrowser.open(filepath)
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

                # print("="*100)

    # close the connection and logout
    imap.close()
    imap.logout()
    return mainArr,mainDetails

@app.route("/")
def hello():

    return render_template('LandingPage.html')
    #return "Hello, World!"

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
        return render_template('index.html')
    if request.method == 'POST':
        arr = []
        mainArr,mainDetails = readd()
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
                mainDetails[i].append("High(" + str(x) + ")")
            elif float(x) >= 0.5 and float(x) < 0.6:
                mainDetails[i].append("Medium(" + str(x) + ")")
            if float(x) < 0.5:
                mainDetails[i].append("Low(" + str(x) + ")")
            i += 1

        arr = mainDetails
        print(mainDetails)

        # arr.append(" scores =  " + '  |  '.join([str(elem) for elem in tempArr]))
        # print(arr)
        # for x in arr:
        #     print(x)
        #arr.append(score_result)

        # uploaded_file = request.files.getlist("file[]")
        # container_name = "container" + str(uuid.uuid4())
        #
        # # Create the container
        # blob_service_client.create_container(container_name)
        # #
        # scoreResult = []
        # for file in uploaded_file:
        #     filename = secure_filename(file.filename)
        #     # file_extension = filename.rsplit('.', 1)[1]
        #     print(filename)
        #     file.save(os.path.join(local_path, filename))
        #
        #     local_file_name = filename
        #     upload_file_path = os.path.join(local_path, local_file_name)
        #
        #     # Create a blob client using the local file name as the name for the blob
        #     blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)
        #
        #
        #     print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)
        #
        #     # Upload the created file
        #     with open(upload_file_path, "rb") as data:
        #         blob_client.upload_blob(data)
        #
        # print("\nList blobs in the container")
        #
        # container = blob_service_client.get_container_client(container=container_name)
        #
        # generator = container.list_blobs()
        #
        # arr = []
        # for blob in generator:
        #     print("\t Blob name: " + blob.name)
        #
        #     service_name = 'scoredfraudmodel'
        #     ws = Workspace.get(
        #         name='sdmMachineLearning',
        #         subscription_id='efe60ef5-a4f3-4c91-8037-2f6c88c97246',
        #         resource_group='T12-SDM'
        #     )
        #     service = Webservice(ws, service_name)
        #
        #     url = "https://sdmfilesystem.blob.core.windows.net/" + container_name + "/" + blob.name
        #     url = r"https://sdmfilesystem.blob.core.windows.net/container6bbf8adb-1958-439a-b01c-7f1bae48befc/samples.json"
        #
        #     print(url)
        #     resp_text = urllib.request.urlopen(url).read().decode('UTF-8')
        #     # Use loads to decode from text
        #     json_obj = json.loads(resp_text)
        #     score_result = service.run(json.dumps(json_obj))
        #     print(f'Inference result = {score_result}')
        #     res = json.loads(score_result)
        #     raw_scores = (res["Raw Scores"])
        #     arr.append(raw_scores)

        return render_template('result.html', var=arr)




