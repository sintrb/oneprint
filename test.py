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


if __name__ == '__main__':
    do_all_test()
