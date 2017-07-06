import os
import traceback

from flask_appbuilder.fieldwidgets import BS3TextAreaFieldWidget
from wtforms import TextAreaField

from app import appbuilder, db
import datetime
import simplejson
from flask import render_template, request, url_for,  g, current_app
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, AppBuilder, expose, has_access, BaseView, IndexView
from flask_wtf import csrf
from flask_wtf.csrf import generate_csrf
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename, redirect


from .models import About, News, Activity, Message, Media, Pageblock, Pageregion, Page

from flask_appbuilder.widgets import ListThumbnail, ListItem, ListBlock, ShowWidget
from flask_appbuilder.filemanager import uuid_namegen, thumbgen_filename, ImageManager, FileManager
from flask_appbuilder.upload import ImageUploadField
from PIL import Image, ImageOps
from datetime import datetime



import config


class CKTextAreaWidget(BS3TextAreaFieldWidget):
    def __call__(self, field, **kwargs):
        # kwargs.setdefault('class_', 'ckeditor')
        kwargs['class'] = 'ckeditor'
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget

#
# class MediaView(ModelView):
#
#     datamodel = SQLAInterface(Media)
#
#     list_widget = ListBlock
#
#
#
#     list_columns = ['photo_img_thumbnail']
#
#
#
#     add_fieldsets = [('Media', {'fields': ['photo',  'name']})]
#
#     edit_fieldsets = [
#         ('Media', {'fields': [ 'news']})
#     ]





class MyMediaView(ModelView):
    datamodel = SQLAInterface(Media)
    add_template = 'media_add.html'

    list_columns = ['activities_id','messages_id', 'blocks_id', 'news_id', 'name']
    list_widget = ListThumbnail
    add_widget = ShowWidget
    include_cols = ['activities_id','messages_id','blocks_id' ,'news_id', 'name']
    value_columns = ['activities_id','messages_id','blocks_id' ,'news_id', 'name']
    add_columns = ['activities_id','messages_id','blocks_id' ,'news_id', 'name']




    @expose('/upload',  methods=['POST'])
    def upload_img(self):

        im = ImageManager()
        files = request.files['files']
        media = Media()

        filelist = []
        # sname = str(files)
        # imgsize = im.resize(files, (200, 100, True))
        if files:
            newname = im.generate_name(None, files)
            mpath = config.IMG_UPLOAD_FOLDER + '/' + newname
            im.save_file(files, mpath, thumbnail_size=(75, 50, True), size=(1225, 750, True))
            media.name = newname

            fpath = self.appbuilder.static_url_path + '/uploads/images/' + newname
            files, file_extension = os.path.splitext(fpath)
            th = files + '_thumb' + file_extension

            db.session.add(media)
            db.session.commit()

            size = os.path.getsize(mpath)
            json_display = {'name': newname, "thumbnailUrl": th, 'deleteUrl': 'delete/' + newname, 'size': size}
            filelist.append(json_display)

        return simplejson.dumps({"files": filelist})

    @expose('/upload', methods=['GET'])
    def show_images(self):

        thumbs = ImageManager()

        thumbs.relative_path = 'static/uploads/images/'

        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        # print SITE_ROOT
        paths = os.path.join(current_app.root_path, current_app.static_folder, 'uploads/images')
        print current_app.static_folder
        # print paths

        files = [thumbs.get_url(f) for f in os.listdir(config.IMG_UPLOAD_FOLDER) if
                 os.path.isfile(os.path.join(config.IMG_UPLOAD_FOLDER, f))]
        myfiles = self.appbuilder.get_session.query(Media).all()
        print self.appbuilder.static_url_path

        file_display = []



        for f in myfiles:


            fl = f.name

            # fpath = os.path.join(config.IMG_UPLOAD_FOLDER, fl)
            fpath = self.appbuilder.static_url_path + '/uploads/images/' + fl
            files, file_extension = os.path.splitext(fpath)
            th = files + '_thumb' + file_extension
            # size = os.path.getsize(os.path.join('/home/afidegnum/PycharmProjects/myfab/app/', f))
            # furl = os.path.getsize(os.path.join('/home/afidegnum/PycharmProjects/myfab/app/', f))
            json_display = {"deleteType": "DELETE", 'name': fl, 'url': self.appbuilder.static_url_path + '/uploads/images/' + fl, 'thumbnailUrl': th, 'deleteUrl': 'delete/' + fl, 'size': 888}

            # file_saved = uploadfile(name=f, size=size)
            # file_saved.url = config.NEUTRAL_PATH + f
            file_display.append(json_display)


        return simplejson.dumps({"files": file_display})

    @expose("/delete/<string:filename>", methods=['DELETE'])
    def evaporate(self, filename):

        # fpath = self.appbuilder.static_url_path + '/uploads/images/' + filename
        fpath = os.path.join(config.IMG_UPLOAD_FOLDER, filename)
        files, file_extension = os.path.splitext(fpath)
        th = files + '_thumb' + file_extension
        # th = fpath.split(suffix, 1)[0]

        print th, fpath

        if os.path.exists(fpath):
            try:
                os.remove(fpath)

                self.appbuilder.get_session.query(Media).filter_by(name=filename).delete()
                self.appbuilder.get_session.commit()


                if os.path.exists(th):
                    os.remove(th)

                jconfirm = simplejson.dumps({filename: 'True'})
            except:
                jconfirm = simplejson.dumps({filename: 'False'})
        return simplejson.dumps({filename: 'False'})



