#!flask/bin/python

# Author: Ngo Duy Khanh
# Email: ngokhanhit@gmail.com
# Git repository: https://github.com/ngoduykhanh/flask-file-uploader
# This work based on jQuery-File-Upload which can be found at https://github.com/blueimp/jQuery-File-Upload/

import os
import PIL
from PIL import Image
import simplejson
import traceback

from flask import g
from flask import session

from core.media import media
from core import ALLOWED_EXTENSIONS, IGNORED_FILES
from flask import request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

# from core.media.model import Media
from lib.upload_file import uploadfile
from core import app, db, ghana
from datetime import datetime

medi = ghana.edge_collection('mediaof')
art = ghana.edge_collection('articlemedia')




def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def gen_file_name(filename):
    """
    If file was exist already, rename it and return a new name
    """

    i = 1
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        name, extension = os.path.splitext(filename)
        filename = '%s_%s%s' % (name, str(i), extension)
        i = i + 1

    return filename


def create_thumbnai(image):
    try:
        basewidth = 80
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], image))
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
        img.save(os.path.join(app.config['THUMBNAIL_FOLDER'], image))

        return True

    except:
        print traceback.format_exc()
        return False

# this one ?
@media.route("/upload", methods=['GET', 'POST'])
def upload():


    if request.method == 'POST':
        file = request.files['file']
        # print request.view_args
        # print request.args['myrequests']
        # print request.args.get('blogsource')
        # print request.form['blogsource']
        g.source = request.form['blogsrc'] if request.form['blogsrc'] else None
        g.acs = request.form['acs'] if request.form['acs'] else None
        # print request.args
        # print request.form
        # print request.values


        #pprint (vars(objectvalue))

        if file:
            filename = secure_filename(file.filename)
            filename = gen_file_name(filename)
            mimetype = file.content_type


            if not allowed_file(file.filename):
                result = uploadfile(name=filename, type=mimetype, size=0, not_allowed_msg="Filetype not allowed")

            else:
                # save file to disk
                uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(uploaded_file_path)
                target_media = {
                    "filename": filename,
                    "time": datetime.utcnow().isoformat()

                }

                amedia = ghana.vertex_collection('media')

                amed = amedia.insert(target_media)

                if g.acs:
                    medi.insert({'_from': 'activities/' + g.acs, '_to': 'media/' + str(amed['_key'])})

                if g.source:
                    art.insert({'_from': 'articles/' + g.source, '_to': 'media/' + str(amed['_key'])})



                # media = Media(name=filename, blogs=g.source)
                # db.session.add(media)
                # db.session.commit()


                # create thumbnail after saving
                if mimetype.startswith('image'):
                    create_thumbnai(filename)

                # get file size after saving
                size = os.path.getsize(uploaded_file_path)

                # return json for js call back
                result = uploadfile(name=filename, type=mimetype, size=size)

            return simplejson.dumps({"files": [result.get_file()]})

    if request.method == 'GET':

        # get all file in ./data directory
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'],f)) and f not in IGNORED_FILES ]

        file_display = []

        for f in files:
            size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f))
            file_saved = uploadfile(name=f, size=size)
            file_display.append(file_saved.get_file())

        return simplejson.dumps({"files": file_display})

    return redirect(url_for('index'))


@media.route("/delete/<string:filename>", methods=['DELETE'])
def delete(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], filename)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            db.session.query(Media).filter_by(name=filename).delete()
            db.session.commit()

            if os.path.exists(file_thumb_path):
                os.remove(file_thumb_path)

            return simplejson.dumps({filename: 'True'})
        except:
            return simplejson.dumps({filename: 'False'})


# serve static files
@media.route("/thumbnail/<string:filename>", methods=['GET'])
def get_thumbnail(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename=filename)


@media.route("/data/<string:filename>", methods=['GET'])
def get_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename=filename)

#ok lets see
@media.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index_old.html')

#
# if __name__ == '__main__':
#     app.run(debug = True, port=9191)