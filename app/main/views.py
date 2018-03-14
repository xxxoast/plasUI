from flask import render_template, request, url_for, flash, redirect, jsonify
from . import main
from .. import ufile
from .forms import UploadForm, RuleForm, ResetRules, JsBindBubmit, RadioBoxForm
import os
import json

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/me')
def me():
    return render_template('resume.html')


#----------------------------------------------------------------
#@The below code are all testing code
@main.route('/test', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        filename = ufile.save(form.upload_file.data)
        file_url = ufile.url(filename)
        print file_url
    else:
        file_url = None
    return render_template('test/upload.html', form=form, file_url=file_url)


@main.route('/progressbar', methods=['GET', 'POST'])
def progressbar():
    return render_template('test/progressbar.html')


initV = 0
@main.route('/getValue', methods=['GET', 'POST'])
def getValue():
    global initV
    initV = initV + 5 if (initV <= 95) else 0
    return jsonify(result=initV)


@main.route('/square', methods=['GET', 'POST'])
def square():
    input = request.args.get('value', -1, type=int)
    print 'request.args = ', request.args, ' input = ', input
    return jsonify(result=input + 100)


@main.route('/testJquery', methods=['GET', 'POST'])
def test_jquery():
    return render_template('test/test_jquery.html')

