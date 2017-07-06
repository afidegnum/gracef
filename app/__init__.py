import logging
import os
import shutil


import jinja2
from dirtools import Dir
from flask import Flask, redirect, url_for, g, render_template
from flask_appbuilder import SQLA, AppBuilder, IndexView, expose, BaseView

from app.models import Page

"""
 Logging configuration
"""

# This allows to create a hash directory for ckeditor but we need to correct the unessary creation of junk files.

class AssetDirTree(object):
    def __init__(self, app, src, dst):
        """src is absolute and dst is relative to the app's static_folder """
        static_folder = app.static_folder
        # Add "cache busting" without flask.assets
        abs_src = os.path.join(static_folder, src)
        abs_dst = os.path.join(static_folder, dst)

        directory = Dir(abs_src)
        #####################################################
        # Make sure the destination directory is different if
        # any of the files has changed
        # This is a form of cache busting.
        #####################################################
        # - get a hash of the directory;
        # - take only first 16 hex digits (= 16*16 bits)
        uniq = directory.hash()[:16]

        dst_dirtree_relpath = os.path.join(dst, uniq)
        dst_dirtree_abspath = os.path.join(static_folder, dst_dirtree_relpath)

        if not os.path.exists(dst_dirtree_abspath):
            shutil.copytree(abs_src, dst_dirtree_abspath)

        self.dst_url = dst_dirtree_relpath

def configure_ckeditor(app):
    ckeditor = AssetDirTree(app,
                            app.config['CKEDITOR_SRC'],
                            app.config['CKEDITOR_DST'])


    @app.context_processor
    def inject():
        return dict(
          ckeditor_main_filename=os.path.join(ckeditor.dst_url, 'ckeditor.js'))

    return ckeditor

#
#
# class NewIndexView(BaseView):
#     route_base = ''
#     default_view = 'index'
#
#     @expose('/')
#     def index(self):
#         # This method redirects the user to a different page depending on
#         # whether the user is authenticated or not:
#         self.update_redirect
#         if g.user is not None and g.user.is_authenticated():
#             if g.user.role.name != app.config['AUTH_ROLE_PUBLIC']:
#                 return redirect(url_for('UserDBModelView.show', pk=g.user.id))
#         else:
#             return redirect(url_for('PublicView.home'))

class MyIndex(IndexView):
    index_template = 'grace/index.html'
    default_view = 'about'

    @expose('/')
    def index(self):
        return self.render_template(self.index_template)

    @expose('/about')
    def about(self):
        return self.render_template('grace/about.html')

    @expose('/events')
    def events(self):
        return self.render_template('grace/events.html')

    @expose('/contact')
    def contact(self):
        return self.render_template('grace/contacts.html')


    @expose('/volunteer')
    def volunteer(self):
        return self.render_template('grace/volunteer.html')


    @expose('/donate')
    def donate(self):
        return self.render_template('grace/donate.html')



logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object('config')
db = SQLA(app)
appbuilder = AppBuilder(app, db.session, static_url_path='/static', indexview=MyIndex)




"""
from sqlalchemy.engine import Engine
from sqlalchemy import event

#Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""

def show_all_attrs(value):
    res = []
    for k in dir(value):
        res.append('\n %r %r\n' % (k, getattr(value, k)))
    return '\n'.join(res)


# print all available jinja variables and attributes

@jinja2.contextfunction
def get_context(c):
    return c

app.jinja_env.globals['context'] = get_context
app.jinja_env.globals['callable'] = callable
app.jinja_env.filters['show_all_attrs'] = show_all_attrs

ckeditor = configure_ckeditor(app)
from app import views