class AboutView(ModelView):
    datamodel = SQLAInterface(About)

class MyShowWidget(ShowWidget):
    template = 'editable/plain_show.html'

# web page structure where wee have page, regions and blocks hierarchycally displayed.


class PageblockView(ModelView):
    datamodel = SQLAInterface(Pageblock)

class PageregionView(ModelView):
    datamodel = SQLAInterface(Pageregion)
    related_views = [PageblockView]
    show_columns = ['name', 'listname']


class PageView(ModelView):
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
    # index_template = 'sample_theme/index.html'




class NewsView(ModelView):
    datamodel = SQLAInterface(News)

    list_columns = ['name','posted_date']
    add_columns = ['name', 'body']
    # label_columns = {'name':'News Title', 'posted_date':'Posted On', 'media':'Gallery'}
    related_views = [MyMediaView]

    # add_fieldsets = [
    #     ('Media', {'fields': ['Media.photo']})
    # ]



class ActivityView(ModelView):
    datamodel = SQLAInterface(Activity)
    list_columns = ['name', 'start_date', 'end_date']
    related_views = [MyMediaView]
    list_widget = ListThumbnail




class MessageView(ModelView):

    datamodel = SQLAInterface(Message)
    list_columns = ['name', 'posted']
    related_views = [MyMediaView]
    list_widget = ListThumbnail


class SiteFrameView(BaseView):
    default_view = 'navigate'
    @expose('/navigate')
    def navigate(self):
        item = db.session.query(Page).filter_by(id=1).first()
        return render_template('pages.html', items=item)

db.create_all()

appbuilder.add_view(AboutView, "About", icon="fa-folder-open-o", category="Admin")
appbuilder.add_view(SiteFrameView, "Site Frame", icon="fa-folder-open-o", category="Admin")
appbuilder.add_view(NewsView, "News", icon="fa-folder-open-o", category="Admin")
appbuilder.add_view(ActivityView, "Activities", icon="fa-folder-open-o", category="Admin")
appbuilder.add_view(MessageView, "Messages", icon="fa-folder-open-o", category="Admin")
appbuilder.add_view(MyMediaView, "MyMedia", icon="fa-folder-open-o", category="Admin")
appbuilder.add_view(PageView, "Pages", icon="fa-folder-open-o", category="Admin")
appbuilder.add_view(PageregionView, "Regions", icon="fa-folder-open-o", category="Admin")
appbuilder.add_view(PageblockView, "Blocks", icon="fa-folder-open-o", category="Admin")


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404