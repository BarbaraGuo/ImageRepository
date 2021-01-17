from __future__ import print_function
import pickle
import os.path
import json
import tkinter as tk
from tkinter import filedialog
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def update_inventory(file_id= None) :
    quantity = 0
    price = 0.00
    discount = 0.00

    while True :
        print('Set quantity: ', end='')
        try :
            quantity = int(input())
            break
        except ValueError :
            print('invalid inventory number, try again')
    print('quantity set as:', quantity)

    while True :
        print('Set price: ', end='')
        try :
            price = float(input())
            break
        except ValueError :
            print('invalid price number, try again')
    print('Price set as: ', price)

    while True :
        print('Set discount (%): ', end='')
        try :
            discount = float(input().replace('%', ''))/100
            break
        except ValueError :
            print('invalid discount number, try again')
    print('Discount set as:', discount)

    inventory = open('inventory.json', 'r+')
    datas = str(inventory.read())
    inventory.close()

    inventory_data = None

    
    if datas!= "" :  
        inventory_data = json.loads(datas)
    else :
        inventory_data = {}

    data = {
        'quantity' : quantity,
        'price' : price,
        'discount' : discount
    }

    inventory_data[file_id] = data
    

    inventory = open('inventory.json', 'w')
    json.dump(inventory_data,inventory)
    inventory.close()


def add_image(service) :
    root = tk.Tk()
    filez = filedialog.askopenfilenames(parent=root,title='Choose a file')
    if filez :
        filelist = list(filez)
        for file in filelist :
            # Creates the files to upload
            file_metadata = {'name': file.split("/")[-1]}
            media = MediaFileUpload(file, mimetype='image/jpeg')

            print('Uploading ', file)

            # Uploads
            file_created = service.files().create(body = file_metadata, media_body=media,
                                    fields='id').execute()

            file_id =  file_created.get('id')
            print('Upload Successful, File ID: %s' % file_id)

            ids = open('ids.txt', 'a+')
            ids.write(file_id + " ; ")
            ids.close()

            print('Adding inventory details for ', file)
            update_inventory(file_id)
    else :
        print('Action cancelled')

def showInventory():
    
    
def inventory() :
    try :
        file_ids = open('ids.txt', 'r')
        ids = file_ids.read().split(" ; ")

        print("enter the number corresponding to which entry you want to modify:")

        # because of the splice and how we append ; to the ids the last entry will always be empty
        for index in range(len(ids) - 1) :
            print( "{0} : {1}".format( index, ids[index]))

        invalid_entry_message = 'invalid entry number, try again'
        while True :
            try :
                index = int(input("Enter: "))
                if(index >= len(ids) - 1) :
                    print(invalid_entry_message)
                else :
                    update_inventory(ids[index])
                    break;
            except ValueError :
                print(invalid_entry_message)

    except FileNotFoundError:
        print('Repository is currently empty')


def run_app(service) :
    add = 'a'
    quit= 'q'
    manage_inventory = 'm'

    actions = [add, quit, manage_inventory]

    print('Enter the corresponding key to enter action:')
    

    while True:
        print('Add Image(s): {0}, Manage Inventory: {1}, Quit: {2}'.format(add, manage_inventory, quit))
        entered = str(input('enter: '))

        if entered not in actions:
            print('Please enter a valid action')
        elif entered is quit:
            break
        elif entered is add:
            add_image(service)
        elif entered is manage_inventory:
            inventory()

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """

    print("SIGNING IN...")

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Run Application
    run_app(service)

if __name__ == '__main__':
    main()
