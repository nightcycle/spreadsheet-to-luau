import json
import requests
import shutil
import luau
import pandas as pd
from pandas import DataFrame
from typing import TypedDict, Any, Literal

# create a balance file
GoogleSheetStatus = Literal["ok"]
GoogleSheetDataType = Literal["string", "number", "bool"]
GoogleGeneralPattern = Literal["General"]
RobloxLuauType = Literal["string", "number", "boolean"]

class GoogleSheetCellData(TypedDict):
	v: str | float | int | bool
	f: str | None

class GoogleSheetRowData(TypedDict):
	c: list[GoogleSheetCellData]

class GoogleSheetColumnData(TypedDict):
	id: str
	label: str
	type: GoogleSheetDataType
	pattern: str | GoogleGeneralPattern | None

class GoogleSheetDataTable(TypedDict):
	cols: list[GoogleSheetColumnData]
	rows: list[GoogleSheetRowData]
	parsedNumHeaders: int

class GoogleSheetData(TypedDict):
	version: str
	reqId: str
	status: GoogleSheetStatus
	sig: str
	table: GoogleSheetDataTable

GOOGLE_TYPE_TRANSLATIONS: dict[GoogleSheetDataType, RobloxLuauType] = {
	"string": "string",
	"number": "number",
	"bool": "boolean",
}

def get_df_data(
	df: DataFrame,
	id_column_name: str | None = None,
	remove_spaces_from_column_name=True
) -> tuple[dict[str, dict] | list[dict], dict[str, RobloxLuauType]]:
		
	# format the id column
	if remove_spaces_from_column_name and id_column_name != None:
		assert id_column_name
		id_column_name = id_column_name.replace(" ", "")

	type_data = {}
	out_dict: dict[str, dict] = {}
	out_list: list[dict] = []

	for record in df.to_dict(orient='records'):
		entry: dict = {}
		for k in record:
			v = record[k]
			if remove_spaces_from_column_name: 
				assert type(k) == str
				k = k.replace(" ", "")
			if not k in type_data:
				if type(v) == str:
					type_data[k] = "string"
				elif type(v) == bool:
					type_data[k] = "boolean"
				elif type(v) == int:
					type_data[k] = "number"
				elif type(v) == float:
					type_data[k] = "number"
				
			entry[k] = v
		
		if id_column_name != None:
			assert id_column_name
			id_val: str = entry[id_column_name]
			assert not id_val in out_dict, f"duplicate id ({id_column_name})"
			out_dict[id_val] = entry
		else:
			out_list.append(entry)

	
	untyped_out_dict: Any = out_dict
	untyped_out_list: Any = out_list
	untyped_type_data: Any = type_data

	if id_column_name != None:
		return untyped_out_dict, untyped_type_data
	else:
		return untyped_out_list, untyped_type_data


def get_google_sheet_data(
	sheet_id: str, 
	page_id: str, 
	id_column_name: str | None = None,
	remove_spaces_from_column_name=True
) -> tuple[dict[str, dict] | list[dict], dict[str, RobloxLuauType]]:
	url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:json&gid={page_id}"

	# http request
	response = requests.get(url, headers={
		"X-DataSource-Auth": "true"
	})
	assert response.status_code == 200, 'wrong status code'

	google_sheet_data: GoogleSheetData = json.loads(response.content.decode('utf8').replace("'", '"').replace(')]}"', ""))
	google_table_data: GoogleSheetDataTable = google_sheet_data["table"]
	
	# format the id column
	if remove_spaces_from_column_name and id_column_name != None:
		assert id_column_name
		id_column_name = id_column_name.replace(" ", "")


	# get column information
	column_names: list[str] = []
	column_types: list[RobloxLuauType] = []
	type_data = {}
	for column_data in google_table_data["cols"]:
		google_type = column_data["type"]
		roblox_type = GOOGLE_TYPE_TRANSLATIONS[google_type]
		column_types.append(roblox_type)
		label_name = column_data["label"]
		
		if remove_spaces_from_column_name: 
			label_name = label_name.replace(" ", "")

		column_names.append(label_name)
		type_data[label_name] = roblox_type

	out_dict: dict[str, dict] = {}
	out_list: list[dict] = []
	# format edit rows
	for row_data in google_table_data["rows"]:
		entry: dict = {}

		for column_index, cell in enumerate(row_data["c"]):
			value = cell["v"]
			column_name = column_names[column_index]
			column_type = column_types[column_index]	
			entry[column_name] = value
			
		if id_column_name != None:
			assert id_column_name
			id_val: str = entry[id_column_name]
			assert not id_val in out_dict, f"duplicate id ({id_column_name}) in page {page_id} of sheet {sheet_id}"
			out_dict[id_val] = entry
		else:
			out_list.append(entry)

	if id_column_name != None:
		return out_dict, type_data
	else:
		return out_list, type_data
