from flask import Flask, session
from env import KEY

app = Flask(__name__)
app.secret_key = KEY