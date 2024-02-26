from datetime import datetime
import sqlite3
import pytz

connection = sqlite3.connect("mybank.db")
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS accounts(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR UNIQUE NOT NULL,
                    balance REAL NOT NULL)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS history(
                    id INTEGER NOT NULL,
                    date VARCHAR NOT NULL,
                    amount REAL NOT NULL,
                    status VARCHAR)""")

connection.commit()


class Account:

    def __init__(self, name, balance=None):
        self.name = name
        cursor.execute("SELECT * FROM accounts WHERE name=?", (self.name,))
        existing_account = cursor.fetchone()

        if existing_account:
            self.uid = existing_account[0]
            self.balance = existing_account[2]
        else:
            self.balance = balance if balance is not None else 0

            cursor.execute("""INSERT INTO accounts(name, balance)
                                VALUES (?, ?)""", (self.name, self.balance))

            connection.commit()

            cursor.execute("SELECT last_insert_rowid()")
            self.uid = cursor.fetchone()[0]

    @staticmethod
    def _get_local_time():
        return pytz.utc.localize(datetime.utcnow()).astimezone().isoformat()

    def __db_operate(self, op_date, op_amount, op_status):
        cursor.execute("""INSERT INTO history
                            VALUES
                            (?,?,?,?)""", (self.uid, op_date, op_amount, op_status))

        cursor.execute("""UPDATE accounts SET balance = ?
                            WHERE id = ?""", (self.balance, self.uid))

        connection.commit()

    def deposit(self, amount):
        self.balance += amount
        print(f"ანგარიშზე დაემატა {amount} ლარი.")
        self.__db_operate(self._get_local_time(), amount, "თანხის შეტანა")

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            print(f"ანგარიშიდან ჩამოიჭრა {amount} ლარი.")
            self.__db_operate(self._get_local_time(), -amount, "თანხის გატანა")
        else:
            print(f"ანგარიშზე არასაკმარისი რაოდენობის თანხაა!")

    def showbalance(self):
        return f"მიმდინარე ბალანსი: {self.balance}"

    def showhistory(self):
        cursor.execute("""SELECT accounts.id, name, history.date, history.amount, history.status
                            FROM history JOIN accounts ON accounts.id = history.id
                            WHERE accounts.id = ?""", (self.uid,))
        data = cursor.fetchall()
        for item in data:
            print(item)


def main():
    while True:


        
        print("1. ანგარიშზე შესვლა\n2. ახალი ანგარიშის შექმნა\n3. გამოსვლა")
        login_choice = input("აირჩიეთ ოპცია (1-3): ")

        if login_choice == '1':
            account_name = input("შეიყვანეთ ანგარიშის სახელი: ")

            # Check if the account exists
            cursor.execute("SELECT * FROM accounts WHERE name=?", (account_name,))
            existing_account = cursor.fetchone()

            if existing_account:
                account = Account(account_name, balance=existing_account[2])
                break
            else:
                print(f"ანგარიში სახელით '{account_name}' არ არსებობს. შეამოწმეთ სხვა სახელი.")
        elif login_choice == '2':
            while True:
                account_name = input("შეიყვანეთ ანგარიშის სახელი: ")
                cursor.execute("SELECT * FROM accounts WHERE name=?", (account_name,))
                existing_account = cursor.fetchone()
                if existing_account:
                    print(f"ანგარიში სახელით '{account_name}' უკვე არსებობს. შეამოწმეთ სხვა სახელი.")
                    break
                else:
                    account = Account(account_name)
                    break
        elif login_choice == '3':
            break
        else:
            print("არასწორი შერჩევა")

    while True:
        print("\n1. თანხის შეტანა\n2. თანხის გატანა\n3. ბალანსის ნახვა\n4. ისტორიის ნახვა\n5. გამოსვლა")
        choice = input("აირჩიეთ ოპერაცია (1-5): ")

        if choice == '1':
            amount = float(input("შეიყვანეთ თანხა რომ შეატანოთ: "))
            account.deposit(amount)
        elif choice == '2':
            amount = float(input("შეიყვანეთ თანხა რომ გამოაჩინოთ: "))
            account.withdraw(amount)
        elif choice == '3':
            print(account.showbalance())
        elif choice == '4':
            account.showhistory()
        elif choice == '5':
            break
        else:
            print("არასწორი შერჩევა")


if __name__ == "__main__":
    main()