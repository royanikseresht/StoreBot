import telebot
import logging
import mysql.connector

token = 'place your Telegram bot token here'
bot = telebot.TeleBot(token)
cart = {}
users = {}
knownUsers = []
commands = {
    'start'       : 'Get used to the bot',
    'order'       : 'To order',
    'help'        : 'Gives you information about the available commands'
}
config = {'user': 'root', 'password': '...', 'host': '...', 'database': 'StoreBot'}

logging.basicConfig(filename='storebot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info('*** StoreBot INITIALIZED ***')

def create_database(name):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute(f'''DROP DATABASE IF EXISTS {name}''')
    conn.commit()
    cursor.execute(f'''CREATE DATABASE IF NOT EXISTS {name}''')
    print('DATABASE CREATED.')
    conn.commit()
    cursor.close()
    conn.close()

def create_user_table():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS Users (
                user_ID         BIGINT,
                first_name      VARCHAR(100),
                last_name       VARCHAR(255),
                username        VARCHAR(50)    NOT NULL,
                phone_number    BIGINT,
                date            TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_ID)
                );
                '''
                )
    conn.commit()
    cursor.close()
    conn.close()

def create_product_table():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS Products (
                product_ID      INT             AUTO_INCREMENT,
                name            VARCHAR(300),
                inventory       TINYINT         NOT NULL DEFAULT 0,
                price           DECIMAL(10, 2),
                date            TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (product_ID)
                );
                '''
                )
    conn.commit()
    cursor.close()
    conn.close()

def create_orders_table():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS Orders (
                order_ID            INT             AUTO_INCREMENT,
                user_ID             BIGINT,
                item_total_price    DECIMAL(12, 2),
                date                TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (order_ID),
                FOREIGN KEY (user_ID) REFERENCES Users(user_ID)
                );
                '''
                )
    conn.commit()
    cursor.close()
    conn.close()

def create_orderlines_table():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS Orderlines (
                product_ID      INT,
                order_ID        INT             AUTO_INCREMENT,
                quantity        TINYINT,
                date            TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_ID) REFERENCES Products(product_ID),
                FOREIGN KEY (order_ID) REFERENCES Orders(order_ID)
                );
                '''
                )
    conn.commit()
    cursor.close()
    conn.close()

def insert_user_info(user_ID, first_name, last_name, username, phone_number):
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        sql = "INSERT INTO Users (user_ID, first_name, last_name, username, phone_number) VALUES (%s, %s, %s, %s, %s)"
        val = (user_ID, first_name, last_name, username, phone_number)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error inserting user info:", e)

def insert_product_info(products):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor() 
    SQL_Query = """INSERT INTO Products (name, inventory, price)
    VALUES (%s, %s, %s); """
    values = [(product['name'], product['inventory'], product['price']) for code, product in products.items()]
    cursor.executemany(SQL_Query, values)
    conn.commit()
    cursor.close()
    conn.close()

def insert_order_info(user_ID, item_total_price):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    try:
        query = "INSERT INTO Orders (user_ID, item_total_price) VALUES (%s, %s)"
        values = (user_ID, item_total_price)
        cursor.execute(query, values)
        conn.commit()
        order_ID = cursor.lastrowid
        return order_ID
    except Exception as e:
        print(f"Error inserting order info: {e}")
        conn.rollback()

def insert_orderlines_info(order_ID, product_ID, quantity):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    sql_insert = "INSERT INTO Orderlines (order_ID, product_ID, quantity) VALUES (%s, %s, %s)"
    val_insert = (order_ID, product_ID, quantity)
    cursor.execute(sql_insert, val_insert)
    conn.commit()
    cursor.close()
    conn.close()

products = {
     '1': {'name': 'Caffe Latte', 'price': 4.15, 'inventory': 5},
     '2': {'name': 'Caffe Mocha', 'price': 4.65, 'inventory': 5},
     '3': {'name': 'Iced Coffee', 'price': 3.45, 'inventory': 5},
     '4': {'name': 'Strawberries Frappuccino', 'price': 4.95, 'inventory': 5},
     '5': {'name': 'Caramel Macchiato', 'price': 4.75, 'inventory': 5},
     '6': {'name': 'Mocha Frappuccino', 'price': 4.95, 'inventory': 5},
     '7': {'name': 'Toasted Graham Latte', 'price': 5.25, 'inventory': 5},
     '8': {'name': 'Pumpkin Spice Latte', 'price': 5.25, 'inventory': 5},
     '9': {'name': 'Salted Caramel Mocha Frappuccino', 'price': 5.25, 'inventory': 5}
            }

def user_step(user_ID):
    if user_ID in users:
        return users[user_ID]
    else:
        knownUsers.append(user_ID)
        users[user_ID] = 0
        logging.info(f'New user detected: {user_ID}.')
        return 0
    
def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            logging.info(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)
    bot.set_update_listener(listener)

@bot.message_handler(commands=['start'])
def send_channel_link(message):
    user_ID = message.from_user.id
    user_step(user_ID)
    channel_link = "https://t.me/sample2001"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Go to channel', url=channel_link))
    bot.send_message(user_ID, "Welcome! Check out our channel first and /order from here 🥰\n\nNeed help? /help", reply_markup=markup)

@bot.message_handler(commands=['help'])
def command_help(message):
        user_ID = message.chat.id
        help_text = "The following commands are available: \n"
        for key in commands:
            help_text += "/" + key + ": "
            help_text += commands[key] + "\n"
        bot.send_message(user_ID, help_text)

