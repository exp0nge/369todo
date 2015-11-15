from flask import Flask, request, jsonify
from bitbucket.bitbucket import Bitbucket
import todoist

app = Flask(__name__)

# Todoist Info
api = todoist.TodoistAPI('TODOIST API TOKEN')
project_id = 'PROJECT ID'
issue_label_id = 'ISSUE LABEL ID'
business_label_id = 'BUSINESS LABEL ID'

# Bitbucket Info
bitbucket_login = Bitbucket("username", "password")
issues_dict = {}


ok = []


@app.route('/')
def index():
    return jsonify(ok)


@app.route('/webhook', methods=['POST'])
def todo_hook():
    data = request.get_json()
    api.sync(resource_types=['all'])
    if data['event_name'] == 'item:added':
        for label_id in data['event_data']['labels']:
            ok.append(data)
            # print "Label ID: " + str(label_id)
            label_name = api.labels.get_by_id(label_id)
            # print "Label Name: " + str(label_name)
            title = data['event_data']['content'] + " # ID: " + str(data['event_data']['id'])
            ok.append(data)
            if 'task' == label_name['name']:
                issue = bitbucket_login.issue.create('hack_battle',
                                                     title=title,
                                                     kind='task',
                                                     content=data['event_data']['due_date'])
                # api.sync(resource_types=['all'])
                # item = api.items.get_by_id(label_id)
                # print item
                # item.update(content=title)
                # api.commit()
                issues_dict[data['event_data']['id']] = issue[1]['local_id']
                break
    elif data['event_name'] == 'note:added':
        if issues_dict.get(data['event_data']['item_id'], False):
            bitbucket_login.issue.update(
                issues_dict[data['event_data']['item_id']],
                'hack_battle', content=data['event_data']['content'])
        del issues_dict[data['event_data']['id']]
    return 'OK'


@app.route('/bithook', methods=['GET', 'POST'])
def bitbucket_hook():
    if request.method == 'POST':
        data = request.get_json()
        if data['issue']['kind'] == 'bug':
            try:
                issue_title, issue_message = data['issue']['title'], data['issue']['content']['raw']
                item = api.items.add(content=issue_title, project_id=project_id, labels=[issue_label_id])
                api.notes.add(item.temp_id, issue_message)
                api.commit()
            except IndexError:
                pass
    return 'OK'


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)