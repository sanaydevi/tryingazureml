from flask import Flask, request, render_template
from azureml.core import Workspace, Webservice
import json

app = Flask(__name__)
@app.route("/")
def hello():
    return render_template('LandingPage.html')

@app.route('/uploader', methods=['GET', 'POST'])
def upload_files():

    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        service_name = 'scoredfraudmodel'
        ws = Workspace.get(
            name='sdmMachineLearning',
            subscription_id='efe60ef5-a4f3-4c91-8037-2f6c88c97246',
            resource_group='T12-SDM'
        )
        service = Webservice(ws, service_name)
        with open('uploads/trial.json', 'r') as f:
            sample_data = json.load(f)
        score_result = service.run(json.dumps(sample_data))
        res = json.loads(score_result)
        raw_scores = res["Results"]
        print(raw_scores)
        returnString = " ".join(str(x) for x in raw_scores)
        return render_template('result.html', var=raw_scores)
