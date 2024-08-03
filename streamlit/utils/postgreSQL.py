
#  use postgreSQL to store the data in python 
import psycopg2

class PostgreSQL:
    def __init__(self):
        self.conn = psycopg2.connect(
            host='localhost',
            user='postgres',
            password='password'
        )
    
    def show_databases(self):
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT datname FROM pg_database')
            databases = cursor.fetchall()
            return databases
    
    def create_database(self, database_name):
        with self.conn.cursor() as cursor:
            cursor.execute(f'CREATE DATABASE {database_name} if not exists')
            self.conn.commit()
            
    def use_database(self, database_name):
        with self.conn.cursor() as cursor:
            cursor.execute(f'USE {database_name}')
            self.conn.commit()
            
    def show_tables(self):
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = "public"')
            tables = cursor.fetchall()
            return tables
    
    def create_table(self, table_name, columns):
        with self.conn.cursor() as cursor:
            columns_str = ', '.join([f'{col} {data_type}' for col, data_type in columns.items()])
            cursor.execute(f'CREATE TABLE {table_name} ({columns_str}) if not exists')
            self.conn.commit()
            
    def insert_data(self, table_name, data):
        with self.conn.cursor() as cursor:
            columns = ', '.join(data.keys())
            values = ', '.join([f"'{value}'" if isinstance(value, str) else str(value) for value in data.values()])
            cursor.execute(f'INSERT INTO {table_name} ({columns}) VALUES ({values})')
            self.conn.commit()
            

if __name__ == '__main__':
    postgreSQL = PostgreSQL()
    # show databases
    postgreSQL.show_databases()
    
    # postgreSQL.create_database('test_db')
    # postgreSQL.use_database('test_db')
    # postgreSQL.create_table('test_table', {'name': 'VARCHAR', 'age': 'INT'})
    # postgreSQL.insert_data('test_table', {'name': 'Alice', 'age': 25})
    # postgreSQL.insert_data('test_table', {'name': 'Bob', 'age': 30})
    # postgreSQL.insert_data('test_table', {'name': 'Charlie', 'age': 35})
    # postgreSQL.conn.close()