# Umiirosoft Teal | coding by @gamma_410
# Copyright 2022 Umiirosoft.

from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def redirect_func():
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)