import json
from datetime import datetime, timedelta

class Book:
    def __init__(self, book_id, name, author, quantity):  # Düzeltildi
        self.book_id = book_id
        self.name = name
        self.author = author
        self.quantity = quantity

    def to_dict(self):
        return {"book_id": self.book_id, "name": self.name, "author": self.author, "quantity": self.quantity}

    @staticmethod
    def from_dict(data):
        return Book(data["book_id"], data["name"], data["author"], data["quantity"])


class User:
    def __init__(self, user_id, name):  # Düzeltildi
        self.user_id = user_id
        self.name = name
        self.borrowed_books = []

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "borrowed_books": [book.to_dict() for book in self.borrowed_books]
        }

    @staticmethod
    def from_dict(data):
        user = User(data["user_id"], data["name"])
        user.borrowed_books = [BorrowedBook.from_dict(book) for book in data["borrowed_books"]]  # Hata düzeltilmiş
        return user


class BorrowedBook:
    def __init__(self, book, borrow_date):  # Düzeltildi
        self.book = book
        self.borrow_date = borrow_date

    def to_dict(self):
        return {
            "book": self.book.to_dict(),
            "borrow_date": self.borrow_date.strftime("%Y-%m-%d")
        }

    @staticmethod
    def from_dict(data):
        book = Book.from_dict(data["book"])
        borrow_date = datetime.strptime(data["borrow_date"], "%Y-%m-%d")
        return BorrowedBook(book, borrow_date)


class Library:
    def __init__(self):  # Düzeltildi
        self.books = []
        self.users = []
        self.load_data()

    def save_data(self):
        data = {
            "books": [book.to_dict() for book in self.books],
            "users": [user.to_dict() for user in self.users]
        }
        with open("library_data.json", "w") as file:
            json.dump(data, file)

    def load_data(self):
        try:
            with open("library_data.json", "r") as file:
                data = json.load(file)
                self.books = [Book.from_dict(book) for book in data.get("books", [])]
                self.users = [User.from_dict(user) for user in data.get("users", [])]
        except FileNotFoundError:
            pass

    def add_book(self, book_id, name, author, quantity):
        new_book = Book(book_id, name, author, quantity)
        self.books.append(new_book)
        self.save_data()
        print("Kitap başarıyla eklendi!")

    def list_books(self):
        if not self.books:
            print("Kütüphanede hiçbir kitap yok.")
        else:
            print("Kütüphanedeki kitaplar:")
            for book in self.books:
                print(f"ID: {book.book_id}, İsim: {book.name}, Yazar: {book.author}, Miktar: {book.quantity}")

    def add_user(self, user_id, name):
        new_user = User(user_id, name)
        self.users.append(new_user)
        self.save_data()
        print("Kullanıcı başarıyla eklendi!")

    def delete_user(self, user_id):
        user = next((u for u in self.users if u.user_id == user_id), None)
        if not user:
            print("Kullanıcı bulunamadı!")
            return

        if user.borrowed_books:
            print("Kullanıcının ödünç aldığı kitaplar mevcut, silme işlemi gerçekleştirilemiyor.")
        else:
            self.users.remove(user)
            self.save_data()
            print("Kullanıcı başarıyla silindi!")

    def list_users(self):
        if not self.users:
            print("Kütüphanede hiçbir kullanıcı yok.")
        else:
            print("Kayıtlı kullanıcılar:")
            for user in self.users:
                print(f"ID: {user.user_id}, İsim: {user.name}")

    def borrow_book(self, user_id, book_id):
        user = next((u for u in self.users if u.user_id == user_id), None)
        book = next((b for b in self.books if b.book_id == book_id), None)

        if not user:
            print("Kullanıcı bulunamadı!")
            return

        if not book:
            print("Kitap bulunamadı!")
            return

        if book.quantity > 0:
            book.quantity -= 1
            borrow_date = datetime.now()
            borrowed_book = BorrowedBook(book, borrow_date)
            user.borrowed_books.append(borrowed_book)
            self.save_data()
            print("Kitap başarıyla ödünç alındı!")
        else:
            print("Bu kitap stokta yok!")

    def return_book(self, user_id, book_id):
        user = next((u for u in self.users if u.user_id == user_id), None)
        book = next((b for b in self.books if b.book_id == book_id), None)

        if not user:
            print("Kullanıcı bulunamadı!")
            return

        if not book:
            print("Kitap bulunamadı!")
            return

        borrowed_book = next((bb for bb in user.borrowed_books if bb.book.book_id == book_id), None)
        if borrowed_book:
            borrowed_period = datetime.now() - borrowed_book.borrow_date
            if borrowed_period > timedelta(days=30):
                print(f"Uyarı: Bu kitap {borrowed_period.days} gün gecikmeli iade ediliyor!")
            user.borrowed_books.remove(borrowed_book)
            book.quantity += 1
            self.save_data()
            print("Kitap başarıyla iade edildi!")
        else:
            print("Bu kitap kullanıcı tarafından ödünç alınmamış.")

    def list_user_books(self, user_id):
        user = next((u for u in self.users if u.user_id == user_id), None)

        if not user:
            print("Kullanıcı bulunamadı!")
            return

        if not user.borrowed_books:
            print("Kullanıcının ödünç aldığı kitap yok.")
        else:
            print(f"{user.name} adlı kullanıcının ödünç aldığı kitaplar:")
            for borrowed_book in user.borrowed_books:
                book = borrowed_book.book
                print(f"ID: {book.book_id}, İsim: {book.name}, Yazar: {book.author}, Ödünç Alındı: {borrowed_book.borrow_date.strftime('%Y-%m-%d')}")


# Ana program
library = Library()

while True:
    print("\n1. Kitap Ekle\n2. Kütüphanedeki Kitapları Listele\n3. Kullanıcı Ekle\n4. Kullanıcı Sil\n5. Kullanıcıları Listele\n6. Kitap Ödünç Al\n7. Kitap İade Et\n8. Kullanıcının Ödünç Aldığı Kitapları Listele\n9. Çıkış")
    choice = input("Bir seçenek girin: ")

    if choice == "1":
        book_id = input("Kitap ID: ")
        name = input("Kitap İsmi: ")
        author = input("Yazar İsmi: ")
        quantity = int(input("Miktar: "))
        library.add_book(book_id, name, author, quantity)

    elif choice == "2":
        library.list_books()

    elif choice == "3":
        user_id = input("Kullanıcı ID: ")
        name = input("Kullanıcı İsmi: ")
        library.add_user(user_id, name)

    elif choice == "4":
        user_id = input("Kullanıcı ID: ")
        library.delete_user(user_id)

    elif choice == "5":
        library.list_users()

    elif choice == "6":
        user_id = input("Kullanıcı ID: ")
        book_id = input("Kitap ID: ")
        library.borrow_book(user_id, book_id)

    elif choice == "7":
        user_id = input("Kullanıcı ID: ")
        book_id = input("Kitap ID: ")
        library.return_book(user_id, book_id)

    elif choice == "8":
        user_id = input("Kullanıcı ID: ")
        library.list_user_books(user_id)

    elif choice == "9":
        print("Programdan çıkılıyor...")
        break

    else:
        print("Geçersiz seçenek, lütfen tekrar deneyin.")
