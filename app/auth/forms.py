#coding:utf-8    
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
                        DateField, RadioField, SelectField, SelectMultipleField, IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User
from .. import ufile
from docutils.nodes import organization
from ..misc import unicode2utf8

class LoginForm(FlaskForm):

    username = StringField('UserName', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required(), Length(1, 64)])
    submit_login = SubmitField('Log In')

class TaskItemForm(FlaskForm):
    
    item  = SelectField('item',choices = [('merchant',u'收单商户二清'),('personal_account_classify',u'个人结算账户分类')],\
                                 default = 'merchant')
    destination = SelectField('destination',choices = [('beijing',u'北京'),('shanghai',(u'上海')),('shenzhen',(u'深圳'))],\
                                 default = 'beijing')
    start_date = IntegerField('start_date',id='start_date', validators=[Required()],\
                                render_kw={'placeholder': '20170101'},default=20170101)
    end_date = IntegerField('end_date',id='end_date',validators=[Required()],\
                                render_kw={'placeholder': '20180101'},default=20180101) 
    organization = SelectField('organization',choices = [('minsheng_b',(u'平安银行')),('alipay_p',u'民生银行'),('unionpay_p',(u'银联商务'))],\
                                 default = 'minsheng_b')
    branch    = SelectField('branch',choices = [('super',(u'法人')),('branch',(u'所在地分支机构'))],\
                                 default = 'super')
    submit_task_item = SubmitField('Next Step')

class TaskMerchantParamsForm(FlaskForm):
    
    param1  = SelectField('type',choices = [('merchant',(u'商户')),('trade',(u'交易明细'))],\
                                 default = 'merchant')
    submit_task_params = SubmitField('Next Step')
    
class TaskSubmitForm(FlaskForm):
    
    submit_task = SubmitField('Submit') 
