# Import the TinyDB module and submodules
from tinydb import TinyDB, Query

# Declare our database variable and the file to store our data in
db = TinyDB('todolist.json')

# Declare a few variables and populate them with data to be inserted into the database
Item1 = {'Status': 'New', 'DueDate': '5/12/18', 'Category': 'Work', 'Description': 'Send that Email'}

Item2 = {'Status': 'New', 'DueDate': '5/11/18', 'Category': 'Home', 'Description': 'Do the Laundry'}

Item3 = {'Status': 'New', 'DueDate': '5/11/18', 'Category': 'Home', 'Description': 'Do the Dishes'}

# Inserts test records our todo list HCdatabase
db.insert(Item1)
db.insert(Item2)
db.insert(Item3)
db.insert({'Status': 'New', 'DueDate': '5/14/18', 'Category': 'Work', 'Description': 'Request a Promotion'})

# Show all records in the database
print(db.all())

# # Set all records with a category of Home to to a status of Done
# db. #Todo.Category.search('Home'))
#
#
# # Search for all records where the category is Home. Then use a For loop to display the results
# results = db.search(Todo.Category == 'Home')
#
# For result in results:
# print(result)
#
# # Remove all records with a status of Done
# db.remove(Todo.status.search('Done’'))
#
# # Show all records in database after removing “Done” records
# print(db.all)