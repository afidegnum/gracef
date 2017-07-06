from flask_appbuilder import ModelView, IndexView
from flask_appbuilder.models.sqla.interface import SQLAInterface

from app.models import Page
from app.views import PageregionView, MyShowWidget


class PageView(ModelView, IndexView):
    datamodel = SQLAInterface(Page)
    related_views = [PageregionView]
    # page = Page()
    show_widget = MyShowWidget
    # current_page = appbuilder.session.query(Page).all()
    # extra_args = {'rich_textareas': ['body'], 'current_page': current_page}
    extra_args = {'rich_textareas': ['body']}
    add_template = 'richtxt/add.html'
    edit_template = 'richtxt/edit.html'
    show_template = 'editable/ajax_show.html'
    add_columns = ['title', 'tag', 'body']
    edit_columns = ['title', 'tag', 'body']
    show_columns = ['titles', 'tags', 'bodies', 'blocklist']
    index_template = 'sample_theme/index.html'