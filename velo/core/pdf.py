from django.conf import settings
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, cm
from reportlab.platypus import Image
from reportlab.lib.colors import black
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import utils


__version__=''' $Id$ '''
__doc__='''Classes for ParagraphStyle and similar things.

A style is a collection of attributes, but with some extra features
to allow 'inheritance' from a parent, and to ensure nobody makes
changes after construction.

ParagraphStyle shows all the attributes available for formatting
paragraphs.

getSampleStyleSheet()  returns a stylesheet you can use for initial
development, with a few basic heading and text styles.
'''

__all__ = (
        'PropertySet',
        'ParagraphStyle',
        'LineStyle',
        'ListStyle',
        'StyleSheet1',
        'getSampleStyleSheet',
        )

_baseFontName = "Ubuntu"
_baseFontNameB = "UbuntuB"
_baseFontNameI = "Ubuntu"
_baseFontNameBI = "Ubuntu"

if not 'Ubuntu' in pdfmetrics._fonts:
    pdfmetrics.registerFont(TTFont('Ubuntu', os.path.join(str(settings.APPS_DIR), 'static', 'assets', 'Ubuntu-R.ttf')))

if not 'UbuntuB' in pdfmetrics._fonts:
    pdfmetrics.registerFont(TTFont('UbuntuB', os.path.join(str(settings.APPS_DIR), 'static', 'assets', 'Ubuntu-B.ttf')))


def get_image(path, width=1*cm):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))


###########################################################
# This class provides an 'instance inheritance'
# mechanism for its descendants, simpler than acquisition
# but not as far-reaching
###########################################################
class PropertySet:
    defaults = {}

    def __init__(self, name, parent=None, **kw):
        """When initialized, it copies the class defaults;
        then takes a copy of the attributes of the parent
        if any.  All the work is done in init - styles
        should cost little to use at runtime."""
        # step one - validate the hell out of it
        assert 'name' not in self.defaults, "Class Defaults may not contain a 'name' attribute"
        assert 'parent' not in self.defaults, "Class Defaults may not contain a 'parent' attribute"
        if parent:
            assert parent.__class__ == self.__class__, "Parent style %s must have same class as new style %s" % (parent.__class__.__name__,self.__class__.__name__)

        #step two
        self.name = name
        self.parent = parent
        self.__dict__.update(self.defaults)

        #step two - copy from parent if any.  Try to be
        # very strict that only keys in class defaults are
        # allowed, so they cannot inherit
        self.refresh()
        self._setKwds(**kw)

    def _setKwds(self,**kw):
        #step three - copy keywords if any
        for (key, value) in kw.items():
             self.__dict__[key] = value

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.name)

    def refresh(self):
        """re-fetches attributes from the parent on demand;
        use if you have been hacking the styles.  This is
        used by __init__"""
        if self.parent:
            for (key, value) in self.parent.__dict__.items():
                if (key not in ['name','parent']):
                    self.__dict__[key] = value

    def listAttrs(self, indent=''):
        print(indent + 'name =', self.name)
        print(indent + 'parent =', self.parent)
        keylist = self.__dict__.keys()
        keylist.sort()
        keylist.remove('name')
        keylist.remove('parent')
        for key in keylist:
            value = self.__dict__.get(key, None)
            print(indent + '%s = %s' % (key, value))

    def clone(self, name, parent=None, **kwds):
        r = self.__class__(name,parent)
        r.__dict__ = self.__dict__.copy()
        r.parent = parent is None and self or parent
        r._setKwds(**kwds)
        return r

class ParagraphStyle(PropertySet):
    defaults = {
        'fontName':_baseFontName,
        'fontSize':10,
        'leading':12,
        'leftIndent':0,
        'rightIndent':0,
        'firstLineIndent':0,
        'alignment':TA_LEFT,
        'spaceBefore':0,
        'spaceAfter':0,
        'bulletFontName':_baseFontName,
        'bulletFontSize':10,
        'bulletIndent':0,
        #'bulletColor':black,
        'textColor': black,
        'backColor':None,
        'wordWrap':None,
        'borderWidth': 0,
        'borderPadding': 0,
        'underlineProportion': 0.05,
        'borderColor': None,
        'borderRadius': None,
        'allowWidows': 1,
        'allowOrphans': 0,
        'justifyLastLine': 0,
        'justifyBreaks': 0,
        'textTransform':None,   #uppercase lowercase (captitalize not yet) or None or absent
        'endDots':None,         #dots on the last line of left/right justified paras
                                #string or object with text and optional fontName, fontSize, textColor & backColor
                                #dy
        'splitLongWords':1,     #make best efforts to split long words
        'spaceShrinkage': 0.05,
        }


class LineStyle(PropertySet):
    defaults = {
        'width':1,
        'color': black
        }
    def prepareCanvas(self, canvas):
        """You can ask a LineStyle to set up the canvas for drawing
        the lines."""
        canvas.setLineWidth(1)
        #etc. etc.

