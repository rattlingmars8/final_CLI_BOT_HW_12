from my_classes import *
import signal
    
# The read-file fnc and setting the object of AddressBook class to the right way for work with.
def read_csv():
    with open('contacts.csv', 'a+', newline="") as csvfile:
        csvfile.seek(0)
        reader = csv.DictReader(csvfile)
        contacts = AddressBook()
        for line in reader:
            record = Record(Name(line['Name']))
            file_phones = None
            try:
                bday = Birthday(line["B-day"]) if line["B-day"] != "" else None
                file_phones = [Phone(phone) for phone in eval(line["Phones"])] if line["Phones"] != "[]" else None # get the list by using eval from string like this: "['+380930030322', '+380731404451']". 
            except (ValueError, TypeError):
                pass
            if file_phones and len(file_phones) > 1:
                record.add_phones(file_phones)
            elif file_phones and len(file_phones) == 1:
                record.add_phone(next(iter(file_phones)))
            if bday:
                record.add_bday(bday)
            contacts.add_record(record)            
        return contacts
    
contacts = read_csv() # Set the object of AddressBook class and read/create the file.

# Decorator function for common input errors
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)  # Call the decorated function with the given arguments
        except KeyError:
            return "This contact doesn't exist in the phonebook."
        except ValueError:
            return "Please enter correct phone number. Example: '+380123456789' or '0123456879'."
        except IndexError:
            return "Please enter valid name."
        except TypeError:
            return "Invalid date format. Try 'dd.mm' or 'dd.mm.yyyy'"
    return wrapper

def name_check(name:str):
    if name not in ['', " ", '_'] and name in contacts.keys():
        return name
    elif not contacts and name not in ['', " ", '_']:
        return name
    else:
        raise IndexError

# fnc to show user the position of the phones for requested contact
@input_error 
def take_position(name:str) -> (list | str): 
    record = contacts.get(name)
    if len(record.phones) == 0:
        return None
    print(f'{name} phone numbers:')
    for i, number in enumerate([phone.value for phone in record.phones], 0):
        print(f'{i+1}. {number}')
    while True:
        try:
            pos_input = input('Type "exit" to exit or enter the position of the phone: ')
            if pos_input.lower() in ['exit', 'end', 'stop']:
                return 'Exiting del_phone...'
            pos = int(pos_input) - 1
            if pos > len(record.phones)-1 or pos < 0:
                raise IndexError
        except IndexError:
            print('Wrong position. Please try again.')
            continue
        except ValueError:
            print('Please enter a valid integer index.')
            continue
        return [pos, record, number]

@input_error
def hello(*args):
    return "Hi. How can I help you?"

# fnc to add a new contact to the phonebook
@input_error
def add_contact(*args):
    name = Name(args[0]) 
    if name.value.strip() == "":
        return "Try again. Enter contact name you want to add."
    if name.value in contacts.keys():
        return "This contact already exists."
    else:
        if len(args) > 1:
            phone = Phone(args[1])
            record = Record(name, phone)
            contacts.add_record(record)
            contacts.write_csv()
            return f"{name.value} with {phone.value} has been added to the phonebook."
        else:
            record = Record(name)
            contacts.add_record(record)
            contacts.write_csv()
            return f"{name.value} has been added to the phonebook." 

@input_error
def show_all(*args):
    return contacts.show_all()
    
@input_error
def add_bday(*args):
    name = name_check(args[0])
    record = contacts.get(name)
    record.add_bday(Birthday(args[1]))
    contacts.write_csv()
    return(f"Added birthday to {name}'s record.")

@input_error
def get_day_till_bday(*args):
    name = name_check(args[0])
    record = contacts.get(name)
    return record.days_till_bday()

@input_error
def change_phone(*args):
    name = name_check(args[0])
    taken_pos = take_position(name)
    if taken_pos:
        pos, record, number = taken_pos[0], taken_pos[1], taken_pos[2]
        while True:
            phone_input = input(f'Enter new phone number for contact - {name}: ')
            if phone_input.lower() in ['exit', 'end']:
                return 'Exiting...'
            try:
                new_phone = Phone(phone_input)
            except ValueError:
                print('Please enter a valid phone number. Recommended format: "+380123456789" or "0123456879".')
            else:
                break
        record.change_phone(pos, new_phone)
        contacts.write_csv()
        return f"{name}'s phone {number} was changed to {new_phone}."
    return f"{name} haven't any phone yet."

