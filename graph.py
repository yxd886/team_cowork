import tkinter


def go():
    print(entry1.get())  # 获取文本框的内容


win = tkinter.Tk()
#text = tkinter.Text(win)
#text.pack()
#text.insert(tkinter.END,"请在下面输入框输入您的API key:")
label = tkinter.Label(win,text="请在下面输入框输入您的API key:")
label.pack()
entry1 = tkinter.Entry(win,width=50, bg="white", fg="black")
# entry1=tkinter.Entry(win,show="*",width=50,bg="red",fg="black")
entry1.pack()


label = tkinter.Label(win,text="请在下面输入框输入您的API secret:")
label.pack()
entry2 = tkinter.Entry(win,width=50, bg="white", fg="black")
# entry1=tkinter.Entry(win,show="*",width=50,bg="red",fg="black")
entry2.pack()




button = tkinter.Button(win, text="有种点我", command=go)  # 收到消息执行这个函数
button.pack()  # 加载到窗体，
win.mainloop()
