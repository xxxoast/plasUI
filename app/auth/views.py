#coding:utf-8 
from flask import render_template, redirect, request, url_for, flash, session, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user, fresh_login_required
from sqlalchemy import desc, func
from . import auth
from .. import db
from ..models import User
from ..create_user_table import get_cities
from .forms import module2form,LoginForm,TaskItemForm,TaskMerchantParamsForm,TaskSubmitForm
from .. import ufile
from ..misc import get_today, get_hourminsec, unicode2str_r,diff_seconds,timeint2str,unicode2utf8_r
import os
import json
import time
from app.misc import unicode2utf8

min_backtest_gap_seconds = 10
cities = get_cities()

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
    print 'item data = ',cookie['start_date'],cookie['end_date'],cookie['item'],\
        cookie['destination'],cookie['organization'],cookie['branch']

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
        param2 = input_form.param2.data
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
    #As task_params_form is a dynamic module... 
    #动态代码一时爽，代码重构...
    try:
        print 'item = ',session['item']
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
    #3 step
    elif task_params_form.submit_task_params.data and task_params_form.validate_on_submit():
        print 'step 3'
        session['step'] = 3
        params_data_dump(session, task_params_form)
        print session['params']
        print session['params']
        params = '|'.join([ unicode2str_r(v) for k,v in sorted(session['params'].items(),key = lambda x:x[0]) ])
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
            ##As a demo, we only call this module
            #new_task = current_app.rpc_client[session['item']].delay(session['organization'],*session['params'])
            #new_task = current_app.rpc_client['non_certify'].delay('pingan','merchant')
            ##Update this history in MYSQL task
            user_name = current_user.username
            user = User.query.filter_by(username=user_name).first()
            from_unit = user.work_unit
            to_unit   = session['destination']
            task_name = session['item']
            organization = session['organization']
            level = session['branch']
            task_id   = ''
            submit_date = now[0]
            submit_time = now[1]
            params = '|'.join([ unicode2str_r(v) for k,v in sorted(session['params'].items(),key = lambda x:x[0]) ])
            task_record = (None,user_name,from_unit,to_unit,task_name,task_id,organization,level,submit_date,submit_time,params)
            print 'task_record = ',task_record
            task_client = current_app.task_client
            task_client.insert_listlike(task_client.table_struct, task_record, merge=False)
            ##############################################################################
            return redirect(url_for('auth.submit_successed'))
    #1 step    
    else:
        if step is not None:
            session['step'] = step
        else:
            session['step'] = 1
    #inject form as params
    #must be put here, because param_vals will be rendered by ref when loading templates,must be inited everytime
    #As task_params_form is a dynamic module... 
    init_session_params(session,task_params_form)
    print 'step =', session['step']
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
    cursor = ss.query(task_client.table_struct).filter_by(username = user_name)\
                                                .order_by(desc(task_client.table_struct.submit_date))\
                                                .order_by(desc(task_client.table_struct.submit_time))\
                                                .all()
    ss.close()
    tbvals = []
    for record in cursor:
        task_id = record.task_id
        task_block = redis_client.get_value_by_id(task_id)
        task_ok = 0
        task_status = u'待审核' if str(task_id) != str('-1') else u'上级拒绝'
        if task_block is not None:
            task_status = u'正在执行'
            if task_block['status'] == 'SUCCESS':
                task_status = u'已完成'
                task_ok = 1
            else:
                task_status = u'执行错误'
        tbvals.append([record.username,record.task_name,record.task_to,record.orgnizition,\
                        record.level,'-'.join((str(record.submit_date),timeint2str(record.submit_time))),task_status,task_ok,task_id]) 
    print 'tbvals = ',tbvals
    return render_template('auth/query.html',tbvals = tbvals)


####################################################################################
@login_required
@auth.route('/authorize', methods=['GET', 'POST'])
def authorize():
    return render_template('auth/authorize.html',cities = cities)


@login_required
@auth.route('/query_all_data', methods=['POST','GET'])
@auth.route('/query_all_data/<string:from_city>', methods=['POST','GET'])
def query_all_data(from_city = None):
    user_name = current_user.username
    if user_name == 'admin':
        task_client = current_app.task_client
        user_name = current_user.username
        ss = task_client.get_session()
        args = {'from_city':from_city} if from_city else {}
        cursor = ss.query(task_client.table_struct).filter_by(task_id = '',**args)\
                                                    .order_by(desc(task_client.table_struct.submit_date))\
                                                    .order_by(desc(task_client.table_struct.submit_time))\
                                                    .all()
        ss.close()
        tbvals = []
        colnames = task_client.get_column_names(task_client.table_struct)
        for record in cursor:
            new_dict = {colname:getattr(record, colname) for colname in colnames}
            new_dict['datetime'] = '-'.join((str(new_dict['submit_date']),timeint2str(new_dict['submit_time'])))
            new_dict.pop('submit_date')
            new_dict.pop('submit_time')
            tbvals.append(new_dict)
        print tbvals
        return jsonify(tbvals)
    else:
        return jsonify({})


def load_json_data(form):
    dict_request_form = dict(form)
    indata_json = {
        key: dict_request_form[key][0]
                for key in dict_request_form
    }['data']
    indata = unicode2utf8_r(json.loads(indata_json))
    return indata
    
@login_required
@auth.route('/accept_task', methods=['POST',])
def accept_task():
    task_client = current_app.task_client 
    indata = load_json_data(request.form)
    for primary_key in indata:
        ss = task_client.get_session()
        record = ss.query(task_client.table_struct).filter_by(index = primary_key).scalar()
        params = record.params.split('|')
        new_task = current_app.rpc_client[record.task_name].delay(record.orgnization,*params)
        record.task_id = new_task.id
        ss.commit()
    return jsonify(success=1)       

@login_required
@auth.route('/deny_task', methods=['POST',])
def deny_task():
    task_client = current_app.task_client 
    indata = load_json_data(request.form)
    for primary_key in indata:
        ss = task_client.get_session()
        record = ss.query(task_client.table_struct).filter_by(index = primary_key).scalar()
        record.task_id = "-1"
        ss.commit()
    return jsonify(success=1)

######################################################################################
#this is self-defined by module developer
@login_required
@auth.route('/query_result/<string:task_id>', methods=['GET', 'POST'])
def query_result(task_id):
    redis_client = current_app.redis_client
    task_block = redis_client.get_value_by_id(task_id)
    taskvals = json.loads(task_block['result'])['result']
    return render_template('auth/query_result.html',taskvals = taskvals)



