import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

# Initialize Database
conn = sqlite3.connect("pos_system.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
''')

# Insert default admin user if not exists
cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
if cursor.fetchone() is None:
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', '1234'))
conn.commit()
conn.close()

# Screens
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)

        self.username_input = TextInput(hint_text="Username", multiline=False)
        self.password_input = TextInput(hint_text="Password", password=True, multiline=False)
        login_btn = Button(text="Login", font_size=24, background_color=(0.2, 0.6, 0.8, 1))
        login_btn.bind(on_press=self.login)

        layout.add_widget(Label(text="POS System Login", font_size=32))
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(login_btn)

        self.add_widget(layout)

    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        conn = sqlite3.connect("pos_system.db")
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.manager.current = 'main'
        else:
            self.show_popup("Invalid Login", "Incorrect username or password.")

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text=message))
        close_btn = Button(text="Close", size_hint_y=None, height=50)
        popup = Popup(title=title, content=popup_layout, size_hint=(0.7, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        popup_layout.add_widget(close_btn)
        popup.open()

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=20, padding=40)

        add_btn = Button(text="Add Product", font_size=22, background_color=(0.4, 0.8, 0.4, 1))
        sell_btn = Button(text="Sell Product", font_size=22, background_color=(0.8, 0.4, 0.4, 1))
        view_btn = Button(text="View Products", font_size=22, background_color=(0.6, 0.4, 0.8, 1))

        add_btn.bind(on_press=self.add_product)
        sell_btn.bind(on_press=self.sell_product)
        view_btn.bind(on_press=self.view_products)

        layout.add_widget(Label(text="POS System Main Menu", font_size=32))
        layout.add_widget(add_btn)
        layout.add_widget(sell_btn)
        layout.add_widget(view_btn)

        self.add_widget(layout)

    def add_product(self, instance):
        layout = GridLayout(cols=2, padding=20, spacing=20)

        name_input = TextInput(hint_text="Product Name", multiline=False)
        price_input = TextInput(hint_text="Price", multiline=False)
        quantity_input = TextInput(hint_text="Quantity", multiline=False)

        save_btn = Button(text="Save", background_color=(0.2, 0.6, 0.2, 1))
        cancel_btn = Button(text="Cancel", background_color=(0.6, 0.2, 0.2, 1))

        layout.add_widget(Label(text="Name:"))
        layout.add_widget(name_input)
        layout.add_widget(Label(text="Price:"))
        layout.add_widget(price_input)
        layout.add_widget(Label(text="Quantity:"))
        layout.add_widget(quantity_input)
        layout.add_widget(save_btn)
        layout.add_widget(cancel_btn)

        popup = Popup(title="Add New Product", content=layout, size_hint=(0.8, 0.8))

        def save_product(instance):
            name = name_input.text
            try:
                price = float(price_input.text)
                quantity = int(quantity_input.text)
            except ValueError:
                self.show_popup("Error", "Price must be a number and quantity an integer.")
                return

            if name == "":
                self.show_popup("Error", "Product name cannot be empty.")
                return

            conn = sqlite3.connect("pos_system.db")
            cursor = conn.cursor()
            cursor.execute('INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)', (name, price, quantity))
            conn.commit()
            conn.close()

            popup.dismiss()
            self.show_popup("Success", "Product added successfully.")

        save_btn.bind(on_press=save_product)
        cancel_btn.bind(on_press=popup.dismiss)

        popup.open()

    def sell_product(self, instance):
        layout = GridLayout(cols=2, padding=20, spacing=20)

        product_input = TextInput(hint_text="Product Name", multiline=False)
        quantity_input = TextInput(hint_text="Quantity to Sell", multiline=False)

        sell_btn = Button(text="Sell", background_color=(0.2, 0.6, 0.2, 1))
        cancel_btn = Button(text="Cancel", background_color=(0.6, 0.2, 0.2, 1))

        layout.add_widget(Label(text="Product:"))
        layout.add_widget(product_input)
        layout.add_widget(Label(text="Quantity:"))
        layout.add_widget(quantity_input)
        layout.add_widget(sell_btn)
        layout.add_widget(cancel_btn)

        popup = Popup(title="Sell Product", content=layout, size_hint=(0.8, 0.8))

        def sell(instance):
            product_name = product_input.text
            try:
                quantity = int(quantity_input.text)
            except ValueError:
                self.show_popup("Error", "Quantity must be an integer.")
                return

            conn = sqlite3.connect("pos_system.db")
            cursor = conn.cursor()
            cursor.execute('SELECT quantity FROM products WHERE name = ?', (product_name,))
            product = cursor.fetchone()

            if product and product[0] >= quantity:
                new_quantity = product[0] - quantity
                cursor.execute('UPDATE products SET quantity = ? WHERE name = ?', (new_quantity, product_name))
                conn.commit()
                popup.dismiss()
                self.show_popup("Success", "Product sold successfully.")
            else:
                self.show_popup("Error", "Not enough stock or product not found.")

            conn.close()

        sell_btn.bind(on_press=sell)
        cancel_btn.bind(on_press=popup.dismiss)

        popup.open()

    def view_products(self, instance):
        conn = sqlite3.connect("pos_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, price, quantity FROM products")
        products = cursor.fetchall()
        conn.close()

        if not products:
            self.show_popup("No Products", "No products available.")
            return

        layout = GridLayout(cols=1, spacing=10, padding=10)
        for name, price, quantity in products:
            label = Label(text=f"{name} - ${price:.2f} - {quantity} left", font_size=18)
            layout.add_widget(label)

        popup = Popup(title="Products List", content=layout, size_hint=(0.8, 0.8))
        popup.open()

    def show_popup(self, title, message):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text=message))
        close_btn = Button(text="Close", size_hint_y=None, height=50)
        popup = Popup(title=title, content=layout, size_hint=(0.7, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        layout.add_widget(close_btn)
        popup.open()

# Screen Manager
class POSApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    POSApp().run()