from tkinter import ttk


def configure_styles():
    style = ttk.Style()
    style.configure('TFrame', background='#f0f0f0')
    style.configure('TButton', padding=5, font=('Segoe UI', 9))
    style.configure('TRadiobutton', background='#f0f0f0', font=('Segoe UI', 9))
    style.configure('TLabel', background='#f0f0f0',
                    font=('Segoe UI', 10, 'bold'))

    return style
