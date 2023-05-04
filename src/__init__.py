import src.dataretriever as dataretriever
import src.luautranslate as luautranslate
import multiprocessing
import os
import shutil
import math
import sys
# import openpyxl
import pandas as pd
from pandas import DataFrame
from typing import Any, Literal

# types
InputModeType = Literal["xlsx", "google", "csv"]

# constants
PREFIX = "-"
ID_COLUMN_NAME_PARAM_NAME = PREFIX+"id"
REMOVE_SPACE_FROM_COLUMN_TAG_NAME = PREFIX+"nospace"
GOOGLE_SHEET_ID_PARAM_NAME = PREFIX+"sheet"
GOOGLE_PAGE_ID_PARAM_NAME = PREFIX+"page"
OUT_PATH_PARAM_NAME = PREFIX+"o"
LIMIT_PARAM_NAME = PREFIX+"split"
TYPE_PARAM_NAME = PREFIX+"type"
VERBOSE_TAG = PREFIX+"verbose"
TOP_COMMENT = "\n-- this script was generated using spreadsheet-to-luau\n-- manual editing not recommended\n"

def main():

	# parse command
	input_mode: InputModeType | None = None
	input_path: None | str = None
	id_column_name: None | str = None
	remove_space_enabled = False
	google_sheet_id: None | str = None
	google_page_id: None | str = None
	out_path: None | str = None
	entries_per_page_limit: int = 250
	entry_type_name: None | str = None
	is_verbose = VERBOSE_TAG in sys.argv
	assert len(sys.argv) > 1, "no arguments provided"

	for i, arg in enumerate(sys.argv):
		if i > 0:
			key = arg
			if key[(len(PREFIX)-1)] != PREFIX and i == 1:
				if (not i+1 in sys.argv) or (sys.argv[i+1][(len(PREFIX)-1)] == PREFIX):
					input_path = key
					base_path, path_ext = os.path.splitext(input_path)
					if path_ext == ".csv":
						input_mode = "csv"
					elif path_ext == ".xlsx":
						input_mode = "xlsx"
				else:
					value = sys.argv
			else:
				if ID_COLUMN_NAME_PARAM_NAME == key:
					id_column_name = sys.argv[i+1]

				elif REMOVE_SPACE_FROM_COLUMN_TAG_NAME == key:
					remove_space_enabled = True
				elif GOOGLE_SHEET_ID_PARAM_NAME == key:
					google_sheet_id = sys.argv[i+1]
					if google_page_id == None:
						google_page_id = "0"
					input_mode = "google"
				elif GOOGLE_PAGE_ID_PARAM_NAME == key:
					google_page_id = sys.argv[i+1]
				elif OUT_PATH_PARAM_NAME == key:
					out_path = sys.argv[i+1]
				elif LIMIT_PARAM_NAME == key:
					entries_per_page_limit = int(sys.argv[i+1])
				elif TYPE_PARAM_NAME == key:
					entry_type_name = sys.argv[i+1]
	# run command
	# print(f"input_mode: {input_mode}")
	# print(f"input_path: {input_path}")
	# print(f"google_sheet_id: {google_sheet_id}")
	# print(f"google_page_id: {google_page_id}")
	# print(f"id_column_name: {id_column_name}")
	# print(f"remove_space_enabled: {remove_space_enabled}")
	# print(f"out_path: {out_path}")
	def write_data(data: dict[str, dict] | list[dict], type_data: dict):
		type_name = "EntryData"
		if entry_type_name != None:
			assert entry_type_name
			type_name = entry_type_name
		type_str = f"export type {type_name} = " + luautranslate.dump_type(type_data, add_comma_at_end=False)
		type_ending = ""
		if type(data) == list:
			type_ending = " :: {[number]: "+type_name+"}"
		else:
			type_ending = " :: {[string]: "+type_name+"}"

		if out_path == None:
			print("-- no out path provided")
			print(luautranslate.dump(f"return {luautranslate.dump(data)}"))
		else:
			assert out_path
			print(f"writing to {out_path}")

			base_path, path_ext = os.path.splitext(out_path)
			assert base_path
			if os.path.exists(base_path):
				shutil.rmtree(base_path)

			if os.path.exists(out_path):
				os.remove(out_path)
				
			entry_count = 0
			if type(data) == list:
				entry_count = len(data)
			else:
				assert type(data) == dict
				entry_count = len(data.keys())

				key_type_name = f"{type_name}Keys"
				key_type = f"export type {key_type_name} ="
				for key in data:
					key_type += f" \"{key}\" |"
				key_type = key_type[0:(len(key_type)-2)]

				type_str += "\n\n" + key_type
				type_ending = " :: {["+key_type_name+"]: "+type_name+"}"

			if entry_count < entries_per_page_limit:
				out_file = open(out_path, "w")
				out_file.write(f"--!strict{TOP_COMMENT}\n{type_str}\nreturn {luautranslate.dump(data)}{type_ending}")
				out_file.close()
			else:
				os.makedirs(base_path)
				sub_file_count = math.ceil(entry_count / entries_per_page_limit)

				for i in range(1, sub_file_count):
					start_index = (i-1) * entries_per_page_limit
					finish_index = start_index+entries_per_page_limit-1
					sub_data_list = []
					sub_data_dict = {}
					sub_file = open(base_path+"/"+str(i)+path_ext, "w")
					if type(data) == list:
						sub_data_list = data[start_index:finish_index]
						sub_file.write(f"--!strict{TOP_COMMENT}\nreturn {luautranslate.dump(sub_data_list)}")
					else:
						assert type(data) == dict
						keys = list(data.keys())[start_index:finish_index]
						for key in keys:
							sub_data_dict[key] = data[key]
						sub_file.write(f"--!strict{TOP_COMMENT}\nreturn {luautranslate.dump(sub_data_dict)}")
					sub_file.close()
				
				out_text = f"--!strict{TOP_COMMENT}\n{type_str}\n" + "\nlocal out = {}\n"
				for i in range(1, sub_file_count):
					
					if type(data) == list:
						out_text += f"\nfor i, v in ipairs(require(script:WaitForChild(\"{i}\"))) do\n"
						out_text += f"\ttable.insert(out, v)\n"				
					else:
						out_text += f"\nfor k, v in pairs(require(script:WaitForChild(\"{i}\"))) do\n"
						out_text += f"\tout[k] = v\n"			

					out_text += "end\n"

				out_text += f"\nreturn out {type_ending}"

				out_file = open(base_path+"/init"+path_ext, "w")
				out_file.write(out_text)
				out_file.close()

	if input_mode == "google":
		# print(f"running {input_mode}")
		assert google_sheet_id
		assert google_page_id
		data, type_data = dataretriever.get_google_sheet_data(
			google_sheet_id, 
			google_page_id, 
			id_column_name,
			remove_space_enabled,
			is_verbose
		)
		write_data(data, type_data)

	elif input_mode == "csv":
		assert input_path
		# print(f"running {input_mode}")
		csv_df: DataFrame = pd.read_csv(input_path)
		data, type_data = dataretriever.get_df_data(csv_df, id_column_name, remove_space_enabled, is_verbose)
		write_data(data, type_data)

	elif input_mode == "xlsx":
		if google_sheet_id == None:
			google_sheet_id = "0"
		assert input_path, google_sheet_id
		# print(f"running {input_mode}")
		# print(f"sheet {google_sheet_id}")
		xlsx_df: DataFrame = pd.read_excel(input_path)
		data, type_data = dataretriever.get_df_data(xlsx_df, id_column_name, remove_space_enabled, is_verbose)
		write_data(data, type_data)

# prevent from running twice
if __name__ == '__main__':
	multiprocessing.freeze_support()
	main()		

