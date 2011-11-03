# -*- coding: utf-8 -*-

from gluon.custom_import import track_changes; track_changes(True)

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

from cms_settings import cfg_parser
main_cfg = cfg_parser('cms-settings', force_reload=True)

db_connection_url = main_cfg.getd('database','connection_url')
db = DAL(db_connection_url)

#if not request.env.web2py_runtime_gae:     
#    ## if NOT running on Google App Engine use SQLite or other DB
#    db = DAL('sqlite://storage.sqlite')
#else:
#    ## connect to Google BigTable (optional 'google:datastore://namespace')
#    db = DAL('google:datastore') 
#    ## store sessions and tickets there
#    session.connect(request, response, db = db) 
#    ## or store session in Memcache, Redis, etc.
#    ## from gluon.contrib.memdb import MEMDB
#    ## from google.appengine.api.memcache import Client
#    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key()) 
crud, service, plugins = Crud(db), Service(), PluginManager()

## @see: http://www.web2py.com/book/default/chapter/08#Authorization-and-CRUD
## "Another way to implement access control is to always use CRUD
## (as opposed to SQLFORM) to access the database and to ask CRUD to enforce
## access control on database tables and records."
## This is done by linking Auth and CRUD with the following statement: 
#crud.settings.auth = auth

## create all tables needed by auth if not custom tables
auth.define_tables()

## configure email
mail=auth.settings.mailer
#mail.settings.server = 'logging' or 'smtp.gmail.com:587'
#mail.settings.sender = 'you@gmail.com'
#mail.settings.login = 'username:password'
mail.settings.server = main_cfg.getd('mail','server')
mail.settings.sender = main_cfg.getd('mail','sender')
mail.settings.login = main_cfg.getd('mail','login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
#from gluon.contrib.login_methods.rpx_account import use_janrain
#use_janrain(auth,filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

#db.auth_user.format = lambda x: '%(first_name)s %(last_name)s' % x

import cms_settings

## Table: node =================================================================
## Used to store actual content

db.define_table(
    'node',
    Field('type', 'string', length=128, required=True, requires=IS_NOT_EMPTY()),
    Field('title', 'string', length=256, required=True, requires=IS_NOT_EMPTY()),
    Field('body', 'text'),
    Field('body_format', 'string', length=256),
    Field('created', 'datetime', default=request.now, required=True),
    Field('updated', 'datetime', update=request.now, required=True),
    Field('author', db.auth_user, default=auth.user_id, required=True),
    Field('published', 'boolean', default=True),
    Field('weight', 'integer', default=0),
    )

db.node.body_format.requires = IS_IN_SET(
    dict([(k,v['label']) for k,v in cms_settings.list_text_formats().items()]))
db.node.created.requires = IS_DATETIME(T('%Y-%m-%d %H:%M:%S'))    
db.node.updated.requires = IS_DATETIME(T('%Y-%m-%d %H:%M:%S'))
db.node.author.requires = IS_IN_DB(db, db.auth_user.id, '%(first_name)s %(last_name)s [#%(id)d]')
db.node.author.represent = lambda x,y=None: '%(first_name)s %(last_name)s' % x
db.node.weight.requires = IS_INT_IN_RANGE(-50, 50)

## Table: block ================================================================
db.define_table(
    'block',
    Field('type', 'string', length=128, required=True, default='custom'),
    Field('title', 'string', length=256, required=True, requires=IS_NOT_EMPTY()),
    Field('body', 'text'),
    Field('body_format', 'string', length=256),
    Field('weight', 'integer', default=0),
    Field('region', 'string', length=128),
    )


## Table: variable =============================================================
## Used to store configuration variables, as pickled values

db.define_table(
    'variable',
    Field('var_name', 'string', length=256, required=True, unique=True),
    Field('var_value_pickled', 'text'), ## pickled value
    )

#import pickle
#class VirtualFields_variable(object):
#    def var_value(self):
#        return pickle.loads(self.variable.var_value_pickled)
#db.variable.virtualfields.append(VirtualFields_variable())
