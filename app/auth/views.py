from flask import render_template, redirect, request, url_for, flash, session, g, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user, fresh_login_required
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm,TaskItemForm,TaskMerchantParamsForm,TaskSubmitForm
from .. import ufile
from ..misc import get_today, get_hourminsec, unicode2str_r,diff_seconds
import os
import json

min_backtest_gap_seconds = 10

#########################################################################
''' misc '''

def submit_over_frequency(last_submit,now):
    return last_submit[0] != -1 and diff_seconds(now,last_submit) < min_backtest_gap_seconds


#########################################################################
''' Web Input Data -> Server Format Data '''

def web_data_to_server_data(web_data):
    pass

def web_data_dump(input_form):
    pass

#########################################################################
''' Inject vars '''
@auth.context_processor
def inject_var():
    ret = {}
    ret['step'] = session['step']
    ret['params'] = session['params']
    return ret

def init_session(cookie):
    if 'last_submit_task' not in cookie:
        cookie['last_submit_task'] = (-1, -1)   
    if 'step' not in cookie:
        cookie['step'] = 1
    if 'params' not in cookie:
        cookie['params'] = {}

#########################################################################
''' For log in '''

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, False)
            return redirect(url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

#########################################################################
''' Main Page: Task & Query '''
@login_required
@auth.route('/task', methods=['GET', 'POST'])
@auth.route('/task/<int:step>', methods=['GET', 'POST'])
def task():
    init_session(session,True)
    #get input form data
    task_item_form,task_params_form,task_submit_form = TaskItemForm(),TaskMerchantParamsForm(),TaskSubmitForm()
    #second step
    if task_params_form.submit_task_params.data and task_params_form.validate_on_submit():
        now = (get_today(), get_hourminsec())
        if submit_over_frequency(session['last_submit_task'],now):
            flash('warning! take a rest~~'.format(min_backtest_gap_seconds))
            return redirect(url_for('auth.fill'))  
        else:
            session['last_submit_task'] = now
            session['step'] = 3    
    #third step        
    elif task_item_form.submit_task_item.data and task_item_form.validate_on_submit():
        session['step'] = 2
    #fourth step
    elif task_submit_form.submit_task.data and task_submit_form.validate_on_submit():
        return redirect(url_for('main.index'))
    #first step    
    else:
        try:
            step = request.args.get('step')
            session['step'] = step
        except:
            session['step'] = 1
    
    #inject form as params
    args = {}
    args['task_item_form'],args['task_params_form'],args['task_submit_form'] = \
                    task_item_form,task_params_form,task_submit_form      
    return render_template('auth/task.html', **args)


@login_required
@auth.route('/query', methods=['GET', 'POST'])
def query():
    pass











