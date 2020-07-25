# -*- coding: UTF-8 -*
'''
Created on 2020-07-10
'''
from oneprint import EscPosPrint, ImageDrawPrint


def do_table_test():
    import io
    pt = EscPosPrint(encode='utf8', temp_path='/tmp/print', width=576)
    with io.open('test/table.xml', 'r', encoding='utf8') as f:
        # print(pt._get_char_width(' '))
        pt.auto_print(f.read())
        print(pt.get_text())
        # print(pt._get_char_width(' '))


def do_all_test():
    import io
    pt = ImageDrawPrint(encode='utf8', temp_path='/tmp/print', width=576)
    with io.open('test/all.xml', 'r', encoding='utf8') as f:
        pt.auto_print(f.read())
        # print(pt.get_text())
        pt.show()


def do_usb_test():
    from escpos.printer import Usb
    import io
    pt = EscPosPrint(encode='gb2312', temp_path='/tmp/print', width=576)
    with io.open('test/all.xml', 'r', encoding='utf8') as f:
        pt.auto_print(f.read())
        p = Usb(0x6868, 0x0500, in_ep=0x84, out_ep=0x3)
        p._raw(pt.get_data())
        p.close()


if __name__ == '__main__':
    do_all_test()
