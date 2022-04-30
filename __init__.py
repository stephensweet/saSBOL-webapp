"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)

import example_flask_dockerApp.views
