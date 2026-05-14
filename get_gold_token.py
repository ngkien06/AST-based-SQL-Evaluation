import json

from evaluation import build_foreign_key_map_from_json, build_valid_col_units, rebuild_sql_val, rebuild_sql_col
from process_sql_bird import tokenize, get_schema, get_tables_with_alias, Schema, get_sql

file_name = "bird_dev_gold_sql.json"
table = "bird_dev_tables.json"

with open(file_name) as f:
    data = json.load(f)

print(f"load {len(data)} from {file_name}")

gold_sql = []

kmaps = build_foreign_key_map_from_json(table)

for item in data:
    g_str = item['goldSQL']
    db_path = item['db_path']
    db_name = item['db_path'].split('/')[-2]  # extract db_name from original path first
    db_path = f"F:/Personal Stuff/Uni/Sem 5/Lab/Technical Writing/DIN_SQL/DIN_SQL/dev_databases/dev_databases/{db_name}/{db_name}.sqlite"
    #print(f"{db_name}: {db_path}")

    schema = Schema(get_schema(db_path))

    print("=====================================================================")
    print(g_str)
    try:
        g_sql = get_sql(schema, g_str)
    except AssertionError as e:
        error_msg = str(e)
        if 'Error col:' in error_msg:
            unsupported_token = error_msg.split('Error col:')[-1].strip()
            print(f"Unsupported token: '{unsupported_token}'")
        else:
            print(f"Other assertion: {error_msg}")
        continue
    except Exception as e:
        print(f"Other error type {type(e).__name__}: {e}")


    kmap = kmaps[db_name]
    g_valid_col_units = build_valid_col_units(g_sql['from']['table_units'], schema)
    g_sql = rebuild_sql_val(g_sql)
    g_sql = rebuild_sql_col(g_valid_col_units, g_sql, kmap)

    gold_sql.append({
        'goldSQL': g_str,
        'gold_tokens': g_sql
    })


with open(file_name, 'w') as f:
    json.dump(gold_sql, f, indent=4)

print(f"extract {len(gold_sql)} incorrect")