import requests
import json
from flask import Flask, render_template, request

app = Flask(__name__)

client_id = '4114dac8-0195-475e-9b60-da65231a2ea8'
client_secret = 'E1N8Q~qkrgkAtK0mlNNHHNfQoDg7nDQeSWlOqaPJ'
tenant_id = 'e18a0c35-c3ed-46f4-8e69-018ca67f8288'
subscription_id = '6e268af1-b2a7-44a7-9a1a-9025889dbe5d'

token_uri = "https://login.microsoftonline.com/" + str(tenant_id) + "/oauth2/token"

token_req_headers = {'content-type': 'application/x-www-form-urlencodeds'}
token_req_body = 'grant_type=client_credentials&client_secret=' + str(client_secret) + '&client_id=' + str(
    client_id) + '&resource=https%3A%2F%2Fmanagement.azure.com%2F'

token_response = requests.request('POST', token_uri, headers=token_req_headers, data=token_req_body)

access_token = json.loads(token_response.text)['access_token']

costdata_uri = "https://management.azure.com/subscriptions/" + str(subscription_id) + "/providers/Microsoft" \
                                                                                      ".CostManagement/query?api-version=2021-10-01&$top=50"
costdata_body = '{"type":"ActualCost","dataSet":{"granularity":"None","aggregation":{"totalCost":{"name":"Cost",' \
                '"function":"Sum"},"totalCostUSD":{"name":"CostUSD","function":"Sum"}},"sorting": [{"direction": ' \
                '"descending","name": "Cost"}],"grouping":[{' \
                '"type":"Dimension","name":"ResourceId"},{"type":"Dimension","name":"ResourceType"},' \
                '{"type":"Dimension","name":"ResourceLocation"},{"type":"Dimension","name":"ChargeType"},' \
                '{"type":"Dimension","name":"ResourceGroupName"},{"type":"Dimension","name":"PublisherType"},' \
                '{"type":"Dimension","name":"ServiceName"},{"type":"Dimension","name":"ServiceTier"},' \
                '{"type":"Dimension","name":"Meter"}],"include":["Tags"],"filter":{"And":[{"Dimensions":{' \
                '"Name":"PublisherType","Operator":"In","Values":["azure"]}},{"Dimensions":{"Name":"BillingPeriod",' \
                '"Operator":"In","Values":["202310(2023-09-18 - 2023-10-17)"]}}]}},"timeframe": "MonthToDate"}'
costdata_headers = {'Authorization': 'Bearer ' +
                                     access_token, 'Content-Type': 'Application/JSON'}

costdata_response = requests.request('POST', costdata_uri, headers=costdata_headers, data=costdata_body)

cost_json_data = json.loads(costdata_response.text)


@app.route('/')
def index():
    custom_data_json = {}
    custom_data = []
    graph_x_data = []
    graph_y_data = []
    rstype_x_data = []
    rstype_y_data = []
    location_x_data = []
    location_y_data = []
    rg_x_data = []
    rg_y_data = []
    for items in cost_json_data['properties']['rows']:
        custom_data_json['cost'] = round(items[0], 2)
        custom_data_json['resourceid'] = items[2]
        custom_data_json['resource'] = (items[2]).split('/')[-1]
        custom_data_json['type'] = items[3]
        custom_data_json['location'] = items[4]
        custom_data_json['chargetype'] = items[5]
        custom_data_json['rgname'] = items[6]
        custom_data_json['publisher'] = items[7]
        custom_data_json['servicename'] = items[8]
        custom_data_json['tier'] = items[9]
        custom_data_json['meter'] = items[10]
        custom_data_json['currency'] = items[12]
        custom_data.append(custom_data_json.copy())
        graph_x_data.append((items[2]).split('/')[-1])
        graph_y_data.append(items[0])
        if items[3] not in rstype_x_data:
            rstype_x_data.append(items[3])
            rstype_y_data.append(items[0])
        elif items[3] in rstype_x_data:
            index = rstype_x_data.index(items[3])
            old_data = rstype_y_data[index]
            new_data = old_data + items[0]
            rstype_y_data[index] = new_data
        if items[4] not in location_x_data:
            location_x_data.append(items[4])
            location_y_data.append(items[0])
        elif items[4] in location_x_data:
            lindex = location_x_data.index(items[4])
            old_data = location_y_data[lindex]
            new_data = old_data + items[0]
            location_y_data[lindex] = new_data
        if items[6] not in rg_x_data:
            rg_x_data.append(items[6])
            rg_y_data.append(items[0])
        elif items[6] in rg_x_data:
            rgindex = rg_x_data.index(items[6])
            old_data = rg_y_data[rgindex]
            new_data = old_data + items[0]
            rg_y_data[rgindex] = new_data

    return render_template('index.html', costdata=custom_data, labels=graph_x_data, data=graph_y_data,
                           glabels=rstype_x_data, gdata=rstype_y_data, llabels=location_x_data, ldata=location_y_data,rglabels=rg_x_data, rgdata=rg_y_data)


@app.route('/examine', methods=['GET', 'POST'])
def examine():
    resourceid = request.form['resourceid']
    resource_uri = "https://management.azure.com" + str(resourceid) + "?api-version=2021-04-01"
    resource_response = requests.request("GET", resource_uri, headers=costdata_headers)
    resource_json_data = json.loads(resource_response.text)

    return render_template('kvcompliance.html', data=resource_json_data)


if __name__ == '__main__':
    app.run()
