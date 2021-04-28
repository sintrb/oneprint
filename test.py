# -*- coding: UTF-8 -*
'''
Created on 2020-07-10
'''
from oneprint import EscPosPrint, ImageDrawPrint


def do_table_test():
    import io
    pt = ImageDrawPrint(encode='utf8', temp_path='/tmp/print', width=576)
    with io.open('test/table.xml', 'r', encoding='utf8') as f:
        # print(pt._get_char_width(' '))
        pt.auto_print(f.read())
        # print(pt.get_text())
        # print(pt._get_char_width(' '))
        pt.show()


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
    pt = EscPosPrint(encode='gb2312', temp_path='/tmp/print', width=384)
    with io.open('test/all.xml', 'r', encoding='utf8') as f:
        pt.auto_print(f.read())
        import base64
        # print(base64.encodebytes(pt.get_data()))
        # return
        # p = Usb(0x6868, 0x0500, in_ep=0x84, out_ep=0x3)
        # p = Usb(0x154f, 0x1300, in_ep=0x82, out_ep=0x01)
        p = Usb(0x0483, 0x5720, in_ep=0x82, out_ep=0x02)
        # p._raw(bytes([0x31,0x32,0x33,0x0A,0x1D,0x4C,0x50,0x00,0x31, 0x32,0x33, 0x0A]) + pt.get_data())
        px = [
            0x1B, 0x53,
            0x1D, 0x57, 0x80, 0x01,
            0x1D, 0x4C, 0xF0, 0x00, 0x0a,
            # 0x31, 0x32, 0x33, 0x34, 0x34, 0x0A
        ]
        b = px + [ord(c) for c in '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklnm\n']
        # b = [0x31, 0x32, 0x33, 0x0A, 0x1D, 0x4C, 0xE0, 0x00, 0x31, 0x32, 0x33, 0x0A]
        b = bytes(px) + pt.get_data()[2:]
        for i in b:
            print(hex(i))
        p._raw(bytes(b))
        p.close()


def do_usb_test2():
    from escpos.printer import Usb
    # p = Usb(0x6868, 0x0500, in_ep=0x84, out_ep=0x3)
    # p = Usb(0x2207, 0x0011, in_ep=0x02, out_ep=0x01)
    # p._raw(b'\x1b\x42\x02\x01')
    # p.close()


if __name__ == '__main__':
    # do_table_test()
    do_all_test()
    # do_usb_test()
    # do_usb_test()
    exit()
    from werkzeug._reloader import run_with_reloader

    run_with_reloader(lambda: do_table_test())