@input_error        
def append_phone(*args):
    name = name_check(args[0])
    if len(args) > 1:
        new_phone = Phone(args[1])
        record = contacts.get(name)
        if len(record.phones) == 0:
            record.add_phone(new_phone)
            contacts.write_csv()
            return f"To {name}'s phones was add {new_phone.value}."
        for phone in record.phones:
            if phone.value == new_phone.value:
                return f"{new_phone.value} is already in {name}'s phones. Try again."
            else:
                record.add_phone(new_phone)
                contacts.write_csv()
                return f"To {name}'s phones was add {new_phone.value}."
    else:
        return f"Enter the phone you want to add for {name}. Try again."

@input_error
def remove_phone(*args):
    name = name_check(args[0])
    taken_pos = take_position(name)
    pos, record, number = taken_pos[0], taken_pos[1], taken_pos[2]
    record.remove_phone(pos)
    contacts.write_csv()
    return f"{name}'s phone {number} was deleted."

@input_error       
def contact_remove(*args):
    name = name_check(args[0])
    del contacts.data[name]
    contacts.write_csv()
    return f"Contact {name} was deleted from phonebook."

# show phones for the unique contact
@input_error  
def show_cont_phones(*args):
    name = name_check(args[0])
    record = contacts.get(name)
    if not record.phones:
        print(f"{name} has no phone numbers.")
    else:
        print(f"{name} phone numbers:")
        for i, phone in enumerate(record.phones, 1):
            print(f"{i}. {phone.value}")
    return ""

def help(*args):
    return """
    'hello' -> Greeting the user: (Hi. How can I help you?).
    'show all' -> Returns a list of all contacts. If there are more than 10 contacts in the list, returns a book of 5 contacts per page.
    'add [name]* (phone)**' -> Adds a contact to the phone book.
    'change phone [name]*' -> Allows the user to select the position of the phone number to replace from the proposed list of numbers that the selected contact has/if any.
    'append phone [name]*' -> Adds a phone number to the selected contact.
    'remove phone [name]*' -> Allows the user to select the position of the phone number to delete from the proposed list of numbers for the selected contact.
    'del contact [name]*' ->  Completely deletes a contact and its data.
    'show phones [name]*' -> Returns a list of all numbers for the selected contact.
    'set bday [name]* [birth day]*' -> Adds a birthday for the selected contact. The date must be in the format: 'dd.mm' or 'dd.mm.yyyy'.
    'when bday [name]*' -> Returns the number of days until the selected contact's birthday.
    'find' -> Returns a list of contacts where the entered value matches the contact name or number.
    'exit', 'close', 'good bye', 'goodbye' -> Ends the program execution and saves the data to the 'contacts.csv' file in the folder with the program itself.
    
    *[] -  must have. Use without brackets.
    **() - optional. Use without brackets.
    
    IMPORTANT!!!
    The program automatically saves all changes that have occurred to the address book.
"""

# fnx to search by value in names or phones
def search(*args):
    search_value = args[0] if len(args[0]) >= 1 else None
    if search_value:
        res = [record for record in contacts.data.values() if search_value in record.name.value or any(search_value in phone.value for phone in record.phones)]
        if res:
            print(f'{len(res)} records were found with your search request:\n ')
            for i, record in enumerate(res, 1):
                print(f'{i}. {record}')
        else:
            return 'No records were found with your search request.'
    else:
        return "Enter the search request and try again."
    return ""

COMMANDS = {
    hello: 'hello',
    show_all: "show all",
    add_contact: "add",
    change_phone: "change phone",
    append_phone: "append phone",
    remove_phone: "remove phone",
    contact_remove: "del contact", 
    show_cont_phones: "show phones",
    add_bday: 'set bday',
    get_day_till_bday: "when bday",
    search: 'find',
    help:'help'
}

# fnc to keep only needed part of the command
def remove_unnecessary_text(text):
    regex_pattern = "|".join(map(re.escape, COMMANDS.values()))
    match = re.search(regex_pattern, text.lower())
    if not match:
        return text
    start_index = match.start()
    return text[start_index:]

def command_handler(user_input: str):
    for command, command_words in COMMANDS.items():
        if user_input.lower().startswith(command_words):
            return command, user_input[len(command_words):].strip().split(" ")
    return None, None

# program interrupt handler 
def signal_handler(signal, frame):
    contacts.write_csv()
    print('Data was saved successfully. Exiting the program...')
    exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler) # Set the 'SIGINT' signal handler, and if it is triggered call 'signal_handler' fnc.
    while True:
        read_csv()
        user_input = input("Enter a command: ")
        cmd = remove_unnecessary_text(user_input)
        command, data = command_handler(cmd)
        # print(data)
        if command:
            print(command(*data))
        elif any(word in user_input.lower() for word in ['exit', 'close', 'good bye', 'goodbye']):
            contacts.write_csv()
            print('Good bye!')
            break
        else:
            print('Command is not supported. Try again.')
    


if __name__ == "__main__":
    main()