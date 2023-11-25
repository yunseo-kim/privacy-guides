#! /bin/sh

printf "%s\n" "Updating korean-first-names.txt…"

python3 scrape-korean-first-names.py
< ../korean_name_data.json jq -c '.pages[].props.pageProps.data.items[].langs.en' \
| sed 's/"//g' > ../korean-first-names.txt

printf "%s\n" "Done"