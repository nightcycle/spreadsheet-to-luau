import re
from typing import Any

# creates a recursive luau table
def insert_comma(enabled: bool) -> str:
	if enabled:
		return ","
	else:
		return ""

def get_indent(indent_count: int) -> str:
	return "\t"*indent_count

def dump_bool(value: bool, indent_count=0, add_comma_at_end=False) -> str:
	return get_indent(indent_count) + str(value).lower() + insert_comma(add_comma_at_end)

def dump_str(value: str, indent_count=0, add_comma_at_end=False) -> str:
	return get_indent(indent_count) + f"\"{value}\"" + insert_comma(add_comma_at_end)

def dump_number(value: int | float, indent_count=0, add_comma_at_end=False) -> str:
	return get_indent(indent_count) + str(value) + insert_comma(add_comma_at_end)

def dump_nil(indent_count=0, add_comma_at_end=False) -> str:
	return f"{get_indent(indent_count)} nil" + insert_comma(add_comma_at_end)


def dump_list(value: list, indent_count=0, add_comma_at_end=False, multi_line=True, skip_initial_indent=False):
	
	# start list
	list_val = ""
	if skip_initial_indent:
		list_val += "{"
	else:
		list_val += get_indent(indent_count) + "{"

	# iterate through values
	for v in value:
		
		# write entry
		if type(v) == dict or type(v) == list:
			entry = dump(v, indent_count+1, False, multi_line, True) + insert_comma(True)
		else:
			entry = dump(v, indent_count, False, multi_line, True) + insert_comma(True)

		# add it to existing string
		if multi_line:
			list_val += "\n" + get_indent(indent_count+1) + entry
		else:
			list_val += entry

	# end the table on a new line if multi-line
	if multi_line:
		list_val += "\n" + get_indent(indent_count)

	# close the table
	list_val += "}"

	# indent as needed and return value
	return get_indent(indent_count) + list_val + insert_comma(add_comma_at_end)

def dump_dict(value: dict, indent_count=0, add_comma_at_end=False, multi_line=True, skip_initial_indent=False):
	
	# start dictionary
	list_val = ""
	if skip_initial_indent:
		list_val += "{"
	else:
		list_val += get_indent(indent_count) + "{"

	# iterate through key-val pairs
	for k, v in value.items():

		# write entry
		if type(v) == dict or type(v) == list:
			entry = f"[{dump(k, 0, False)}] = {dump(v, indent_count+1, False, multi_line, True)}" + insert_comma(True)
		else:
			entry = f"[{dump(k, 0, False)}] = {dump(v, 0, False, multi_line, True)}" + insert_comma(True)

		# add it to existing string
		if multi_line:
			list_val += "\n" + get_indent(indent_count+1) + entry
		else:
			list_val += entry

	# end the table on a new line if multi-line
	if multi_line:
		list_val += "\n" + get_indent(indent_count)

	# close the table
	list_val += "}"

	# indent as needed and return value
	if skip_initial_indent:
		return get_indent(0) + list_val + insert_comma(add_comma_at_end)
	else:
		return get_indent(indent_count) + list_val + insert_comma(add_comma_at_end)

def dump_type(type_table: dict, indent_count=0, skip_initial_indent=False, add_comma_at_end = False) -> str:
	out = ""
	if skip_initial_indent:
		out += "{"
	else:
		out += get_indent(indent_count) + "{"

	for k in type_table:
		v = type_table[k]

		# write entry
		if type(v) == dict or type(v) == list:
			entry = f"{k}: {dump_type(type_table, indent_count+1, True, False)}" + insert_comma(True)
		else:
			entry = f"{k}: {v}" + insert_comma(True)
	
		out += "\n" + get_indent(indent_count+1) + entry

	out += "\n" + get_indent(indent_count) + "}" + insert_comma(add_comma_at_end)
	return out

def dump(
	value: int | str | None | float | dict | list = None, 
	indent_count = 0, 
	add_comma_at_end = False, 
	multi_line=True,
	skip_initial_indent=False
) -> str:

	if type(value) == list:

		return dump_list(value, indent_count, add_comma_at_end, multi_line, skip_initial_indent)

	elif type(value) == dict:
		
		return dump_dict(value, indent_count, add_comma_at_end, multi_line, skip_initial_indent)

	elif type(value) == float or type(value) == int:
		return dump_number(value, indent_count, add_comma_at_end)
		
	elif type(value) == bool:
		return dump_bool(value, indent_count, add_comma_at_end)
		
	elif type(value) == str:
		return dump_str(value, indent_count, add_comma_at_end)
		
	return dump_nil(indent_count, add_comma_at_end)
