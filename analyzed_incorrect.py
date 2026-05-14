from calendar import c
import json

def classify_set_op_error(p_sql, g_sql):
    p_has_set = any(p_sql.get(op) for op in ['union','intersect','except'])
    g_has_set = any(g_sql.get(op) for op in ['union','intersect','except'])
    
    if not p_has_set and not g_has_set:
        return None  # No set ops in either
    
    # type mismatch
    for op in ['union', 'intersect', 'except']:
        if bool(p_sql.get(op)) != bool(g_sql.get(op)):
            return 'wrong_set_op_type'
    
    # content check
    for op in ['union', 'intersect', 'except']:
        if p_sql.get(op) and g_sql.get(op):
            if p_sql[op] != g_sql[op]:  # Spider's deep AST equality
                return f'wrong_set_op_content'
    
    return 'set_op_match'  # Same type AND content

def classify_error(p_sql, g_sql):

    # Check FROM tables
    p_tables = p_sql['from']['table_units']
    g_tables = g_sql['from']['table_units']
    if len(p_tables) != len(g_tables):
        return 'missing_join'
    if p_tables != g_tables:
        return 'wrong_tables'
    
    #print(g_tables)
    
    # Compare SELECT 
    if len(p_sql.get('select', [])) != len(g_sql.get('select', [])):
        return 'wrong_columns'
    if p_sql.get('select', []) != g_sql.get('select', []):
        return 'wrong_columns'
    
    # Check set ops
    op_chk = classify_set_op_error(p_sql, g_sql)
    if op_chk and op_chk != 'set_op_match':
        return op_chk

    # Check WHERE
    if p_sql.get('where') != g_sql.get('where'):
        return 'wrong_condition'

    # Check ORDER and LIMIT
    if p_sql.get('orderBy') != g_sql.get('orderBy'):
        return 'wrong_order_limit'
    if p_sql.get('limit') != g_sql.get('limit'):
        return 'wrong_order_limit'
    
    return 'exec_only'  


def has_nesting(query):
    open_paren = query.count('(')
    close_paren = query.count(')')
    
    # If there are parentheses and multiple SELECTs, high chance of nested queries
    if open_paren > 0 and query.upper().count('SELECT') > 1:
        return True
    
    # Even with one SELECT, parentheses might indicate derived tables or subqueries
    if open_paren > 0 and any(keyword in query.upper() for keyword in [' IN ', ' EXISTS ', ' FROM (']):
        return True
        
    return False

operators_to_count = [
    'SELECT', 'FROM', 'WHERE', 'JOIN', 'GROUP BY', 'HAVING', 
    'ORDER BY', 'LIMIT', 'DISTINCT', 'COUNT', 'SUM', 'AVG',
    'MAX', 'MIN', 'AND', 'OR', 'NOT', 'IN', 'BETWEEN',
    'LIKE', 'EXISTS', 'CASE', 'WHEN', 'THEN', 'END', 'INTERSECT' 
]

def count_operators(query):
    query_upper = query.upper()
    operator_count = {}
    c = 0
    
    for operator in operators_to_count:
        # Count occurrences of each operator
        count = query_upper.count(operator)
        if count > 0:
            operator_count[operator] = count
            c += count
    
    return c

def get_complexity(p_sql, p_str):
    joins = len(p_sql['from']['conds'])
    clauses = sum(1 for v in p_sql.values() if v)
    #clauses = count_operators(p_str)
    is_nested = has_nesting(p_str)
    return {
        'num_joins': joins,
        'total_clauses': clauses,
        'is_nested': is_nested
    }


file_name = 'spider_dev_incorrect_sql_XiYan.json'
with open(file_name, 'r') as f:
    data = json.load(f)

classify_lists = {
    'parse_fail': [],
    'wrong_columns': [],
    'missing_join': [],
    'wrong_tables': [],
    'wrong_set_op_type': [],
    'wrong_set_op_content': [],
    'wrong_order_limit': [],
    'wrong_condition': [],
    'exec_only': []
}

complexity_lists = {
    'is_nested': [],
    'high_joins': [],
    'high_clauses': []
}
avr_joins = 0
avr_clauses = 0

for item in data:
    p_sql = item['predicted_tokens']
    g_sql = item['gold_tokens']
    p_str = item['predictSQL']
    g_str = item['goldSQL']

    complexity = get_complexity(g_sql, g_str)
    if complexity['is_nested'] == True:
        complexity_lists['is_nested'].append(g_str)
        #print(g_str)
    if complexity['num_joins'] >= 1:
        complexity_lists['high_joins'].append(g_str)
    if complexity['total_clauses'] >= 5:
        complexity_lists['high_clauses'].append(g_str)


    avr_joins += complexity['num_joins']
    avr_clauses += complexity['total_clauses']

    if item['is_invalid'] == True:
        classify_lists['parse_fail'].append({
            'predictSQL': item['predictSQL'],
            'goldSQL': item['goldSQL']
        })
        continue
    
    error_type = classify_error(p_sql, g_sql)
    classify_lists[error_type].append({
        'predictSQL': p_str,
        'goldSQL': g_str
    })

for key, lst in classify_lists.items():
    print(f"{key}: {len(lst)} examples")

print("\nComplexity Analysis:")
#print(f"Average Joins: {avr_joins / len(data):.2f}")
#print(f"Average Clauses: {avr_clauses / len(data):.2f}")
print(f"High Joins (>=1): {len(complexity_lists['high_joins'])} examples")
print(f"High Clauses (>=6): {len(complexity_lists['high_clauses'])} examples")
print(f"Nested Queries: {len(complexity_lists['is_nested'])} examples")


print()
for item in classify_lists['exec_only']:  # Print first 5 examples
    print("Predicted:", item['predictSQL'])
    print("     Gold:", item['goldSQL'])
    print()

'''
for item in complexity_lists['high_clauses'][:5]:  # Print first 5 examples
    print("SQL:", item)
    print()
'''