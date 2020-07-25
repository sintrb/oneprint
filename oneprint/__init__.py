# -*- coding: UTF-8 -*
'''
Created on 2020-07-10
'''
from __future__ import print_function

__version__ = '1.0.0'

CHAR_V_LINE = '|'
CHAR_H_LINE = '-'
CHAR_BLANK = ' '

import xml.dom.minidom
from xml.dom.minidom import Element, Document


class PrintException(Exception):
    pass


def check_tag(node, tag):
    tags = tag if isinstance(tag, (set, list, tuple)) else [tag]
    if node.tagName.lower() not in tags:
        raise PrintException('need <%s> not %s: %s' % (tag, node.tagName, node.toxml()))


def filter_elements(nodes):
    return list(filter(lambda n: isinstance(n, Element), nodes))


def calc_md5(s):
    import hashlib
    m2 = hashlib.md5()
    m2.update(s.encode("utf8"))
    return m2.hexdigest()


def get_node_attr(node, attr, default=None):
    wn = node.getAttributeNode(attr)
    if not wn and default == None:
        raise PrintException('need %s attribute for %s' % (attr, node.toxml()))
    return wn.value if wn else default


def get_node_attr_int(node, attr, default=None):
    return int(get_node_attr(node, attr, default))


def get_node_text(node):
    text = ''
    if node.childNodes:
        text = node.childNodes[0].data
    return text