@bot.message_handler(commands=['order'])
def order_command(message):
        user_ID = message.from_user.id
        user_step(user_ID)
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard= True, one_time_keyboard=True)
        items_buttons = []
        for item_code in products:
            items_buttons.append(telebot.types.KeyboardButton(item_code))
        markup.add(*items_buttons)
        bot.send_message(message.chat.id, "What is the item code of the product you want to order?", reply_markup=markup)
        bot.register_next_step_handler(message, add_quantity)

def add_quantity(message):
    product_ID = message.text
    if product_ID in products:
        product = products[product_ID]
        bot.send_message(message.chat.id, f"How many {product['name']}(s) do you want? (Inventory: {product['inventory']})")
        bot.register_next_step_handler(message, add_to_cart, product)
    else:
        bot.send_message(message.chat.id, "Invalid product code.")

def add_to_cart(message, product):
    try:
        quantity = int(message.text)
        if quantity <= product['inventory']:
            if product['name'] in cart:
                cart[product['name']]['quantity'] += quantity
            else:
                cart[product['name']] = product
                cart[product['name']]['quantity'] = quantity
            markup = telebot.types.InlineKeyboardMarkup()
            add_button = telebot.types.InlineKeyboardButton(text='Add More Items', callback_data='add_more')
            cart_button = telebot.types.InlineKeyboardButton(text='View Cart', callback_data='cart')
            admin_button = telebot.types.InlineKeyboardButton(text='Contact Admin', url='https://t.me/...')
            owner_button = telebot.types.InlineKeyboardButton(text='Contact Bot Owner', url='https://t.me/NiksereshtRoya')
            markup.row(add_button, cart_button)
            markup.row(admin_button, owner_button)
            bot.send_message(message.chat.id, f"{quantity} {product['name']} added to cart.", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f"Sorry, we only have {product['inventory']} {product['name']} in stock.")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid quantity.")

@bot.callback_query_handler(func=lambda call: call.data in ['add_more', 'cart', 'contact_admin', 'contact_owner', 'confirm_purchase', 'cancel_purchase'])
def handle_callback_query(call):
        if call.data == 'add_more':
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard= True, one_time_keyboard=True)
            items_buttons = []
            for item_code in products:
                items_buttons.append(telebot.types.KeyboardButton(item_code))
            markup.add(*items_buttons)
            bot.send_message(call.message.chat.id, "Enter product code:", reply_markup=markup)
            bot.register_next_step_handler(call.message, add_quantity)
        elif call.data == 'cart':
            total_price = 0
            cart_items = []
            for item_name, item_data in cart.items():
                item_price = item_data['price']
                item_quantity = item_data['quantity']
                item_total_price = item_price * item_quantity
                total_price += item_total_price
                cart_items.append(f"{item_name} x {item_quantity}: {item_total_price}")
            if cart_items:
                cart_items.append(f"Total: {total_price}$")
                cart_message = "\n".join(cart_items)
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton(text='Confirm', callback_data='confirm_purchase'),
                           telebot.types.InlineKeyboardButton(text='Cancel', callback_data='cancel_purchase'))
                bot.send_message(call.message.chat.id, cart_message, reply_markup=markup)
            else:
                bot.send_message(call.message.chat.id, "Your cart is empty.")
        elif call.data == 'contact_admin':
            bot.send_message(call.message.chat.id, "Please contact our admin.")
        elif call.data == 'contact_owner':
            bot.send_message(call.message.chat.id, "Please contact the bot owner.")
        elif call.data == 'confirm_purchase':
            bot.send_message(call.message.chat.id, "Enter your name: ")
            bot.register_next_step_handler(call.message, get_number)
        elif call.data == 'cancel_purchase':
            bot.send_message(call.message.chat.id, "Purchase cancelled. Goodbye!")
            cart.clear()

def get_number(message):
    user_ID = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username
    phone_number = message.contact.phone_number if message.contact is not None else None
    if phone_number is None:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton(text="Share Contact", request_contact=True))
        bot.send_message(message.chat.id, "Please share your contact information:", reply_markup=keyboard)
        bot.register_next_step_handler(message, lambda m: insert_user_info(user_ID, first_name, last_name, username, m.contact.phone_number))
    else:
        insert_user_info(user_ID, first_name, last_name, username, phone_number)
    bot.register_next_step_handler(message, get_customer_info)

def get_customer_info(message):
    user_ID = message.from_user.id
    phone_number = message.contact.phone_number if message.contact is not None else None
    total_price = 0
    cart_items = []
    order_ID = None
    for item_name, item_data in cart.items():
        item_price = item_data['price']
        item_quantity = item_data['quantity']
        item_total_price = item_price * item_quantity
        total_price += item_total_price
        cart_items.append(f"{item_name} x {item_quantity}: {item_total_price}$")
        product_ID = None
        for k, v in products.items():
            if v['name'] == item_name:
                product_ID = k
                break
        order_ID = insert_order_info(user_ID, item_total_price)
        insert_orderlines_info(order_ID, product_ID, item_quantity)
    success_message(message, phone_number)

def success_message(message, phone_number):
    first_name = message.from_user.first_name
    customer_info_message = f"Thank you for your order, {first_name}!\n\n"
    customer_info_message += f"We will call you soon at {phone_number}!\n\n"
    customer_info_message += f"Have a nice day!\n\n"
    bot.send_message(message.chat.id, customer_info_message)

if __name__ == '__main__':
    create_database('StoreBot')
    create_user_table()
    create_product_table()
    create_orders_table()
    create_orderlines_table()
    insert_product_info(products)
    bot.infinity_polling()
