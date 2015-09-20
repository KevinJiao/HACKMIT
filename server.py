# This file provided by Facebook is for non-commercial testing and evaluation
# purposes only. Facebook reserves all rights not expressly granted.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# FACEBOOK BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import json
import os
from flask import Flask, Response, request

app = Flask(__name__, static_url_path='', static_folder='')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

@app.route('/reset', methods=['GET', 'POST'])
def comments_handler():
    console.log("resetting")
    if request.method == 'POST':

        with open('data.json', 'r') as r:
            data = json.load(f)
            data["game_state"]="reset"

        with open('data.json', 'w') as f:
            f.write(json.dumps(data));

    return Response(json.dumps(data), mimetype='application/json', headers={'Cache-Control': 'no-cache'})

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT",3000)))