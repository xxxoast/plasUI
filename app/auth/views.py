#coding:utf-8 
from flask import render_template, redirect, request, url_for, flash, session, g, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user, fresh_login_required
from sqlalchemy import desc
from . import auth
from .. import db
from ..models import User
from .forms import module2form,LoginForm,TaskItemForm,TaskMerchantParamsForm,TaskSubmitForm
from .. import ufile
from ..misc import get_today, get_hourminsec, unicode2str_r,diff_seconds,timeint2str
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

def init_session_params(cookie,task_params_form):
    if cookie['item'] == 'merchant':
        session['param_vals'] = [ task_params_form.param1,  task_params_form.param2]
    elif cookie['item'] == 'reserve':
        session['param_vals'] = [ task_params_form.param1,  ]
    elif cookie['item'] == 'data_request':
        session['param_vals'] = [ task_params_form.param1,  ]
        
#self definition here            
def params_data_dump(cookie,input_form):
    if cookie['item'] == 'merchant':
        param1 = input_form.param1.data
        param2 = input_form.param1.data
        cookie['params'] = {}
        cookie['params']['param1'] = param1 
        cookie['params']['param2'] = param2 
    elif cookie['item'] == 'reserve':
        param1 = input_form.param1.data
        cookie['params'] = {}
        cookie['params']['param1'] = param1
    elif cookie['item'] == 'data_request':
        param1 = input_form.param1.data
        cookie['params'] = {}
        cookie['params']['param1'] = param1
        
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
    if 'param_vals' in session:
        ret['param_vals'] = session['param_vals']
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
    if force_init or ('param_vals' not in cookie):
        cookie['param_vals'] = ()
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
    task_item_form,task_submit_form = TaskItemForm(),TaskSubmitForm()
    try:
        print 'mode = ', session['item']
        task_params_form = module2form[session['item']]()
    except:
        task_params_form = TaskMerchantParamsForm()
    args = {}
    #2 step        
    if task_item_form.submit_task_item.data and task_item_form.validate_on_submit():
        print 'step 2'
        session['step'] = 2
        item_data_dump(session,task_item_form)
        task_params_form = module2form[session['item']]()
        init_session_params(session,task_params_form)
        print 'params = ', len(session['param_vals'])
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
            level = session['branch']
            task_id   = new_task.id
#             import uuid
#             task_id = repr(uuid.uuid1())
            submit_date = now[0]
            submit_time = now[1]
            task_record = (user_name,from_unit,to_unit,task_name,task_id,organization,level,submit_date,submit_time)
            print 'task_record = ',task_record
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
@auth.route('/submit_successed', methods=['GET', 'POST'])
def submit_successed():
    return render_template('auth/submit_successed.html')

###############################################################################################
@login_required
@auth.route('/query', methods=['GET', 'POST'])
def query():
    task_client = current_app.task_client
    redis_client = current_app.redis_client
    user_name = current_user.username
    ss = task_client.get_session()
    cursor = ss.query(task_client.task_struct).filter_by(username = user_name)\
                                                .order_by(desc(task_client.task_struct.submit_date))\
                                                .order_by(desc(task_client.task_struct.submit_time))\
                                                .all()
    ss.close()
    tbvals = []
    for record in cursor:
        task_id = record.task_id
        task_block = redis_client.get_value_by_id(task_id)
        task_ok = 0
        task_status = u'未提交'
        if task_block is not None:
            task_status = u'正在执行'
            if task_block['status'] == 'SUCCESS':
                task_status = u'执行完成'
                task_ok = 1
            else:
                task_status = u'执行错误'
        tbvals.append([record.username,record.task_name,record.task_to,record.orgnizition,\
                        record.level,'-'.join((str(record.submit_date),timeint2str(record.submit_time))),task_status,task_ok,task_id]) 
    print 'tbvals = ',tbvals
    return render_template('auth/query.html',tbvals = tbvals)


######################################################################################
#this is self-defined by module developer
@login_required
@auth.route('/query_result/<string:task_id>', methods=['GET', 'POST'])
def query_result(task_id):
    redis_client = current_app.redis_client
    task_block = redis_client.get_value_by_id(task_id)
    taskvals = json.loads(task_block['result'])['result']
    return render_template('auth/query_result.html',taskvals = taskvals)



