import datetime

from flask import url_for
from flask_appbuilder import Model
from flask_appbuilder.filemanager import ImageManager
from flask_appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from markupsafe import Markup
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from jinja2 import Template


def today():
    return datetime.datetime.today()


# custom model queries for baseviews and custom views to override the ModelView query with widgets.


class Pageblock(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    body = Column(Text, unique=True, nullable=False)
    region_id = Column(Integer, ForeignKey('pageregion.id'), nullable=True)
    region = relationship("Pageregion")

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


# Applying model relations on individual methods. from the Page Class
# TODO x-editable does not activate at the last row of Pageblocks. Shift to themefile instead?

class Page(Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(50), unique=True, nullable=False)
    tag = Column(String(50), unique=True, nullable=False, index=True)
    body = Column(Text, unique=True, nullable=False)
    region = relationship("Pageregion")

    def __repr__(self):
        return self.title

    def __str__(self):
        return self.title

    def titles(self):
        title = self.title
        template = Template("""
<a href="#" id="titles" class="list-group-item list-group-item-action flex-column align-items-start" data-type="text" data-pk="region" data-url="/editDesc" data-title="Edit Description"> {{title}} </a> </li>
        """)
        return Markup(template.render(title=title))

    def tags(self):
        title = self.tag
        template = Template("""
<a href="#" id="tags" class="list-group-item list-group-item-action flex-column align-items-start" data-type="text" data-pk="region" data-url="/editDesc" data-title="Edit Description"> {{title}} </a> <br>
        """)
        return Markup(template.render(title=title))

    def bodies(self):
        title = self.body
        template = Template("""
<a href="#" id="bodies" class="list-group-item list-group-item-action flex-column align-items-start" data-type="text" data-pk="region" data-url="/editDesc" data-title="Edit Description"> {{title}} </a> <br>
        """)
        return Markup(template.render(title=title))



    def positions(self):
        for c in self.region:
            yield """<a href="#" id="region" class="list-group-item list-group-item-action flex-column align-items-start active" data-type="text" data-pk="region" data-url="/editDesc" data-title="Edit Description"> %s </a>""" %(c)
            for b in c.blocks:
                yield """<a href="#" id="blocks" class="list-group-item list-group-item-action flex-column align-items-start" data-type="text" data-pk="region" data-url="/editDesc" data-title="Edit Description"> %s </a> """ %(b)


    def blocklist(self):
        listing = self.positions()

        template = Template("""
        
        {%for items in listing%}
        {{items}}
        {%endfor%}
        
        """)
        return Markup(template.render(listing=listing))


    def pos(self):
        regions = self.region
        template = Template("""
        {%for items in regions%}
        <a href="#" id="region" class="list-group-item list-group-item-action flex-column align-items-start" data-type="text" data-pk="region" data-url="/editDesc" data-title="Edit Description">{{items}}</a>
        {%endfor%}
        """)
        return Markup(template.render(regions=regions))



class Pageregion(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    pg_id = Column(Integer, ForeignKey('page.id'), nullable=True)
    blocks = relationship("Pageblock")
    page = relationship("Page")

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def listname(self):
        return self.name

    def listid(self):
        return self.id




class Media(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=True)
    # path = Column(String(250), unique=True, nullable=True)
    photo = Column(ImageColumn(thumbnail_size=(30, 30, True), size=(300, 300, True)))
    # posted = Column(Date, default=today, nullable=False)
    news = relationship("News")
    news_id = Column(Integer, ForeignKey('news.id'), nullable=True)
    activities = relationship("Activity")
    activities_id = Column(Integer, ForeignKey('activity.id'), nullable=True)
    messages = relationship("Message")
    messages_id = Column(Integer, ForeignKey('message.id'), nullable=True)
    blocks = relationship("Pageblock")
    blocks_id = Column(Integer, ForeignKey('pageblock.id'), nullable=True)

    def photo_img(self):
        im = ImageManager()
        if self.name:
            return Markup('<a href="' + url_for('MediaView.show', pk=str(self.id)) +
                          '" class="thumbnail"><img src="' + im.get_url(self.photo) +
                          '" alt="Photo" class="img-rounded img-responsive"></a>')
        else:
            return Markup('<a href="' + url_for('MediaView.show', pk=str(self.id)) +
                          '" class="thumbnail"><img src="//:0" alt="Photo" class="img-responsive"></a>')

    def photo_img_thumbnail(self):
        im = ImageManager()
        if self.name:
            return Markup('<a href="' + url_for('MediaView.show', pk=str(self.id)) +
                          '" class="thumbnail"><img src="' + im.get_url_thumbnail(self.photo) +
                          '" alt="Photo" class="img-rounded img-responsive"></a>')
        else:
            return Markup('<a href="' + url_for('MediaView.show', pk=str(self.id)) +
                          '" class="thumbnail"><img src="//:0" alt="Photo" class="img-responsive"></a>')

    def __repr__(self):
        return self.name


class About(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    body = Column(Text, unique=True, nullable=False)

    def __repr__(self):
        return self.name


class News(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    body = Column(Text, unique=True, nullable=False)
    posted_date = Column(Date, default=today(), nullable=False)


class Activity(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    body = Column(Text, unique=True, nullable=False)
    start_date = Column(Date, default=today, nullable=False)
    end_date = Column(Date, nullable=True)

    def __repr__(self):
        return self.name

class Message(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    body = Column(Text, unique=True, nullable=False)
    posted = Column(Date, default=today, nullable=False)

    def __repr__(self):
        return self.name