class BasePrint(object):
    _temp_path = None
    _get_lock = None

    def __init__(self, temp_path=None, width=None, get_lock=None, **kwargs):
        self._temp_path = temp_path
        self.width = int(width) if width else None
        if get_lock == None:
            from threading import RLock
            _lock = RLock()
            get_lock = lambda k: _lock
        self._get_lock = get_lock

    def _get_char_width(self, c):
        # 获取字符宽度
        if isinstance(c, type(u'')):
            c = u'%s' % c
        if not c:
            return 0
        elif len(c) == 1:
            return 1 if ord(c) < 128 else 2
        else:
            raise PrintException('char "%s" can\' get width' % c)

    def _get_line_width(self, l):
        if isinstance(l, type(u'')):
            l = u'%s' % l
        return sum(map(self._get_char_width, l))

    def _fill_text(self, text, width, align):
        bw = self._get_char_width(CHAR_BLANK)
        tw = int(self._get_line_width(text) / bw)
        width = int(width / bw)
        if tw < width:
            lw = 0
            rw = 0
            if align == 'right':
                # 左对齐
                lw = width - tw
            elif align == 'left':
                # 左对齐
                rw = width - tw
            else:
                # 居中
                lw = int((width - tw) / 2)
                rw = width - tw - lw
            text = self._repeat_to_width(CHAR_BLANK, lw * bw) + text + self._repeat_to_width(CHAR_BLANK, rw * bw)
        return text

    def _split_with_width(self, text, width, align='left'):
        if isinstance(text, type(u'')):
            text = u'%s' % text
        txts = []
        pt = ''

        for c in text:
            t = pt + c
            w = self._get_line_width(t)
            if w > width:
                txts.append(pt)
                pt = c
            else:
                pt = t
        if pt:
            txts.append(pt)
        return txts

    def _repeat_to_width(self, t, width):
        if width <= 0:
            return ''
        w = self._get_line_width(t)
        return t * int(width / (w or 1))

    def _table_to_text(self, table):
        '''table转text'''
        tab_data = []

        def tab_output(text):
            tab_data.append(text)

        def tab_br():
            tab_output('\n')

        eletrs = filter_elements(table.childNodes)
        if eletrs and eletrs[0].tagName.lower() == 'tbody':
            eletrs = filter_elements(eletrs[0].childNodes)
        if not eletrs:
            return
        trh = eletrs[0]
        for trh in eletrs:
            ok = True
            for e in filter_elements(trh.childNodes):
                if get_node_attr_int(e, 'colspan', 1) > 1:
                    ok = False
                    break
            if ok:
                break
        check_tag(trh, 'tr')
        ths = filter_elements(trh.childNodes)
        if not ths:
            return
        tabw = 0
        colws = []
        colct = len(ths)
        for th in ths:
            w = get_node_attr_int(th, 'width', 10)
            colws.append(w)
            tabw += w
        border = get_node_attr_int(table, 'border', 0)
        vborder = border
        hborder = 1  # if border else 0
        if self.width:
            bw = self._get_char_width(CHAR_BLANK)
            fc = int(self.width / bw)
            tw = fc - vborder * (colct + 1)
            colws = [int(float(w) * tw / tabw) for w in colws]
            colws[-1] = tw - sum(colws[0:-1])
            colws = [w * bw for w in colws]
        tabw = sum(colws)
        taboutw = tabw
        if border:
            taboutw = tabw + self._get_char_width(CHAR_V_LINE) * vborder * (colct + 1)
            ix = 0
            while ix < hborder:
                tab_output(self._repeat_to_width(CHAR_H_LINE, taboutw))
                tab_br()
                ix += 1
        for tr in eletrs:
            check_tag(tr, 'tr')
            eletds = filter_elements(tr.childNodes)
            maxlns = 0
            tds = []
            for ix, td in enumerate(eletds):
                check_tag(tr, ('tr', 'td'))
                cct = get_node_attr_int(td, 'colspan', 1)
                cw = sum(colws[ix: ix + cct]) + self._get_char_width(CHAR_V_LINE) * vborder * (cct - 1)
                align = get_node_attr(td, 'align', 'left').lower()
                text = get_node_text(td)
                txts = self._split_with_width(text, width=cw, align=align)
                maxlns = max(maxlns, len(txts))
                tds.append({
                    'align': align,
                    'width': cw,
                    'td': td,
                    'texts': txts
                })
            ix = 0
            while ix < maxlns:
                if vborder:
                    tab_output(CHAR_V_LINE * vborder)
                for tdd in tds:
                    txts = tdd['texts']
                    cw = tdd['width']
                    align = tdd['align']
                    if ix < len(txts):
                        tab_output(self._fill_text(txts[ix], cw, align))
                    else:
                        tab_output(self._repeat_to_width(CHAR_BLANK, cw))
                    if vborder:
                        tab_output(CHAR_V_LINE * vborder)
                tab_br()
                ix += 1
            if get_node_attr_int(tr, 'border', 0) and hborder:
                ix = 0
                while ix < hborder:
                    tab_output(self._repeat_to_width(CHAR_H_LINE, taboutw))
                    tab_br()
                    ix += 1

        return ''.join(tab_data)

    def get_url_to_path(self, url):
        import tempfile, os, requests
        fnd = calc_md5(url)
        if self._temp_path == None:
            self._temp_path = tempfile.mkdtemp(prefix='urlcache-')
        six = url.rfind('.')
        if six > 0:
            sufix = url[six:]
        else:
            sufix = ''
        path = os.path.join(self._temp_path, fnd + sufix)

        with self._get_lock(fnd):
            if not os.path.exists(path):
                with self._get_lock(self._temp_path):
                    if not os.path.exists(self._temp_path):
                        os.makedirs(self._temp_path)
                with open(path, 'wb') as f:
                    f.write(requests.get(url).content)
        return path

    def get_data(self):
        '''获取打印数据'''
        raise NotImplementedError()

    def get_text(self):
        raise NotImplementedError()

    def print_text(self, text):
        raise NotImplementedError()

    def handle_table(self, node):
        text = self._table_to_text(node)
        self.print_text(text)

    def handle_text(self, node):
        self.print_text(get_node_text(node) + '\n')

    def handle_hr(self, node):
        border = get_node_attr_int(node, 'border', 1)
        if border and self.width:
            ix = 0
            while ix < border:
                self.print_text(self._repeat_to_width(CHAR_H_LINE, self.width) + '\n')
                ix += 1

    def _handle_node(self, node):
        tag = node.tagName.lower()
        meth = 'handle_%s' % tag
        fn = getattr(self, meth, None)
        if fn:
            fn(node)
        else:
            import warnings
            warnings.warn('%s can\'t handle <%s>' % (self.__class__.__name__, tag))

    def print_with_xml(self, xmlString):
        if not isinstance(xmlString, type(b'')):
            xmlString = xmlString.encode('utf8')
        dom = xml.dom.minidom.parseString(xmlString)
        if isinstance(dom, Document) or dom.tagName.lower() == 'xml':
            node = dom.childNodes[0]
        else:
            node = dom
        for e in filter_elements(node.childNodes):
            self._handle_node(e)

    def auto_print(self, text):
        import re
        isxml = re.match('<.*>', text.strip().replace('\n', ''))
        if isxml:
            if '<xml' not in text:
                text = '<xml>%s</xml>' % text
            self.print_with_xml(text)
        else:
            self.print_text(text)


