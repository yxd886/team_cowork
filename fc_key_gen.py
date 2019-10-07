import rsa
from base64 import b64encode, b64decode
import time
import os
import tkinter
pem = '''-----BEGIN RSA PRIVATE KEY-----
MIICXwIBAAKBgQCAnqpl6IeK/xCNzA6PbN5N0Vo113nUxbozQDQy7XHbeaNhm9Ft
AX+C/8rMjjyFkCuvle2jxv9dcwGbzyZqyV59c1ylas6Cvou/XuPpPBi98FZ5FeyY
SMIaFqB5/b5ZPvp+LJcW/40engFh39sl6qIiPv+5u3m5SE0E71WFXtPMSwIDAQAB
AoGAFJBJkg2BTjnFfcY4NbokOLDWCXGv6tLKGFOVhObtozdpZbux2gm5R0p6NAYx
qvEH6wS/f8XbIie3BCA0TkEpw79YPY552PuMOIGLGf+rN89Tal8JzQB5P0eVY/W2
f7DwxHFkrTVO9dwBNK3Vy/C/ULYxAQoVLXh7UD5xFtJvw6ECRQD500m/1IEgMZMw
4dFRVyHvXGHp5JCU3v3aVUUoIaFDg8Pu7Xu1s2Jv95MhRNrhZrJJcpSKHPq2A4gW
2OtFtQpwMlV2QwI9AIPMejy/4j1SGp1h+8OzMU8Z9LQec7wJGnx1Lg60F9c1kZMB
CdFQj5OimbCeZko5o13hO+iYPW/YvYIlWQJEBnr4msVEZDVlAAubhmSgOLlIwOxw
46u1Igi8NoJI0JuGZZg7cUcp8oWVh3NlyhsD3Ovf9oUx667DxPPzhmdf0fE8TkkC
PB6Irb0LO0+3iMDzZU9mYUMRIVblQyzJ8x/oSd5QLMHIAEzNTcf3YPv0DKUVXV9O
0SE7wBRXyMvzq5vOKQJEeLI4ncEkKHk8MAJhWq19TIzfUFeQ0ive59mxlQHeR5YI
0IyBG+q0C546gqmrLb7l8aSiRptjYwrXvANLq3qBkoyBa+I=
-----END RSA PRIVATE KEY-----
'''

private = rsa.PrivateKey.load_pkcs1(pem)

gap = "multicoin"
msg1 = ""
new_msg = msg1+gap+"lyaegjdfuyeu"


def get_license_day():
    global msg1
    msg1 = entryday.get().strip()
    new_msg = msg1 + gap + "lyaegjdfuyeu"
    signature = b64encode(rsa.sign(new_msg.encode(), private, "SHA-1"))
    #license_day  = 0.00069
    label = tkinter.Label(win, text="激活码:")
    label.pack()
    T = tkinter.Text(win, height=1, width=120)
    T.pack()
    T.insert(tkinter.END, signature.decode())

win = tkinter.Tk()
win.title("注册")
label = tkinter.Label(win, text="请输入客户提供的代码：")
label.pack()
entryday = tkinter.Entry(win, width=50, bg="white", fg="black")
entryday.pack()

button = tkinter.Button(win, text="确定", command=get_license_day)  # 收到消息执行这个函数
button.pack()  # 加载到窗体，
win.mainloop()
