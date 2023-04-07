# spreadsheet-to-luau
With this you can make sure that the scripts in your game are always reading from the most up-to-date version of balancing, while allowing your designers to do their work in more industry standard tools like Excel and Google Sheets.

It should be able to be installed with Aftman and Foreman, otherwise it is downloadable as an exe under releases for manual addition to your path environment.

## Demo
This tool takes a csv / xlsx / google sheet and converts it into a strictly typed roblox modulescript. 

This is an example CSV file:
```csv
a, b, c
1, 2, 3
4, 5, 6
7, 8, 9
```

This is the type of script the tool generates:
```lua
--!strict
export type EntryData = {
  a: number,
  b: number,
  c: number
}

return {
  {
    a = 1,
    b = 2,
    c = 3,
  },
  {
    a = 4,
    b = 5,
    c = 6,
  },
  {
    a = 7,
    b = 8,
    c = 9
  }
} :: {[number]: EntryData}
```

## Converting CSV / XSLX
The first argument should be the path to the source file (when one is needed), the output path is then provided following the -o marker. 

### CSV
```bash
spreadsheet-to-luau path/to/file.csv -o path/to/luau/script.luau
```
### XLSX
```bash
spreadsheet-to-luau path/to/file.xlsx -o path/to/luau/script.luau
```
You don't need to end your path with .luau, this does work with lua, however since luau is technically a new language with patterns that could break standard lua interpreters, it's better in most cases to use the proper extension.

## Converting a Google Sheet
In the modern age of the internet, living document services like Google Sheet can be useful for collaborative projects. You can take a snapshot of them using this tool.

### Preparing the Google Sheet
On the google sheet page open the publish menu by going to File -> Share -> Publish to Web. In the "Link" tab, configure it to publish with the configuration of "Entire Document" and "Web Page". The press publish and you should be good.

### Finding Sheet and Page Ids
From the URL of the sheets page the sheet and page ids are stored at these points:
```
https://docs.google.com/spreadsheets/d/SHEET_ID/edit#gid=PAGE_ID
```

### Converting the Main Page
Running this will download and write the main page as a balancing file.
```bash
spreadsheet-to-luau -sheet SHEET_ID -o path/to/luau/script.luau
```

### Converting a Specific Page
If you want to download a page other than the main one, you can specify it like so:
```bash
spreadsheet-to-luau -sheet SHEET_ID -page PAGE_ID -o path/to/luau/script.luau
```

## Formatting Parameters
You can further specify the way the module-script beyond supplying the source and output path.

### Remove Spaces from Column Names
Include the tag -nospace to remove spaces from the column names.
```bash
spreadsheet-to-luau -sheet SHEET_ID -o path/to/luau/script.luau -nospace
```

### Specify an Id Column / Export as Dictionary
If the columns have a unique value that can be used as a key in the final luau table, you can specify it following the -id marker. 
```bash
spreadsheet-to-luau -sheet SHEET_ID -o path/to/luau/script.luau -id Name
```
If you don't include this tag it will simply write the final luau table in list format in the order which they were arranged in the source.

### Specify Entries Per Sub-Module
For those using a rojo workflow, larger scripts can fail to sync. To avoid this issue when a spreadsheet has more than 250 entries it will split into smaller sheets which are then compiled into a higher-level sheet. It shouldn't change any external usage, however in instances where the 250 entries have a ton of data it can still cause a rojo failure. Because of this you can configure the split size with the -split marker.
```bash
spreadsheet-to-luau -sheet SHEET_ID -o path/to/luau/script.luau -split 100
```

### Type Exporting
All scripts were generated to support type safety principals, which includes generating an exportable custom luau datatype. You can set the name of that datatype with -type. 
```bash
spreadsheet-to-luau -sheet SHEET_ID -o path/to/luau/script.luau -type TypeNameHere
```
The default type name is "EntryData". 

## Development
### Motivation
Spreadsheets are the best way to do lightweight designing of systems with numerous unique entities containing the same properties. Game development can benefit much from them, by automating the conversion of spreadsheets to balancing data you cutout the risk of manual translation mistakes, as well as decrease the amount of time needed to replicate changes.

### Contributing
If you want to try to add features yourself go for it, this is written in Python because Rust gives me too much of a headache and I don't need this to run in a single millisecond. It's compiled with PyInstaller as an .exe.

### Future Improvements
I'll probably add more command like tags and markers, as well as support for other spreadsheet sources / output formats if there's enough demand for that.

### Support
Feel free to sponsor my github page to show support / say thanks if this helped you out.
