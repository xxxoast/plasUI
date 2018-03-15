#coding:utf-8    
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
                        DateField, RadioField, SelectField, SelectMultipleField, IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User
from .. import ufile
from ..misc import unicode2utf8

class LoginForm(FlaskForm):

    username = StringField(u'姓名', validators=[Required(), Length(1, 64)])
    password = PasswordField(u'密码', validators=[Required(), Length(1, 64)])
    submit_login = SubmitField(u'登录')

class TaskItemForm(FlaskForm):
    
    item  = SelectField(u'检查模块',choices = [('merchant',u'收单商户二清'),\
                                             ('reserve',u'备付金出入金'),\
                                             ('diff_data',u'数据比对'),\
                                             ('data_request',u'数据请求')],\
                                 default = 'merchant')
    destination = SelectField(u'检查地区',choices = [('beijing',u'北京'),('shanghai',(u'上海')),('shenzhen',(u'深圳'))],\
                                 default = 'beijing')
    start_date = IntegerField(u'起始日期',id='start_date', validators=[Required()],\
                                render_kw={'placeholder': '20170101'},default=20170101)
    end_date = IntegerField(u'结束日期',id='end_date',validators=[Required()],\
                                render_kw={'placeholder': '20180101'},default=20180101) 
    organization = SelectField(u'检查机构',choices = [('pingan_b',(u'平安银行')),('alipay_p',u'民生银行'),('unionpay_p',(u'银联商务'))],\
                                 default = 'minsheng_b')
    branch    = SelectField(u'机构层级',choices = [('super',(u'法人')),('branch',(u'所在地分支机构'))],\
                                 default = 'super')
    submit_task_item = SubmitField(u'下一步')

class TaskMerchantParamsForm(FlaskForm):
    
    param1  = SelectField(u'参数1：检查维度',choices = [('merchant',(u'商户')),('trade',(u'交易明细'))],\
                                 default = 'merchant')
    param2  = SelectField(u'参数2：交易金额临界值',choices = [('10000',(u'1万元')),('100000',(u'10万元'))],\
                                 default = '100000')
    submit_task_params = SubmitField(u'下一步')
    
class TaskReserveParamsForm(FlaskForm):
    
    param1  = SelectField(u'参数1：检查项目',choices = [('ratio',(u'缴存比例')),\
                                                  ('account',(u'账户开立')),\
                                                  ('in_and_out',(u'出入金规范'))],\
                                 default = 'ratio')

    submit_task_params = SubmitField(u'下一步')

class TaskDataRequestParamsForm(FlaskForm):
    
    param1  = SelectField(u'参数1：数据内容',choices = [('merchant',(u'商户信息')),\
                                                    ('trade',(u'交易流水')),\
                                                    ('account',(u'支付账户'))],\
                                 default = 'merchant')

    submit_task_params = SubmitField(u'下一步')
    
class TaskSubmitForm(FlaskForm):
    
    submit_task = SubmitField(u'提交') 
    
###################################################
module2form = {}
module2form['merchant'] = TaskMerchantParamsForm
module2form['reserve'] = TaskReserveParamsForm
module2form['data_request'] = TaskDataRequestParamsForm