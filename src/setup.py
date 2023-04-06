from cx_Freeze import setup,Executable


includefiles = ['README.md'] #, 'src', 'helpers\uncompress\unRAR.exe', , 'helpers\uncompress\unzip.exe']
includes: list[str] = []
excludes: list[str] = ["virtualenv", "mypy"]
packages: list[str] = [
	# "json",
	# "requests",
	# "re",
	# "os",
	# "shutil",
	# "math",
	# "sys",
	# "pandas",
	# "typing",
	# "dataretriever",
	# "luau"
]

setup(
    name = 'spreadsheet-to-luau',
    version = '0.1',
    description = 'Allows you to generate a luau modulescript tree from a google sheet, csv, or xlsx file',
    author = 'coyer',
    author_email = 'coyer@nightcycle.us',
    options = {
		'build_exe': {
			"optimize": 0,
			'includes':includes,
			'excludes':excludes,
			'packages':packages,
			'include_files':includefiles
		}
	}, 
    executables = [Executable('src/__init__.py')]
)