import base64

from flask import request
from flask import Flask, render_template

app = Flask(__name__)

data = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAC5ElEQVRYhcWXz0vUURDA3yWooMTolPqdNbWO4TmiYwehEiLchSAIokt/QXTsUIZBRLj7ZtukDhpJSexBog5CIPiF0jREIhArf+x+5+13dXe/7n7d6ZBurr6vu7rrNjDwhe/Mm8+becybJ8QWYeazrJFvcfcyIAVAWgiSTEAVA0k5kJRb/zbbXyb6p8ld1fkz852tsbTiBRCILq/5kLiUXhhM8Fo+r1titCIAfzRZMviGjvzM6pZYZeYDNQG4N5ryqAK3lgQY/eVeqhTgxvCyNro573bsGLwxYrd1RZOxSgGuvktqAa4PLy82BRMt2uAngr8PA9LUFQ/n3QD4o/o1uqJJBqRxX4QPbgMwpPXIh8TVALj9UV+Cjjc2+5DYQLpfvPtw8jRIylUL4MnntHaN9hdq3UatFpXCQPV8w7kaABOx3Db/xdRakY2BFBJCCFH3dLYe0MpUC+DiW5vzmkY09N0psgOklePh2BFhoLq2+UclACfDxGPz2ibEN98vb7M3womrwkArUgxg7wmgGYn7pjJa31nb5Zbwdh8DqVcA0pdKM3D+VYI/zHrdQcy3NLtfL8OoAEmJcjIwMO3ww7F0QXvMNEcmM2wuZL0uH2Zm7p/OeIIDqgUBSPlyAPYi0R8Ot2pS/0+VIwDJLacEuxHHzXP3WIqbSxxakOQKQIpXC0Bl1rhvKsPn+tWOgTedgbgAVGY5JRiZy/LgjFPQ1zMOD0w7HBxP891PK9w5ZJdItzYDpgCpsFp9YLcKUkkBaAf+F0CTJL+oD1IdSErXGgCQUsceW0eFEEJAWD2rOYBUWLgNG0LJUz5U2ZoBSMo2ol08H0LI6qkVAISsbv1IJmlyvwEMSRONPXOH9nUo9dSw8h5KN6QaY7mHLjX0qjM7BheiOg8TXdpL7nyfALIg6YFnzXcDUO7j1Id/mwxICxt7l9rKDlwK4Gvc7QS0AyAVAioTkOKF57mkGKAaA2nJJkn+QocrQ/4A80XCC5cGWmQAAAAASUVORK5CYII="

@app.route('/post-image', methods=['POST'])
def post_image():
    global data
    data = request.data.decode("utf-8")
    return "OK"

@app.route('/')
def hello_world():
    return render_template('index.html', img_data=data)

if __name__ == '__main__':
    app.run()
