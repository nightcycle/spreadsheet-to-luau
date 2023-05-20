import src.dataretriever as dataretriever
import multiprocessing
import os
import shutil
import sys
import pandas as pd
from luau.convert import from_any, from_dict_to_type
from luau.roblox import write_script as write_luau_script
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
SUB_DIVIDE_PARAM_NAME = PREFIX+"sub"
TYPE_PARAM_NAME = PREFIX+"type"
VERBOSE_TAG = PREFIX+"verbose"
TOP_COMMENT = "\n-- this script was generated using spreadsheet-to-luau\n-- manual editing not recommended\n"

def main() -> None:

	# parse command
	input_mode: InputModeType | None = None
	input_path: None | str = None
	id_column_name: None | str = None
	remove_space_enabled = False
	google_sheet_id: None | str = None
	google_page_id: None | str = None
	out_path: None | str = None
	entry_type_name: None | str = None
	is_verbose = VERBOSE_TAG in sys.argv
	sub_division_lists: list[str] = []
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
				elif TYPE_PARAM_NAME == key:
					entry_type_name = sys.argv[i+1]
				elif SUB_DIVIDE_PARAM_NAME == key:
					sub_division_lists.append(sys.argv[i+1])
	# run command
	# print(f"input_mode: {input_mode}")
	# print(f"input_path: {input_path}")
	# print(f"google_sheet_id: {google_sheet_id}")
	# print(f"google_page_id: {google_page_id}")
	# print(f"id_column_name: {id_column_name}")
	# print(f"remove_space_enabled: {remove_space_enabled}")
	# print(f"out_path: {out_path}")
	def write_script(data_path: str, data: dict[str, dict] | list[dict], type_data: dict, write_as_directory=False):
		type_name = "EntryData"
		if entry_type_name != None:
			assert entry_type_name
			type_name = entry_type_name
		type_str = f"export type {type_name} = " + from_dict_to_type(type_data, add_comma_at_end=False)
	
		if out_path == None:
			print("-- no out path provided")
			print(from_any(f"return {from_any(data)}"))
		else:
			assert out_path
			print(f"writing to {out_path}")

			base_path, path_ext = os.path.splitext(out_path)
			assert base_path

			content = f"--!strict{TOP_COMMENT}\n{type_str}\nreturn {from_any(data)}"

			write_luau_script(data_path, content, write_as_directory, packages_dir_zip_file_path=None, skip_source_map=True, rojo_project_path=None)
			
	def export_data(data: dict[str, dict] | list[dict], type_data: dict, path=out_path, index=0):
		if index == 0:
			base_path, base_ext = os.path.splitext(path)

			if os.path.exists(base_path):
				shutil.rmtree(base_path)

			if os.path.exists(path):
				os.remove(path)

		if len(sub_division_lists) - 1 >= index:
			column_key = sub_division_lists[index]
			if remove_space_enabled:
				column_key = column_key.replace(" ", "")
			values: dict[str, Any] = {}
			if type(data) == list:
				for entry in data:
					val = entry[column_key]
					if not val in values:
						values[val] = []

					values[val].append(entry)
			else:
				assert(type(data) == dict)
				
				for key, entry in data.items():
					val = entry[column_key]
					if not val in values:
						values[val] = {}

					values[val][key] = entry

			next_index = index+1
			dir_name, file_ext = os.path.splitext(path)
			for mod_name, mod_data in values.items():
				export_data(mod_data, type_data, path=dir_name+"/"+mod_name+file_ext, index=next_index)
		else:
			write_script(path, data, type_data)

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
		export_data(data, type_data)

	elif input_mode == "csv":
		assert input_path
		# print(f"running {input_mode}")
		csv_df: DataFrame = pd.read_csv(input_path)
		data, type_data = dataretriever.get_df_data(csv_df, id_column_name, remove_space_enabled, is_verbose)
		export_data(data, type_data)

	elif input_mode == "xlsx":
		if google_sheet_id == None:
			google_sheet_id = "0"
		assert input_path, google_sheet_id
		# print(f"running {input_mode}")
		# print(f"sheet {google_sheet_id}")
		xlsx_df: DataFrame = pd.read_excel(input_path)
		data, type_data = dataretriever.get_df_data(xlsx_df, id_column_name, remove_space_enabled, is_verbose)
		export_data(data, type_data)

# prevent from running twice
if __name__ == '__main__':
	multiprocessing.freeze_support()
	main()		

