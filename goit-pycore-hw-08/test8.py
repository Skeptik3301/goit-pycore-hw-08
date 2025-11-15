import pickle

# Клас для контакту
class Contact:
    def __init__(self, name, phone, email=None):
        self.name = name
        self.phone = phone
        self.email = email

    def __str__(self):
        return f"{self.name} | {self.phone} | {self.email if self.email else 'No email'}"

# Клас для адресної книги
class AddressBook:
    def __init__(self):
        self.contacts = []

    def add_contact(self, contact):
        self.contacts.append(contact)

    def list_contacts(self):
        if not self.contacts:
            print("Адресна книга порожня.")
        for c in self.contacts:
            print(c)

    def find_contact(self, name):
        for c in self.contacts:
            if c.name.lower() == name.lower():
                return c
        return None

# Функції для збереження та завантаження
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)
    print("Дані збережено у файл.")

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            book = pickle.load(f)
            print("Дані завантажено з файлу.")
            return book
    except FileNotFoundError:
        print("Файл не знайдено. Створено нову адресну книгу.")
        return AddressBook()

# Основний цикл програми
def main():
    book = load_data()  # Завантаження даних при старті

    while True:
        print("\n1. Додати контакт\n2. Показати всі контакти\n3. Знайти контакт\n4. Вийти")
        choice = input("Виберіть опцію: ")

        if choice == "1":
            name = input("Ім'я: ")
            phone = input("Телефон: ")
            email = input("Email (необов'язково): ")
            book.add_contact(Contact(name, phone, email))
        elif choice == "2":
            book.list_contacts()
        elif choice == "3":
            name = input("Введіть ім'я для пошуку: ")
            contact = book.find_contact(name)
            if contact:
                print(contact)
            else:
                print("Контакт не знайдено.")
        elif choice == "4":
            save_data(book)  # Збереження перед виходом
            print("Вихід з програми...")
            break
        else:
            print("Невірний вибір. Спробуйте ще раз.")

if __name__ == "__main__":
    main()
