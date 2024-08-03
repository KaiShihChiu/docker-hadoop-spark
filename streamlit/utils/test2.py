from hivedb import HiveDB
hive = HiveDB()

# show databases
databases = hive.show_databases()
# create database
db = "govdocs"
hive.use_database(db)

tb = "test_table"

# print(hive.read_table(tb))


# check if the file is already in the database
selected_file = '假日奉派參加研習之公務人員，可准予補休及申請加班費.docx'
file_exists = hive.check_file_exists(tb, selected_file)
print(file_exists)