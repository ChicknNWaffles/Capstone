#!/usr/bin/python3

import sqlite3
import math

sqlite = sqlite3.connect('../capstone.db')
sqlite.execute("Pragma foreign_keys = 1")
sql = sqlite.cursor()


def main():
	runTest(False);
	pass

# visualizes the current state of the database.
# needsTestTable is a boolean value
#     set it to true if you need to create a temporary extra table to visualize, false if not
def runTest(needsTestTable = False):
	if (needsTestTable == True):
		sql.execute("drop table if exists testTable2;")
		sql.execute("drop table if exists testTable;")
		sql.execute("Create table testTable (attr1 varchar(100), attr2 varchar(100), attr3 integer Primary Key);")
		sql.execute("insert into testTable (attr1, attr2) values ('potato', 'chip');")
		sqlite.commit()
		sql.execute("insert into testTable (attr1, attr2) values ('fry', 'latke');")
		sqlite.commit()

		sql.execute("Create table testTable2 (attr1 varchar(100), attr2 varchar(100), attr3 integer Primary Key, attr4 integer, foreign key (attr4) references testTable(attr3));")
		sql.execute("insert into testTable2 (attr1, attr2, attr4) values ('hashed', 'browns', 2);")
		sqlite.commit()
		sql.execute("insert into testTable2 (attr1, attr2, attr4) values ('mashed', 'baked', 1);")
		sqlite.commit()

	tables = getTableNames()
	for table in tables:
		printTable(table)
		print("")
		print("")

	if (needsTestTable == True):
		sql.execute("drop table testTable2;")
		sql.execute("drop table testTable;")
	
# gets the names of all tables currently in the database
def getTableNames():
	tables = sql.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
	tableNames = []

	for table in tables:
		tableNames.append(table[0])

	return tableNames

def printTable(tableName):
	tableWidth = 0
	columnWidths = []

	# get and prepare the data
	data = sql.execute(f"SELECT * FROM {tableName};").description
	content = sql.execute(f"Select * from {tableName};").fetchall()
	pragma = sql.execute(f"pragma table_info({tableName})").fetchall()
	pragmaForeignKeys = sql.execute(f"Pragma foreign_key_list({tableName})").fetchall()
	columns = []
	pks = []
	fks = []

	i = 0
	for key in pragmaForeignKeys:
		fks.append(key[3])
		i+=1

	i = 0
	for column in data:
		if column[0] in fks:
			columns.append(column[0] + " (" + pragma[i][2] + ") -> (" + pragmaForeignKeys[fks.index(column[0])][2] + " " + pragmaForeignKeys[fks.index(column[0])][4] + ")")
			if pragma[i][5] != 0:
				pks.append(column[0] + " (" + pragma[i][2] + ") -> (" + pragmaForeignKeys[fks.index(column[0])][2] + " " + pragmaForeignKeys[fks.index(column[0])][4] + ")")
		else:
			columns.append(column[0] + " (" + pragma[i][2] + ")")
			if pragma[i][5] != 0:
				pks.append(column[0] + " (" + pragma[i][2] + ")")
		
		i += 1

	# calculate column widths based off of the widest entry in each
	c=0
	for column in columns:
		longest = len(columns[c])
		for row in content:
			if (len(str(row[c]))) >= longest:
				longest = len(str(row[c]))
		columnWidths.append(longest + 2)
		c += 1



	# calculate table width based off of column widths
	tableWidth = sum(columnWidths) + (len(columns) - 1) + 2
	#            widest content    + col delim btw cols + col delim outside
	
	#print table name
	print(tableName)

	# print header row
	print("-" * tableWidth)
	print("|", end="")
	i = 0
	for column in columns:
		#print beginning part of buffer
		#subtract the width of the column name from the width of the column to get buffer size
		#divide buffer size down rounding up
		print(" " * (math.ceil((columnWidths[i] - len(column))/2)), end="")

		#print column name, underlining primary key
		if (column in pks):
			print("\033[4m" + column + "\033[0m", end="")
		else:
			print(column, end="")

		#print end part of buffer
		#same math as beginning part, but rounding down this time. This ensures that if there's
		#uneaven buffer, the extra always goes to the front
		print(" " * (math.floor((columnWidths[i] - len(column))/2)), end= "")

		print("|", end="")
		i += 1;
	print("")
	print("=" * tableWidth)

	# print the rest of the rows
	r = 0
	for row in content:
		print("|", end="")
		c = 0
		for column in columns:
			#print beginning part of buffer
			#subtract the width of the column name from the width of the column to get buffer size
			#divide buffer size down rounding up
			print(" " * (math.ceil((columnWidths[c] - len(str(content[r][c])))/2)), end="")

			#print the content
			print(content[r][c], end="")

			#print end part of buffer
			#same math as beginning part, but rounding down this time. This ensures that if there's
			#uneaven buffer, the extra always goes to the front
			print(" " * (math.floor((columnWidths[c] - len(str(content[r][c])))/2)), end= "")
				
			print("|", end="")
			c += 1
			
		print("")
		print("-" * tableWidth)
		r+=1


main()