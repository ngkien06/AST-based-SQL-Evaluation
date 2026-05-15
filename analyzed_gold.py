
import json

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

with open('bird_dev_gold_sql.json', 'r') as f:
    data = json.load(f)


complexity_lists = {
    'is_nested': [],
    'high_joins': [],
    'high_clauses': []
}

for item in data:
    g_sql = item['gold_tokens']
    g_str = item['goldSQL']

    complexity = get_complexity(g_sql, g_str)
    if complexity['is_nested'] == True:
        complexity_lists['is_nested'].append(g_str)
        #print(g_str)
    if complexity['num_joins'] >= 1:
        complexity_lists['high_joins'].append(g_str)
    if complexity['total_clauses'] >= 5:
        complexity_lists['high_clauses'].append(g_str)

print("\nComplexity Analysis:")
#print(f"Average Joins: {avr_joins / len(data):.2f}")
#print(f"Average Clauses: {avr_clauses / len(data):.2f}")
print(f"High Joins (>=1): {len(complexity_lists['high_joins'])} examples")
print(f"High Clauses (>=6): {len(complexity_lists['high_clauses'])} examples")
print(f"Nested Queries: {len(complexity_lists['is_nested'])} examples")