class EscPosPrint(BasePrint):
    '''
    print data to a ESC/POS printer.
    '''
    font = 'A'

    def __init__(self, encode=None, **kwargs):
        BasePrint.__init__(self, **kwargs)
        from escpos.printer import Dummy
        self.dummy = Dummy()
        if encode:
            self.dummy.codepage = encode
        self.dummy.hw('init')
        self.texts = []

    def _get_char_width(self, c):
        w = BasePrint._get_char_width(self, c)
        if self.font == 'A':
            w = w * 12
        elif self.font == 'B':
            if w == 1:
                w = 9
            else:
                w = 16
        return w

    def print_text(self, text):
        self.texts.append(text)
        self.dummy.text(text)

    def _set_with_node(self, node):
        font = get_node_attr(node, 'font', '')
        align = get_node_attr(node, 'align', '')
        size = get_node_attr_int(node, 'size', 0)
        text_type = 'B' if get_node_attr(node, 'bold', '') else '' + 'U' if get_node_attr(node, 'underline', '') else ''
        setd = {}
        if font:
            setd['font'] = font
            self.font = font
        if align:
            setd['align'] = align
        if size:
            setd['width'] = size
            setd['height'] = size
        if text_type:
            setd['text_type'] = text_type
        if setd:
            self.dummy.set(**setd)

    def _handle_node(self, node):
        tag = node.tagName.lower()
        if tag in ['table', 'text', 'td', 'tr']:
            self._set_with_node(node)
        BasePrint._handle_node(self, node)

    def handle_cut(self, node):
        self.dummy.cut()

    def handle_image(self, node):
        src = get_node_attr(node, 'src', '')
        path = self.get_url_to_path(src)
        if path:
            self.dummy.image(path)

    def handle_img(self, node):
        self.handle_image(node)

    def handle_qrcode(self, node):
        self.dummy.qr(get_node_text(node), size=get_node_attr_int(node, 'size', 5), native=get_node_attr(node, 'native', 'False').upper() == 'TRUE')

    def handle_barcode(self, node):
        self.dummy.barcode(get_node_text(node), get_node_attr(node, 'type', 'EAN13').upper(), font=get_node_attr(node, 'font', 'A').upper(), pos=get_node_attr(node, 'pos', 'OFF').upper(), function_type=get_node_attr(node, 'function', 'B').upper())

    def raw_send(self, msg):
        self.dummy._raw(msg)

    def get_data(self):
        return self.dummy.output

    def get_text(self):
        return ''.join(self.texts)


