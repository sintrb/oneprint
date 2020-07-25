# oneprint
oneprint is a uniform print library. It use XML to define print data. Now it can convert XML to ESC/POS data or Pillow Image object.

Install Dependencies
===============
```
 pip install requests qrcode pillow pystrich python-escpos
```

Install oneprint
===============
```
 pip install oneprint
```

XML data define demo
===============
```xml
<xml>
    <!-- text -->
    <text>oneprint is a uniform print library, support ESC/POS printer.</text>
    <!-- table -->
    <table border="1">
        <tr border="1">
            <th colspan="3" align="center" width="8">Title</th>
        </tr>
        <tr border="1">
            <th align="center" width="8">Time</th>
            <th align="center" width="20">Content</th>
            <th align="center" width="20">Remark</th>
        </tr>
        <tr border="1">
            <td>18:00</td>
            <td>This is content field! Just test!</td>
            <td align="center">Empty</td>
        </tr>
        <tr border="1">
            <td>19:00</td>
            <td colspan="2">Content 2</td>
        </tr>
    </table>
    <text>A Image</text>
    <!-- image -->
    <img align="center" src="https://img3.doubanio.com/dae/accounts/resources/527f922/sns/assets/lg_main@2x.png"/>
    <text>A Qrcode</text>
    <!-- qrcode -->
    <qrcode align="center">Hello</qrcode>
    <text>A Barcode</text>
    <!-- ean13 barcode -->
    <barcode align="center" type="ean13">123456789012</barcode>
    <!-- cur the page -->
    <cut/>
</xml>
```

The result:

![all](https://ishop-static-qn.inruan.com/Fn19wIxf7lcQIX_19OB-BIa_Kg8X.png)


Usage
===============

```python

# print to a image and show
data = '''
<text>Hello World</text>
<qrcode>Hello World</qrcode>
'''
from oneprint import ImageDrawPrint
pt = ImageDrawPrint()
pt.auto_print(data)
pt.show() # use Pillow Image.show()
# save to file
pt.get_image().save('/tmp/tt.jpeg')

# or print with python-escpos
from oneprint import EscPosPrint
ep = EscPosPrint()
ep.auto_print(data)

from escpos.printer import Serial
p = Serial(devfile='/dev/tty.usbserial',
           baudrate=9600,
           bytesize=8,
           parity='N',
           stopbits=1,
           timeout=1.00,
           dsrdtr=True)
p._raw(ep.get_data())
```

The result:

![t2](https://ishop-static-qn.inruan.com/FrHhC5sGxYWS9ElyUOHgtf0xTxtD.png)

[Click to view more information!](https://github.com/sintrb/oneprint)