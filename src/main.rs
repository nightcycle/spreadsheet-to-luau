use std::env;
use std::collections::HashMap;
use std::fs::File;
use std::io::Write;
use reqwest;
use tokio::runtime::Runtime;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
struct Table {
	cols: Vec<Column>,
	rows: Vec<Row>,
}

#[derive(Serialize, Deserialize, Debug)]
struct Column {
	id: String,
	label: String,
	r#type: String,
	pattern: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
struct Row {
	c: Vec<Value>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(untagged)]
enum Value {
	String(String),
	Number { v: f64, f: String },
}

#[derive(Serialize, Deserialize, Debug)]
struct Data {
	version: String,
	reqId: String,
	status: String,
	sig: String,
	table: Table,
	parsedNumHeaders: u32,
}

fn parse_args(args: Vec<String>) -> HashMap<String, String> {
	let mut properties = HashMap::new();
	let mut args_iter = args.into_iter().peekable();

	while let Some(arg) = args_iter.next() {
		if arg.starts_with("--") {
			let prop = arg[2..].to_string();
			let val = args_iter.next().unwrap_or_else(|| String::new());
			properties.insert(prop, val);
		} else {
			println!("Invalid argument: {}", arg);
		}
	}

	return properties
}

fn get_request_url(sheet_id: &String, page_id: &String) -> String {
	let url_start = String::from("https://docs.google.com/spreadsheets/d/");
	let url_mid = String::from("/gviz/tq?tqx=out:json&gid=");
	let url = format!("{}{}{}{}", url_start, sheet_id, url_mid, page_id);
	return url;
}

async fn fetch_google_sheet(url: &String) -> Result<String, reqwest::Error> {
	let client = reqwest::Client::new();

	let response = client
	    .get(url)
	    .header("X-DataSource-Auth", "true")
	    .send()
	    .await
	    .unwrap()
	    .text()
	    .await;

	return response;
}

fn deserialize_data(json_string: &str) -> serde_json::Result<Data> {
	let data_result: Data = serde_json::from_str(json_string)?;
	return Ok(data_result);
}

fn write_data_to_file(data: &Data, file_path: &str) -> std::io::Result<()> {
	let json_string = serde_json::to_string_pretty(data)?;
	let mut file = File::create(file_path)?;
	file.write_all(json_string.as_bytes())?;
	Ok(())
 }
 

fn main() {
	let args: Vec<String> = env::args().skip(1).collect();
	let properties = parse_args(args);

	let sheet_key = "sheet";
	let page_key = "page";
	let out_key = "o";
	let input_key = "in";

	// build from google sheet
	if properties.contains_key(sheet_key) {

		// assert all the keys exist
		assert!(properties.contains_key(sheet_key), "the parameter {} was not included", sheet_key);
		assert!(properties.contains_key(page_key), "the parameter {} was not included", page_key);
		assert!(properties.contains_key(out_key), "the parameter {} was not included", out_key);
	
		// assemble the url
		if let Some(sheet_id) = properties.get(sheet_key) {
			if let Some(page_id) = properties.get(page_key) {
				if let Some(out_path) = properties.get(out_key) {
					
					let url = get_request_url(sheet_id, page_id);
					println!("request url: {}", url);
					let async_block = async {
						let data_result = fetch_google_sheet(&url).await;
						let data_string = match data_result {
							Ok(file) => file,
							Err(error) => panic!("Problem opening the file: {:?}", error),
						};
						println!("data_result: {}", &data_string);
						let data_result: serde_json::Result<Data> = deserialize_data(&data_string);
						match data_result {
							Ok(data) => {
								match write_data_to_file(&data, "output.json") {
									Ok(_) => {
										println!("Data successfully written to output.json");
									}
									Err(e) => {
										eprintln!("Failed to write data to file: {}", e);
									}
								}
							}
							Err(e) => {
								eprintln!("Failed to deserialize JSON string: {}", e);
							}
						};

					};
					let rt = Runtime::new().unwrap();
					rt.block_on(async_block);
					
				} else {
					println!("{} is none", out_key);
				}
			} else {
				println!("{} is none", page_key);
			}
		} else {
			println!("{} is none", sheet_key);
		}

	// build from csv or xlsx 
	} else if properties.contains_key(input_key) {

	}

}