# Importing module
import mysql.connector
import random


# Establish connection to MySQL database
def connect_to_database():
    try:
        mydb = mysql.connector.connect(
            host="localhost", user="root", password="Wolve$23!"
        )
        print("Connected to the database\n")
        return mydb
    except mysql.connector.Error as err:
        print("Error connecting to the database:", err)
        return None


# Generates a random 10-digit account number
def generate_account_number():
    return int(random.random() * (10**9 - 1) + 10**8)


def login(mydb, username, password):
    try:
        # Check if account exists
        cursor = mydb.cursor()
        cursor.execute(
            "SELECT * FROM FastTwitch.user WHERE username = %s AND password = %s",
            (username, password),
        )
        user = cursor.fetchone()
        cursor.close()

        if user:
            print(user[0])
            print("Login successful!")
            return user
        else:
            print("Invalid username or password.\n")
            return None
    except mysql.connector.Error as err:
        print("Error during login:", err)
        return None

    # Create a new account


def create_account(
    mydb,
    username,
    password,
    email,
    user_id=None,
):  # default exceptions
    try:
        account_number = generate_account_number()
        # Inserting new account details into the database
        cursor = mydb.cursor()
        cursor.execute(
            "INSERT INTO FastTwitch.user (user_id,username,email,password,account_number) VALUES (%s,%s,%s,%s,%s)",
            (user_id, username, email, password, account_number),
        )
        mydb.commit()
        cursor.close()
        print("Account created successfully. Account Number is", account_number)
    except mysql.connector.Error as err:
        print("Error creating account:", err)


# Deletes an account
def delete_account(mydb, account_number, user_id=None):  # default exceptions
    try:
        # Deleting account from the database
        cursor = mydb.cursor()
        cursor.execute(
            "DELETE FROM user WHERE account_number = %s OR user_id = %s",
            (account_number, user_id),
        )
        mydb.commit()
        cursor.close()
        print("Account deleted successfully")
    except mysql.connector.Error as err:
        print("Error deleting account:", err)


# Modify account details
def modify_account(
    mydb,
    account_number,
    new_username=None,
    new_password=None,
    new_email=None,
    new_pin=None,
    is_admin=None,
):
    try:
        # Modifying account details in the database
        cursor = mydb.cursor()
        if new_username is not None:
            cursor.execute(
                "UPDATE FastTwitch.user SET username = %s WHERE account_number = %s",
                (new_username, account_number),
            )
        if new_password is not None:
            cursor.execute(
                "UPDATE FastTwitch.user SET password = %s WHERE account_number = %s",
                (new_password, account_number),
            )
        if new_email is not None:
            cursor.execute(
                "UPDATE FastTwitch.user SET email = %s WHERE account_number = %s",
                (new_email, account_number),
            )
        if new_pin is not None:
            cursor.execute(
                "UPDATE FastTwitch.user SET pin = %s WHERE account_number = %s",
                (new_pin, account_number),
            )
        if is_admin is not None:
            cursor.execute(
                "UPDATE FastTwitch.user SET is_admin = %s WHERE account_number = %s",
                (is_admin, account_number),
            )
        mydb.commit()
        cursor.close()
        print("Modified Account successfully")
    except mysql.connector.Error as err:
        print("Error Modifying Account:", err)


def send_allergies(mydb, account_number, user_id=None):
    pass


# Close connection to MySQL database
def close_connection(mydb):
    mydb.close()
    print("\nConnection to the database closed")