class ListStyle(PropertySet):
    defaults = dict(
                leftIndent=18,
                rightIndent=0,
                bulletAlign='left',
                bulletType='1',
                bulletColor=black,
                bulletFontName='Helvetica',
                bulletFontSize=12,
                bulletOffsetY=0,
                bulletDedent='auto',
                bulletDir='ltr',
                bulletFormat=None,
                start=None,         #starting value for a list
                )

_stylesheet1_undefined = object()

class StyleSheet1:
    """
    This may or may not be used.  The idea is to:

    1. slightly simplify construction of stylesheets;

    2. enforce rules to validate styles when added
       (e.g. we may choose to disallow having both
       'heading1' and 'Heading1' - actual rules are
       open to discussion);

    3. allow aliases and alternate style lookup
       mechanisms

    4. Have a place to hang style-manipulation
       methods (save, load, maybe support a GUI
       editor)

    Access is via getitem, so they can be
    compatible with plain old dictionaries.
    """

    def __init__(self):
        self.byName = {}
        self.byAlias = {}

    def __getitem__(self, key):
        try:
            return self.byAlias[key]
        except KeyError:
            try:
                return self.byName[key]
            except KeyError:
                raise KeyError("Style '%s' not found in stylesheet" % key)

    def get(self,key,default=_stylesheet1_undefined):
        try:
            return self[key]
        except KeyError:
            if default!=_stylesheet1_undefined: return default
            raise

    def __contains__(self, key):
        return key in self.byAlias or key in self.byName

    def has_key(self,key):
        return key in self

    def add(self, style, alias=None):
        key = style.name
        if key in self.byName:
            raise KeyError("Style '%s' already defined in stylesheet" % key)
        if key in self.byAlias:
            raise KeyError("Style name '%s' is already an alias in stylesheet" % key)

        if alias:
            if alias in self.byName:
                raise KeyError("Style '%s' already defined in stylesheet" % alias)
            if alias in self.byAlias:
                raise KeyError("Alias name '%s' is already an alias in stylesheet" % alias)
        #passed all tests?  OK, add it
        self.byName[key] = style
        if alias:
            self.byAlias[alias] = style

    def list(self):
        styles = sorted(self.byName.items())
        alii = {}
        for (alias, style) in self.byAlias.items():
            alii[style] = alias
        for (name, style) in styles:
            alias = alii.get(style, None)
            print(name, alias)
            style.listAttrs('    ')


def testStyles():
    pNormal = ParagraphStyle('Normal',None)
    pNormal.fontName = _baseFontName
    pNormal.fontSize = 12
    pNormal.leading = 14.4

    pNormal.listAttrs()
    pPre = ParagraphStyle('Literal', pNormal)
    pPre.fontName = 'Courier'
    pPre.listAttrs()
    return pNormal, pPre

def getSampleStyleSheet():
    """Returns a stylesheet object"""
    stylesheet = StyleSheet1()

    stylesheet.add(ParagraphStyle(name='XSmallNormal',
                                  fontName=_baseFontName,
                                  fontSize=6,
                                  leading=8)
                   )

    stylesheet.add(ParagraphStyle(name='SmallNormal',
                                  fontName=_baseFontName,
                                  fontSize=8,
                                  leading=10)
                   )

    stylesheet.add(ParagraphStyle(name='Normal',
                                  fontName=_baseFontName,
                                  fontSize=10,
                                  leading=12)
                   )

    stylesheet.add(ParagraphStyle(name='BodyText',
                                  parent=stylesheet['Normal'],
                                  spaceBefore=6)
                   )
    stylesheet.add(ParagraphStyle(name='Italic',
                                  parent=stylesheet['BodyText'],
                                  fontName = _baseFontNameI)
                   )

    stylesheet.add(ParagraphStyle(name='Heading1',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameB,
                                  fontSize=18,
                                  leading=22,
                                  spaceAfter=6),
                   alias='h1')

    stylesheet.add(ParagraphStyle(name='Title',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameB,
                                  fontSize=18,
                                  leading=22,
                                  alignment=TA_CENTER,
                                  spaceAfter=6),
                   alias='title')

    stylesheet.add(ParagraphStyle(name='Heading2',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameB,
                                  fontSize=14,
                                  leading=18,
                                  spaceBefore=12,
                                  spaceAfter=6),
                   alias='h2')

    stylesheet.add(ParagraphStyle(name='Heading3',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameBI,
                                  fontSize=12,
                                  leading=14,
                                  spaceBefore=12,
                                  spaceAfter=6),
                   alias='h3')

    stylesheet.add(ParagraphStyle(name='Heading4',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameBI,
                                  fontSize=10,
                                  leading=12,
                                  spaceBefore=10,
                                  spaceAfter=4),
                   alias='h4')

    stylesheet.add(ParagraphStyle(name='Heading5',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameB,
                                  fontSize=9,
                                  leading=10.8,
                                  spaceBefore=8,
                                  spaceAfter=4),
                   alias='h5')

    stylesheet.add(ParagraphStyle(name='Heading6',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameB,
                                  fontSize=7,
                                  leading=8.4,
                                  spaceBefore=6,
                                  spaceAfter=2),
                   alias='h6')

    stylesheet.add(ParagraphStyle(name='Bullet',
                                  parent=stylesheet['Normal'],
                                  firstLineIndent=0,
                                  spaceBefore=3),
                   alias='bu')

    stylesheet.add(ParagraphStyle(name='Definition',
                                  parent=stylesheet['Normal'],
                                  firstLineIndent=0,
                                  leftIndent=36,
                                  bulletIndent=0,
                                  spaceBefore=6,
                                  bulletFontName=_baseFontNameBI),
                   alias='df')

    stylesheet.add(ParagraphStyle(name='Code',
                                  parent=stylesheet['Normal'],
                                  fontName='Courier',
                                  fontSize=8,
                                  leading=8.8,
                                  firstLineIndent=0,
                                  leftIndent=36))

    return stylesheet

