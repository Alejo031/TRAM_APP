# Testing GUI - Calculadora

from tkinter import *

# Creo mi ventana de trabajo
root = Tk()
root.title("Simple Calculator")

# Defino caja de entrada de datos
e = Entry(root, width = 35, borderwidth = 5)
# Le doy una ubicacion dentro de una grilla
e.grid(row = 0, column = 0, columnspan = 3, padx = 10, pady = 10)

# Funcion para que mi click me deje ingresar un nro a la calculadora
def button_click(number):
    # Guarda lo que tengo en la caja de texto
    current = e.get()
    # Borra lo que hay en la caja de texto
    e.delete(0, END)
    # Mete a la caja de texto el nro que ya tenía y el que ingresé despues (Los toma como string para que no se sumen)
    e.insert(0, str(current) + str(number))

def clear_button():
    e.delete(0, END)

def button_add():
    first_number = e.get()
    global f_num
    f_num = int(first_number)
    e.delete(0, END)

def equal_button():
    second_number = e.get()
    e.delete(0, END)
    e.insert(0, f_num+int(second_number))

# Definir botones
# Boton del nro 0, de 30x20 pixeles y que cuando lo toco ejecuta la funcion "button_click()" parámetro NUMERO 0 (valor numerico, no string)
button0 = Button(root, text = "0", padx = 30, pady = 20, command = lambda: button_click(0))
button1 = Button(root, text = "1", padx = 30, pady = 20, command = lambda: button_click(1))
button2 = Button(root, text = "2", padx = 30, pady = 20, command = lambda: button_click(2))
button3 = Button(root, text = "3", padx = 30, pady = 20, command = lambda: button_click(3))
button4 = Button(root, text = "4", padx = 30, pady = 20, command = lambda: button_click(4))
button5 = Button(root, text = "5", padx = 30, pady = 20, command = lambda: button_click(5))
button6 = Button(root, text = "6", padx = 30, pady = 20, command = lambda: button_click(6))
button7 = Button(root, text = "7", padx = 30, pady = 20, command = lambda: button_click(7))
button8 = Button(root, text = "8", padx = 30, pady = 20, command = lambda: button_click(8))
button9 = Button(root, text = "9", padx = 30, pady = 20, command = lambda: button_click(9))

button_equal = Button(root, text = "=", padx = 40, pady = 20, command = equal_button)
button_clear = Button(root, text = "Clear", padx = 40, pady = 20, command = clear_button)
button_plus = Button(root, text = "+", padx = 30, pady = 20, command = button_add)


# Dibujo los botones en mi ventana
button1.grid(row = 3, column = 0)
button2.grid(row = 3, column = 1)
button3.grid(row = 3, column = 2)

button4.grid(row = 2, column = 0)
button5.grid(row = 2, column = 1)
button6.grid(row = 2, column = 2)

button7.grid(row = 1, column = 0)
button8.grid(row = 1, column = 1)
button9.grid(row = 1, column = 2)

button0.grid(row = 4, column = 0)
button_clear.grid(row = 4, column = 1, columnspan = 2)

button_plus.grid(row = 5, column = 0)
button_equal.grid(row = 5, column = 1, columnspan = 2)

root.mainloop()