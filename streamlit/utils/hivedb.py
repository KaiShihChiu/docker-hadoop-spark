from pyhive import hive
import pandas as pd

class HiveDB:
    def __init__(self, host='hive-server', port=10000, username='root'):
        self.conn = hive.Connection(host=host, port=port, username=username)
        self.cursor = self.conn.cursor()

    def show_databases(self):
        self.cursor.execute("SHOW DATABASES")
        databases = self.cursor.fetchall()
        # convert list of tuples to list of strings
        databases = [db[0] for db in databases]
        
        return databases
    
    # create database if not existed
    def create_database(self, database):
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")

    def use_database(self, database):
        # if database not exists, create it
        if not database in [db[0] for db in self.show_databases()]:
            self.create_database(database)
        
        self.cursor.execute(f"USE {database}")
        
    def table_exists(self, table_name):
        self.cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = self.cursor.fetchall()
        return len(result) > 0

    def show_tables(self):
        self.cursor.execute("SHOW TABLES")
        tables = self.cursor.fetchall()
        # convert list of tuples to list of strings
        tables = [table[0] for table in tables]
        return tables
    
    def create_table(self, table_name, columns):
        columns_str = ', '.join([f"{col_name} {col_type}" for col_name, col_type in columns.items()])
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        self.cursor.execute(create_table_query)
    

    def insert_data(self, table_name, data):
        # if table not exists, create it
        if not self.table_exists(table_name):
            columns = self.infer_hive_types(pd.DataFrame([data]))
            self.create_table(table_name)
        
        columns_str = ', '.join(data.keys())
        values_str = ', '.join([f"'{value}'" if isinstance(value, str) else str(value) for value in data.values()])
        insert_data_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"
        self.cursor.execute(insert_data_query)
        
    def infer_hive_types(self, df):
        type_mapping = {
            'int64': 'INT',
            'float64': 'FLOAT',
            'object': 'STRING',
            'datetime64[ns]': 'TIMESTAMP',
            'bool': 'BOOLEAN'
        }
        hive_columns = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            hive_columns[col] = type_mapping.get(dtype, 'STRING')
        return hive_columns
        
    # def insert_data_from_df(self, table_name, df):

    #     for row in df.itertuples(index=False):
    #         data = {col: getattr(row, col) for col in df.columns}
    #         self.insert_data(table_name, data)
            
    def insert_data_from_df(self, table_name, df):
        if not self.table_exists(table_name):
            columns = self.infer_hive_types(df)
            self.create_table(table_name, columns)
            
        for _, row in df.iterrows():
            columns = ', '.join(row.index)
            values = ', '.join([f"'{str(value).replace("'", "''")}'" for value in row.values])
            insert_data_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            self.cursor.execute(insert_data_query)
            self.conn.commit()

    def query_data(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()
        
    # read table into df from the table name and databbase
    def read_table_into_df(self, table_name, database):
        self.use_database(database)
        results = self.query_data(f"SELECT * FROM {table_name}")
        df = pd.DataFrame(results, columns=[desc[0] for desc in self.cursor.description])
        return df
        
    def delete_table(self, table_name, database):
        self.use_database(database)
        self.cursor.execute(f"DROP TABLE {table_name}")
        
    
    # def read_table_into_df(self, table_name):
    #     results = self.query_data(f"SELECT * FROM {table_name}")
    #     df = pd.DataFrame(results, columns=[desc[0] for desc in self.cursor.description])
    #     return df
    
    def check_file_exists(self, table_name, filename):
        self.cursor.execute(f"SELECT * FROM {table_name} WHERE filename = '{filename}'")
        result = self.cursor.fetchall()
        return len(result) > 0
        
    def read_table(self, table_name):
        return self.query_data(f"SELECT * FROM {table_name}")
        
    # read columns of filename
    def read_columns(self, col_name, table_name):
        return self.query_data(f"SELECT {col_name} FROM {table_name}")
    
    # read the column 2 of the table if the column 1 is equal to the value
    def read_columns_by_condition(self, col_name, table_name, condition_col, condition_val):
        return self.query_data(f"SELECT {col_name} FROM {table_name} WHERE {condition_col} = '{condition_val}'")
        
    # Function to map pandas dtypes to Hive dtypes
    def map_dtype(self, dtype):
        if pd.api.types.is_string_dtype(dtype):
            return 'STRING'
        elif pd.api.types.is_numeric_dtype(dtype):
            if pd.api.types.is_integer_dtype(dtype):
                return 'INT'
            elif pd.api.types.is_float_dtype(dtype):
                return 'FLOAT'
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return 'TIMESTAMP'
        # Add more mappings as needed
        return 'STRING'  # Default to STRING if type is not matched

    def extract_colname_dtype(self, df):
        columns = {}
        for col, dtype in df.dtypes.items():
            columns[col] = self.map_dtype(dtype)
        return columns

    def close(self):
        self.cursor.close()
        self.conn.close()

# 使用示例
i = 2
if __name__ == "__main__":
    if i == 1:
        # read csv and convert it into df
        df = pd.read_csv('/workspaces/streamlit/utils/2024-08-02T08-38_export.csv')
        
        # remove any Unnamed columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # drop id 
        df = df.drop(columns=['id'])
        
        print(df.columns)
        
        
        
        # 初始化 HiveDB 实例
        hive_db = HiveDB()

        # # 显示所有数据库
        databases = hive_db.show_databases()
        print("old Databases:", databases)
        
        # use the test database
        hive_db.use_database('test')
        databases = hive_db.show_databases()
        print("new Databases:", databases)
        
        # # write a df with multiple rows to hive
        # show table name in db
        old_tables = hive_db.show_tables()
        
        table_name = 'testdf2_table'

        columns = hive_db.extract_colname_dtype(df)
        
        hive_db.insert_data_from_df(table_name, df)
        
        # # read the table
        print(hive_db.read_table(table_name))
        

        
        # # create table named test_table
        # columns = {
        #     df.columns[0]: 'INT',
        #     'filename': 'STRING',
        #     'style': 'STRING',
        # }

        # hive_db.insert_data_from_df(table_name, df)
        
        # # read the table
        # print(hive_db.read_table(table_name))

        # 使用目标数据库
        # hive_db.use_database('openbeer')

        # 创建示例表
        # table_name = 'newbeers'
        # columns = {
        #     'id': 'INT',
        #     'name': 'STRING',
        #     'style': 'STRING',
        #     'abv': 'FLOAT'
        # }
        # hive_db.create_table(table_name, columns)

        # # 插入单行数据
        # data = {
        #     'id': 1,
        #     'name': 'IPA',
        #     'style': 'India Pale Ale',
        #     'abv': 6.5
        # }
        # hive_db.insert_data(table_name, data)

        # 使用 Pandas DataFrame 插入多行数据
        # data = {
        #     'id': [1, 2],
        #     'name': ['Stout', 'Pilsner'],
        #     'style': ['Imperial Stout', 'German Pilsner'],
        #     'abv': [9.0, 4.5]
        # }
        # df = pd.DataFrame(data)
        # hive_db.insert_data_from_df(table_name, df)

        # # 查询数据
        # results = hive_db.query_data(f"SELECT * FROM {table_name}")
        # for result in results:
        #     print(result)

        # 关闭连接
        hive_db.close()

    elif i ==2:
        # read filename from the table
        hive_db = HiveDB()
        hive_db.use_database('test')
        table_name = 'testdf2_table'
        # read the table
        filename = hive_db.read_columns('filename', table_name)
        print(filename)
        print(filename[5][0])
        
        
        cleaned = hive_db.read_columns_by_condition('cleaned', table_name, 'filename', filename[1][0])
        print(cleaned[0])
        print(cleaned[0][0])