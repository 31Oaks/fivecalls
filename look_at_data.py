import sqlite3
import pandas as pd

conn = sqlite3.connect('data/fivecalls.db')
rand_df = pd.read_sql_query("SELECT * FROM flat_data ORDER BY RANDOM() LIMIT 50", conn)
conn.close()
print("Randoms:" , rand_df)
print("Randoms columns:", rand_df.columns)

conn = sqlite3.connect('data/fivecalls.db')
head_df = pd.read_sql_query("SELECT * FROM flat_data ORDER BY id ASC LIMIT 25", conn)
conn.close()
print("Head:" , head_df)
print("Head columns:", head_df.columns)

conn = sqlite3.connect('data/fivecalls.db')
tail_df = pd.read_sql_query("SELECT * FROM flat_data ORDER BY id DESC LIMIT 25", conn)
conn.close()
print("Tail:" , tail_df)
print("Tail columns:", tail_df.columns)

conn = sqlite3.connect('data/fivecalls.db')
all_df = pd.read_sql_query("SELECT * FROM flat_data", conn)
conn.close()
print("All data row count:" , len(all_df))