class ImageDrawPrint(BasePrint):
    '''
    print data to a PIL Image draw.
    it's use to test/debug print format.
    '''
    pos_y = 0
    pos_x = 0
    font = 'A'
    sizemap = None

    def __init__(self, padding=10, width=576, sizemap=None, font='A', **kwargs):
        BasePrint.__init__(self, width=width, **kwargs)
        from PIL import Image, ImageDraw, ImageFont
        self.padding_y = self.padding_x = padding
        width = padding * 2 + self.width
        height = self.padding_y * 2
        self.image = Image.new('RGB', (width, height), (255, 255, 255))
        fontUrl = 'https://cdn-qn.huaeb.com/sellmall/20200725/lhG8Zyft2V5pLmcTpKAsyV9jnjAO.ttf'
        if not sizemap:
            sizemap = {
                'A': 24,
                'B': 16,
            }
        self.font = font
        self.sizemap = sizemap
        self.fontmap = {
            k: ImageFont.truetype(self.get_url_to_path(fontUrl), v)
            for k, v in self.sizemap.items()
        }
        self.draw = ImageDraw.Draw(self.image)
        self.texts = []

    def _set_with_node(self, node):
        font = get_node_attr(node, 'font', '')
        align = get_node_attr(node, 'align', '')
        size = get_node_attr_int(node, 'size', 0)
        text_type = 'B' if get_node_attr(node, 'bold', '') else '' + 'U' if get_node_attr(node, 'underline', '') else ''
        setd = {}
        if font:
            setd['font'] = font
            self.font = font
        if align:
            setd['align'] = align
        if size:
            setd['width'] = size
            setd['height'] = size
        if text_type:
            setd['text_type'] = text_type

    def _handle_node(self, node):
        tag = node.tagName.lower()
        if tag in ['table', 'text', 'td', 'tr']:
            self._set_with_node(node)
        BasePrint._handle_node(self, node)

    def _get_char_width(self, c):
        w = BasePrint._get_char_width(self, c)
        return int(w * self.sizemap[self.font] / 2)

    def _adjust_height(self, h):
        mh = self.pos_y + h + self.padding_y * 2
        iw, ih = self.image.size
        if mh > ih:
            from PIL import Image, ImageDraw, ImageFont
            nh = mh + h * 5
            nimg = Image.new('RGB', (iw, nh), (255, 255, 255))
            nimg.paste(self.image, (0, 0, iw, ih))
            self.image = nimg
            self.draw = ImageDraw.Draw(self.image)

    def print_text(self, text):
        self.texts.append(text)
        for c in text:
            if c == '\r':
                continue
            if c == '\n':
                self._next_line()
                continue
            cw = self._get_char_width(c)
            if self.pos_x == 0:
                self._adjust_height(self._get_char_width(CHAR_BLANK) * 2)
            if self.pos_x + cw > self.width:
                self._next_line()
            self.draw.text((self.padding_x + self.pos_x, self.padding_y + self.pos_y), c, font=self.fontmap[self.font], fill="#000000", spacing=0, align='left')
            self.pos_x += cw

    def _next_line(self):
        self.pos_x = 0
        cw = self._get_char_width(CHAR_BLANK)
        self.pos_y += cw * 2 + int(cw / 3)

    def _pase_image(self, img, align='left'):
        from PIL import Image
        if img.mode == 'RGBA':
            nimg = Image.new('RGB', size=img.size, color=(255, 255, 255))
            nimg.paste(img, (0, 0), mask=img)
            img = nimg.convert('RGB')
        if self.pos_x > 0:
            self._next_line()
        x, y = self.padding_x + self.pos_x, self.padding_y + self.pos_y
        w, h = img.size
        if w < self.width:
            if align == 'right':
                x = self.width - w
            elif align == 'center':
                x = int((self.width - w) / 2)
        self._adjust_height(h)
        self.image.paste(img, (x, y, x + w, y + h))
        self.pos_y += h
        self.pos_x = 0

    def handle_image(self, node):
        src = get_node_attr(node, 'src', '')
        path = self.get_url_to_path(src)
        if path:
            from PIL import Image
            im = Image.open(path)
            self._pase_image(im, get_node_attr(node, 'align', 'left'))

    def handle_img(self, node):
        self.handle_image(node)

    def handle_qrcode(self, node):
        import qrcode

        text = get_node_text(node)
        img = qrcode.make(text)
        self._pase_image(img, get_node_attr(node, 'align', 'center'))

    def handle_cut(self, node):
        self.print_text(self._repeat_to_width(' >> ', self.width) + '\n')

    def handle_barcode(self, node):
        from PIL import Image
        from io import BytesIO
        from pystrich.code128 import Code128Encoder
        from pystrich.ean13 import EAN13Encoder
        from pystrich.code39 import Code39Encoder
        codetype = get_node_attr(node, 'type', 'ean13').lower()
        codermap = {
            'code128': Code128Encoder,
            'ean13': EAN13Encoder,
            'code39': Code39Encoder,
        }
        code = get_node_text(node)
        if codetype not in codermap:
            import warnings
            warnings.warn('unsupported barcode type "%s": %s' % (codetype, node.toxml()))
            self.print_text('unsupported barcode %s\n%s\n' % (codetype.upper(), code))
        else:
            encoder = codermap[codetype](code)
            img = Image.open(BytesIO(encoder.get_imagedata()))
            self._pase_image(img, get_node_attr(node, 'align', 'center'))

    def get_image(self, mode='L'):
        from PIL import Image
        img = self.image
        rw, rh = img.size
        iw = rw
        ih = self.padding_y * 2 + self.pos_y
        if self.pos_x:
            ih = ih + self._get_char_width(CHAR_BLANK)
        nimg = Image.new('RGB', size=(iw, ih), color=(255, 255, 255))
        nimg.paste(img, (0, 0, rw, rh))
        if nimg.mode != mode:
            nimg = nimg.convert(mode)
        return nimg

    def show(self):
        self.get_image().show()

    def get_data(self):
        from io import BytesIO
        buffer = BytesIO()
        img = self.get_image()
        img.save(buffer, "jpeg")
        return buffer.getvalue()

    def get_text(self):
        return ''.join(self.texts)
