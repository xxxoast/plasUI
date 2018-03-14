#coding:utf-8 
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
import time

min_backtest_gap_seconds = 10

#########################################################################
''' misc '''

def submit_over_frequency(last_submit,now):
    return last_submit[0] != -1 and diff_seconds(now,last_submit) < min_backtest_gap_seconds


#########################################################################
''' Web Input Data -> Server Format Data '''

def web_data_to_server_data(web_data):
    pass

def item_data_dump(cookie,input_form):
    start_date, end_date = input_form.start_date.data, input_form.end_date.data
    item = input_form.item.data
    destination = input_form.destination.data
    organization = input_form.organization.data
    branch = input_form.branch.data
    cookie['start_date'],cookie['end_date'],cookie['item'],\
        cookie['destination'],cookie['organization'],cookie['branch'] = start_date, end_date, item, \
            destination, organization,branch

#self definition here            
def params_data_dump(cookie,input_form):
    param1 = input_form.param1.data
    param2 = input_form.param1.data
    cookie['params']['param1'] = param1 
    cookie['params']['param2'] = param2 
    
#########################################################################
''' Inject vars '''
@auth.context_processor
def inject_var():
    ret = {}
    if 'step' in session:
        ret['step'] = session['step']
    if 'params' in session:
        ret['params'] = session['params']
    if 'task_information' in session:
        ret['task_information'] = session['task_information']
    return ret

def init_session(cookie,force_init = False):
    if force_init or ( 'last_submit_task' not in cookie ):
        cookie['last_submit_task'] = (-1, -1)   
    if force_init or ( 'step' not in cookie ):
        cookie['step'] = 1
    if force_init or ( 'params' not in cookie ) or (cookie['params'] is None):
        cookie['params'] = {}
    if force_init or ( 'task_information' not in cookie):
        cookie['task_information'] = ()
#     print 'session init =', cookie['last_submit_task'],cookie['step'],cookie['params']
    
#########################################################################
''' For log in '''

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, False)
            init_session(session,False)
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
@auth.route('/task/', methods=['GET', 'POST'])
@auth.route('/task/<int:step>/', methods=['GET', 'POST'])
def task(step = None):
    #get input form data
    task_item_form,task_params_form,task_submit_form = TaskItemForm(),TaskMerchantParamsForm(),TaskSubmitForm()
    args = {}
    #2 step        
    if task_item_form.submit_task_item.data and task_item_form.validate_on_submit():
        print 'step 2'
        session['step'] = 2
        item_data_dump(session,task_item_form)
    #3 step
    elif task_params_form.submit_task_params.data and task_params_form.validate_on_submit():
        print 'step 3'
        session['step'] = 3
        params_data_dump(session, task_params_form)
        params = '|'.join([ unicode2str_r(v) for v in session['params'].values() ])
        tstamp = ':'.join((str(get_today()),str(get_hourminsec())))
        task_information = (current_user.username,session['item'],session['destination'],\
                            session['organization'],session['branch'],session['start_date'],session['end_date'],\
                            params,tstamp)
        session['task_information'] = task_information
    #4 step
    elif task_submit_form.submit_task.data and task_submit_form.validate_on_submit():
        print 'step 4'
        now = (get_today(), get_hourminsec())
        if submit_over_frequency(session['last_submit_task'],now):
            flash('warning! take a rest~~'.format(min_backtest_gap_seconds)) 
        else:
            session['last_submit_task'] = now
            session['step'] = 1
            print session['item'],session['organization'],session['params']
            ##As a demo, we only call this module
            #new_task = current_app.rpc_client[session['item']].delay(session['organization'],*session['params'])
            new_task = current_app.rpc_client['non_certify'].delay('pingan','merchant')
            print new_task.ready()
            ##Update this history in MYSQL task
            user_name = current_user.username
            user = User.query.filter_by(username=user_name).first()
            from_unit = user.work_unit
            to_unit   = session['destination']
            task_name = session['item']
            organization = session['organization']
            task_id   = new_task.id
#             import uuid
#             task_id = repr(uuid.uuid1())
            submit_date = now[0]
            submit_time = now[1]
            task_record = (user_name,from_unit,to_unit,task_name,task_id,organization,submit_date,submit_time)
            print task_record
            task_client = current_app.task_client
            task_client.insert_listlike(task_client.task_struct, task_record, merge=False)
            ##############################################################################
            return redirect(url_for('auth.submit_successed'))
    #1 step    
    else:
        print 'step 1'
        try:
            if step is not None:
                session['step'] = step
        except:
            session['step'] = 1
    #inject form as params
    args['task_item_form'],args['task_params_form'],args['task_submit_form'] = \
                    task_item_form,task_params_form,task_submit_form      
    return render_template('auth/task.html', **args)


@login_required
@auth.route('/query', methods=['GET', 'POST'])
def query():
    args = {}
    return render_template('auth/query.html', **args)


@login_required
@auth.route('/submit_successed', methods=['GET', 'POST'])
def submit_successed():
    task_client = current_app.task_client
    user_name = current_user.username
    cursor = task_client.query_obj(task.task_struct,username = user_name)
    cols = task_client.get_column_names(task_client.task_struct)
    print cols
    for record in cursor:
        task_id = record['task_id']
        fileds = [ getattr(record,x) for x in cols ]
    return render_template('auth/submit_successed.html')








