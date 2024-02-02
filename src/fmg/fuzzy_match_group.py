from thefuzz import fuzz
import subprocess
import json
from collections import OrderedDict

fzf_forced_matches = OrderedDict()

def fuzzy_match_group(
        a_rows,
        a_field,
        b_rows,
        b_field,
        min_score=85,
        forced_matches=[],
        resolve_with_fzf=True,
        fzf_header=None):
    pairs = []
    a_rows = a_rows[:]
    b_rows = b_rows[:]
    a_values = [(e[a_field] if a_field is not None else e).lower()
                for e in a_rows]
    b_values = [(e[b_field] if b_field is not None else e).lower()
                for e in b_rows]
    a_origs = [(e[a_field] if a_field is not None else e) for e in a_rows]
    b_origs = [(e[b_field] if b_field is not None else e) for e in b_rows]
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
                a_origs.pop(i)
                b_rows.pop(j)
                b_values.pop(j)
                b_origs.pop(j)
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
            not_takens.append({
                'a': a_rows[i],
                'b': b_rows[j],
                'a_value': a_origs[i],
                'b_value': b_origs[j],
                'score': score,
            })
    not_takens = sorted(not_takens, key=lambda x: -x['score'])

    if resolve_with_fzf:
        new_pairs, new_not_takens = show_fzf(not_takens, fzf_header)
        for p in new_pairs:
            i_taken.add(a_rows.index(p['a']))
            j_taken.add(b_rows.index(p['b']))
        pairs += new_pairs
        not_takens = new_not_takens

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
        'not_takens': not_takens
    }


def show_fzf(not_takens, fzf_header):
    pairs = []
    while len(not_takens) > 0:
        lines = [
            ' | '.join([str(e[k]) for k in ['score', 'a_value', 'b_value']])
            for e in not_takens
        ]
        res = subprocess.run(
            ['fzf', *(['--header', str(fzf_header)] if fzf_header else [])],
            input='\n'.join(lines),
            text=True,
            check=True,
            stdout=subprocess.PIPE
        )
        line = res.stdout.strip()
        i = lines.index(line)
        a = not_takens[i]['a']
        b = not_takens[i]['b']
        pairs.append(not_takens[i])
        not_takens = [
            e for e in not_takens
            if e['a'] != a and e['b'] != b
        ]
    fzf_forced_matches[fzf_header] = [
        [e['a_value'], e['b_value']]
        for e in pairs
    ]
    return [pairs, not_takens]


def report_forced_matches():
    fm = OrderedDict()
    for k, v in fzf_forced_matches.items():
        if len(v) > 0:
            fm[k] = v
    print(json.dumps(fm, indent=4))
