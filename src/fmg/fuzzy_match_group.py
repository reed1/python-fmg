from thefuzz import fuzz

def fuzzy_match_group(
        a_rows,
        a_field,
        b_rows,
        b_field,
        min_score=85,
        forced_matches=set()):
    pairs = []
    a_rows = a_rows[:]
    b_rows = b_rows[:]
    a_values = [(e[a_field] if a_field is not None else e).lower()
                for e in a_rows]
    b_values = [(e[b_field] if b_field is not None else e).lower()
                for e in b_rows]
    fm = [(a.lower(), b.lower()) for (a, b) in forced_matches]
    i = 0
    while i < len(a_values):
        found = False
        for j in range(len(b_values)):
            if a_values[i] == b_values[j] or (a_values[i], b_values[j]) in fm:
                if a_values[i] == b_values[j]:
                    score = 100
                else:
                    score = fuzz.ratio(a_values[i], b_values[j])
                pairs.append({'a': a_rows[i], 'b': b_rows[j], 'score': score})
                a_rows.pop(i)
                a_values.pop(i)
                b_rows.pop(j)
                b_values.pop(j)
                found = True
                break
        if not found:
            i += 1
    candidates = sorted([
        (i, j, fuzz.ratio(a_values[i], b_values[j]))
        for i in range(len(a_values))
        for j in range(len(b_values))
    ], key=lambda x: -x[2])
    i_taken = set()
    j_taken = set()
    for i, j, score in candidates:
        if score >= min_score and i not in i_taken and j not in j_taken:
            pairs.append({'a': a_rows[i], 'b': b_rows[j], 'score': score})
            i_taken.add(i)
            j_taken.add(j)

    not_takens = []
    for i, j, score in candidates:
        if i not in i_taken and j not in j_taken:
            not_takens.append({'a': a_rows[i], 'b': b_rows[j], 'score': score})

    no_match = {'a': [], 'b': []}
    for i in range(len(a_rows)):
        if i not in i_taken:
            no_match['a'].append(a_rows[i])
    for j in range(len(b_rows)):
        if j not in j_taken:
            no_match['b'].append(b_rows[j])
    mapping = {}
    for p in pairs:
        a_value = p['a'][a_field] if a_field is not None else p['a']
        b_value = p['b'][b_field] if b_field is not None else p['b']
        mapping[a_value] = b_value
    return {
        'pairs': pairs,
        'no_match': no_match,
        'mapping': mapping,
        'not_takens': sorted(not_takens, key=lambda x: -x['score'])
    }
