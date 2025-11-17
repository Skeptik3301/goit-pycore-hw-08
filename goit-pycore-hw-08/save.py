from collections import UserDict
from datetime import datetime, timedelta
import pickle  


class Field:
    """Базовий клас для всіх полів"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Ім’я контакту"""
    pass


class Phone(Field):
    """Телефон із перевіркою"""
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Phone number must have exactly 10 digits.")
        super().__init__(value)

    @staticmethod
    def validate(value):
        return value.isdigit() and len(value) == 10


class Birthday(Field):
    """День народження у форматі DD.MM.YYYY"""
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


# ----------------- Класи контактів -----------------
class Record:
    """Запис у книзі контактів"""
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return True
        return False

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return True
        return False

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, date_str):
        self.birthday = Birthday(date_str)

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones)
        bday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{bday_str}"


# ----------------- Адресна книга -----------------
class AddressBook(UserDict):
    """Книга контактів"""
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        return False

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        next_week = today + timedelta(days=7)
        result = {}

        for record in self.data.values():
            if record.birthday:
                bday_this_year = record.birthday.value.replace(year=today.year)

                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)

                if bday_this_year.weekday() == 5:
                    bday_to_congratulate = bday_this_year + timedelta(days=2)
                elif bday_this_year.weekday() == 6:
                    bday_to_congratulate = bday_this_year + timedelta(days=1)
                else:
                    bday_to_congratulate = bday_this_year

                if today <= bday_to_congratulate <= next_week:
                    day_str = bday_to_congratulate.strftime("%A")
                    result.setdefault(day_str, []).append(record.name.value)

        return result


# ----------------- ЗБЕРЕЖЕННЯ та ЗАВАНТАЖЕННЯ -----------------
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


# ----------------- Декоратор -----------------
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Enter all required arguments."
        except AttributeError:
            return "Contact not found."
    return inner


# ----------------- Функції команд -----------------
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record.edit_phone(old_phone, new_phone):
        return "Phone number updated."


@input_error
def show_phone(args, book: AddressBook):
    record = book.find(args[0])
    return "; ".join(p.value for p in record.phones)


@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "No contacts saved."
    return "\n".join(str(r) for r in book.data.values())


@input_error
def add_birthday(args, book: AddressBook):
    name, date_str = args
    record = book.find(name)
    record.add_birthday(date_str)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args, book: AddressBook):
    record = book.find(args[0])
    return f"{record.name.value}'s birthday: {record.birthday}"


@input_error
def birthdays(args, book: AddressBook):
    result = book.get_upcoming_birthdays()
    if not result:
        return "No birthdays in the next 7 days."
    output = []
    for day, names in result.items():
        output.append(f"{day}: {', '.join(names)}")
    return "\n".join(output)


# ----------------- Парсер -----------------
def parse_input(user_input):
    parts = user_input.split()
    cmd = parts[0].strip().lower() if parts else ""
    args = parts[1:]
    return cmd, args


# ----------------- Основна функція -----------------
def main():
    book = load_data()   

    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)   
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
