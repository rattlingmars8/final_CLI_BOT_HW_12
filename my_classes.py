from collections import UserDict
import re
import csv
import datetime

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self) -> str:
        return f'{self.value}'

class Name(Field):
    pass

class Birthday(Field):
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        if value is None:
            self._value = value
        else:
            self._value = self._set_date(value)

    def _set_date(self, bday):
        date_types = ["%d.%m.%Y", '%d.%m']
        for date_type in date_types:
            try:
                self._value = datetime.datetime.strptime(bday, date_type).date()
                return self._value
            except ValueError:
                pass
        raise TypeError("Incorrect date format, should be dd.mm.yyyy or dd.mm")

    def __str__(self):
        if self._value.year == 1900:
            return self._value.strftime("%d.%m")
        else:
            return self._value.strftime("%d.%m.%Y")

class Phone(Field):
    def __init__(self, value=None):
        self.value = value
        
    @property
    def value(self):
        return self._value
        
    @value.setter
    def value(self, value):
        if value is None:
            self._value = value
        else:
            self._value = self._normal_phone(value)
        
    def _normal_phone(self, phone: str):
        digits = [char for char in phone if char.isdigit()]
        if len(digits) == 10 and digits[0] == "0":
            value =  "+38" + "".join(digits)
        elif len(digits) == 12 and digits[:3] == ["3", "8", "0"]:
            value =  "+" + "".join(digits)
        elif len(digits) == 12 and phone[0] == "+" and digits[:3] == ["3", "8", "0"]:
            value = "+" + "".join(digits)
        else:
            raise ValueError("Invalid phone number")
        return value
    
class Record():
    def __init__(self, name:Name, phone:Phone=None, bday:Birthday = None):
        self.name = name
        self.phones = [phone] if phone else []
        self.bday = bday

    def add_phone(self, phone:Phone):
        self.phones.append(phone)

    def add_phones(self, phones:list[Phone]):
        self.phones.extend(phones)

    def add_bday(self, bday:Birthday):
        self.bday = bday

    def days_till_bday(self):
        if not self.bday:
            return f"{self.name.value}'s b-day isn't set yet."
        today = datetime.datetime.now().date()
        bday_date = datetime.date(today.year, self.bday.value.month, self.bday.value.day)
        days_to_bday = (bday_date - today).days
        if days_to_bday < 0:
            bday_date = datetime.date(today.year + 1, self.bday.value.month, self.bday.value.day)
            days_to_bday = (bday_date - today).days
        if days_to_bday == 0:
            return f"Sing for {self.name.value} a song, cuz' {self.name.value}'s b-day is today! "
        return f"{self.name.value}'s b-day in {days_to_bday} days."

    def remove_phone(self, index: int):
        self.phones.pop(index)

    def change_phone(self, index: int, new_phone:Phone):
        self.phones[index] = new_phone

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        res = ""
    
        if self.phones:
            phones = ", ".join([str(phone) for phone in self.phones])
        else:
            phones = "No phones"
        if self.bday:
            res += f"{self.name}: {phones}. Birthday: {self.bday}"
        else:
            res += f"{self.name}: {phones}"
        return res


class AddressBook(UserDict):
    index = 0
    def add_record(self, record:Record):
        self.data[record.name.value] = record
    
    def iterator(self, n = 2):
        self.keys_list = sorted(self.data.keys())
        if self.index < len(self.keys_list):
            yield from [self[name] for name in self.keys_list[self.index:self.index+n]]
            self.index += n
        else:
            self.index = 0
            self.keys_list = []
    
    # The method to write changes to the file.
    def write_csv(self):
        records = self.data.values()
        with open('contacts.csv', 'w', newline="") as csvfile:
            fieldnames = ['Name', 'Phones', 'B-day']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                name = record.name.value
                phones = [phone.value for phone in record.phones]
                bday = record.bday
                writer.writerow({'Name': name, 'Phones': phones, "B-day": bday})
    
    def show_all(self) -> str:
        n = 5
        total_rec = len(self.data.keys())
        if total_rec > 10:
            total_pages = (total_rec + n - 1) // n
            current_page = 1
            while True:
                try:
                    print(f'Page {current_page} of {total_pages}:\n')
                    for i, rec in enumerate(self.iterator(n) , (current_page - 1) * n + 1):
                        print(f'{i}. {rec}\n')
                    if current_page == total_pages:
                        print("This is the final page.")
                        self.index = 0
                        break
                    user_input = input("Enter anything co continue watching list or type 'exit' / 'stop' / 'close' for exit: ")
                    if user_input in ['exit', 'stop', 'close']:
                        self.index = 0
                        break
                    else:
                        current_page +=1
                except StopIteration:
                    self.index = 0
                    break
        else:
            all_contacts = [record for _, record in self.items()]
            for i, record in enumerate(all_contacts, 1):
                print(f'{i}. {record}')
        return ""