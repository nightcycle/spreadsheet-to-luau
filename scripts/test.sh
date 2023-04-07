#!/bin/bash
py src/__init__.py test/in/test.csv -nospace -id Name -o test/out/csv.luau
py src/__init__.py test/in/test.xlsx -nospace -id Name -o test/out/xlsx.luau
py src/__init__.py -sheet 1-oZ16B2k9k-jj3APokzYILdPj1oavLxmv3CMUQ9Zkr0 -nospace -o test/out/google.luau -id Id

