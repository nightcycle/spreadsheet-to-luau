#!/bin/bash
source env/Scripts/Activate
sh scripts/to_exe.sh
# dist/spreadsheet-to-luau -o out/Shared/Balancing/Vehicle.luau -page 0  -id Id -nospace -sheet 1-oZ16B2k9k-jj3APokzYILdPj1oavLxmv3CMUQ9Zkr0
# dist/spreadsheet-to-luau -o out/Shared/Balancing/City.luau -page 452549796 -id Id -nospace -sheet 1-oZ16B2k9k-jj3APokzYILdPj1oavLxmv3CMUQ9Zkr0 -sub State
# dist/spreadsheet-to-luau -o out/Vehicle.luau -page 1007097471 -id Id -nospace -sheet 1-oZ16B2k9k-jj3APokzYILdPj1oavLxmv3CMUQ9Zkr0 -sub VehicleClass -sub ConnectionType
dist/spreadsheet-to-luau -o out/Shared/Balancing/Merchandise.luau -page 1185151410 -id Id -nospace -sheet 1-oZ16B2k9k-jj3APokzYILdPj1oavLxmv3CMUQ9Zkr0 -sub MerchandiseClass -sub StorageClass
# dist/spreadsheet-to-luau -o out/Shared/Balancing/Loan.luau -page 1673384457 -id Id -nospace -sheet 1-oZ16B2k9k-jj3APokzYILdPj1oavLxmv3CMUQ9Zkr0