base_table_style = [
     ('FONT', (0, 0), (-1, 0), _baseFontNameB),
     ('FONT', (0, 1), (-1, -1), _baseFontName)]

class PageNumCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        """
        On a page break, add information to the list
        """
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """
        Add the page number to each page (page x of y)
        """
        page_count = len(self.pages)

        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)

        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        """
        Add the page number
        """
        page = "%s / %s" % (self._pageNumber, page_count)
        self.setFont(_baseFontName, 9)
        self.drawRightString(self._pagesize[0] / 2, 10*mm, page)


class InvoiceCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        """
        On a page break, add information to the list
        """
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """
        Add the page number to each page (page x of y)
        """
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_header()
            self.draw_footer()
            canvas.Canvas.showPage(self)

        canvas.Canvas.save(self)

    def draw_header(self):
        img = os.path.join(settings.MEDIA_ROOT, "adverts", "2018_invoice_header.jpg")
        self.drawImage(img, 0.5*cm, 24 * cm, width=self._pagesize[0]-cm, height=153, preserveAspectRatio=True)

    def draw_footer(self):
        img = os.path.join(settings.MEDIA_ROOT, "adverts", "2018_invoice_footer.jpg")
        self.drawImage(img, 0.5*cm, 0.5*cm, width=self._pagesize[0]-cm, height=73, preserveAspectRatio=True)


def fill_page_with_image(path, canvas):
    """
    Given the path to an image and a reportlab canvas, fill the current page
    with the image.

    This function takes into consideration EXIF orientation information (making
    it compatible with photos taken from iOS devices).

    This function makes use of ``canvas.setPageRotation()`` and
    ``canvas.setPageSize()`` which will affect subsequent pages, so be sure to
    reset them to appropriate values after calling this function.

    :param   path: filesystem path to an image
    :param canvas: ``reportlab.canvas.Canvas`` object
    """
    from PIL import Image

    page_width, page_height = canvas._pagesize

    image = Image.open(path)
    image_width, image_height = image.size
    if hasattr(image, '_getexif'):
        orientation = (image._getexif() or {}).get(274, 1)  # 274 = Orientation
    else:
        orientation = 1

    # These are the possible values for the Orientation EXIF attribute:
    ORIENTATIONS = {
        1: "Horizontal (normal)",
        2: "Mirrored horizontal",
        3: "Rotated 180",
        4: "Mirrored vertical",
        5: "Mirrored horizontal then rotated 90 CCW",
        6: "Rotated 90 CW",
        7: "Mirrored horizontal then rotated 90 CW",
        8: "Rotated 90 CCW",
    }
    draw_width, draw_height = page_width, page_height
    if orientation == 1:
        canvas.setPageRotation(0)
    elif orientation == 3:
        canvas.setPageRotation(180)
    elif orientation == 6:
        image_width, image_height = image_height, image_width
        draw_width, draw_height = page_height, page_width
        canvas.setPageRotation(90)
    elif orientation == 8:
        image_width, image_height = image_height, image_width
        draw_width, draw_height = page_height, page_width
        canvas.setPageRotation(270)
    else:
        raise ValueError("Unsupported image orientation '%s'."
                         % ORIENTATIONS[orientation])

    if image_width > image_height:
        page_width, page_height = page_height, page_width  # flip width/height
        draw_width, draw_height = draw_height, draw_width
        canvas.setPageSize((page_width, page_height))

    # Ameriks custom implementation to position in the middle image.
    # TODO: Testing with rotated image
    draw_width = page_width
    draw_height = (page_width * image_height) / image_width

    if draw_height < page_height:

        draw_height = page_height
        draw_width = (page_height * image_width) / image_height

    x = 0
    if draw_width > page_width:
        x = (page_width - draw_width) / 2.0
    y = 0
    if draw_height > page_height:
        y = (page_height - draw_height) / 2.0

    canvas.drawImage(path, x, y, width=draw_width, height=draw_height,
                     preserveAspectRatio=True)
