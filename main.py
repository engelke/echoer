# Copyright 2019 by Charles Engelke
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from datetime import datetime
from flask import Flask, render_template, request
from google.cloud import firestore


app = Flask(__name__)


def save(content_type, headers, body):
    db = firestore.Client()
    posts = db.collection('posts')
    posts.add({
        'timestamp': datetime.utcnow().isoformat(timespec='seconds'),
        'content_type': content_type,
        'headers': headers,
        'body': body,
    })


@app.route('/', methods=['GET'])
def list_recent_posts():
    db = firestore.Client()
    posts = db.collection('posts')
    query = posts.order_by('timestamp', direction=firestore.Query.DESCENDING)
    all_posts = [post.to_dict() for post in query.stream()]
    return render_template('index.html', posts=all_posts[:20])


@app.route('/', methods=['POST'])
def remember_post():

    save(
        request.content_type,
        ['{}: {}'.format(k, v) for k, v in request.headers.items()],
        request.get_data(as_text=True),
    )

    return 'Saved', 201


if __name__ == '__main__':
    # For local testing only. App Engine will handle this when deployed.
    app.run(host='127.0.0.1', port=8080, debug=True)
