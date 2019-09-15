#!/usr/bin/env python
# coding: utf-8

# In[1]:


from dziban.mkiv import Chart
from vega_datasets import data
from copy import deepcopy
import json
from tqdm import tqdm
import pandas as pd


# In[2]:


movies = data('movies')
movies.head(1)


# In[3]:


base = Chart(movies)


# In[4]:


q1 = 'IMDB_Rating'
q2 = 'Rotten_Tomatoes_Rating'
q3 = 'Worldwide_Gross'
n1 = 'Major_Genre'
n2 = 'MPAA_Rating'
n3 = 'Creative_Type'

fields = {
    'q': [q1, q2, q3],
    'n': [n1, n2, n3]
}

marks = ['point', 'bar', 'line', 'area', 'tick', 'rect']
aggs = ['mean']


# In[5]:


def get_props_from_transform(transform):
    props = {}
    if (transform == 'bin'):
        props['bin'] = True
    elif (transform == 'agg'):
        props['aggregate'] = 'mean'
        
    return props


# In[6]:


def generate_queries(currdims, targetdims, curr_query, queries):
    if (currdims < targetdims):
        for fieldtype in ['q', 'n']:
            if (fieldtype == 'q'):
                for transform in ['raw', 'bin', 'agg']:
                    next_query = deepcopy(curr_query)
                    next_query.append({ 'fieldtype': fieldtype, 'transform': transform })
                    queries.append(next_query)

                    generate_queries(currdims + 1, targetdims, next_query, queries)
            else:
                next_query = deepcopy(curr_query)
                next_query.append({ 'fieldtype': fieldtype, 'transform': 'raw' })
                queries.append(next_query)

                generate_queries(currdims + 1, targetdims, next_query, queries)


# In[7]:


def dedupe_queries(queries):
    seen = set()
    
    unique = []
    for query in queries:
        reps = {}
        for field in query:
            string = '{0}({1})'.format(field['transform'], field['fieldtype'])
            if string not in reps:
                reps[string] = 0
            reps[string] += 1
            
        stringified = json.dumps(reps, sort_keys=True)
        
        if stringified not in seen:
            seen.add(stringified)
            unique.append(query)
            
    return unique
            


# In[8]:


def query_to_dziban(prior, query, available_fields):
    chart = prior
    
    used_fields = {}
    
    for field in query:
        fieldtype = field['fieldtype']
        transform = field['transform']
        
        fieldname = available_fields[fieldtype].pop(0)
    
        if (fieldtype not in used_fields):
            used_fields[fieldtype] = []
        used_fields[fieldtype].append(fieldname)
        
        props = get_props_from_transform(transform)
        
        props['ftype'] = 'quantitative' if fieldtype == 'q' else 'nominal'
            
        chart = chart.field(fieldname, **props)
        
    return {
        'chart': chart,
        'query': query,
        'available_fields': available_fields,
        'used_fields': used_fields
    }
        


# In[9]:


priors = []
generate_queries(0, 2, [], priors)
priors = dedupe_queries(priors)


# In[10]:


charts = [query_to_dziban(base, query, deepcopy(fields)) for query in priors]


# In[11]:


mark_edits = []
for mark in marks:
    mark_edits.append({
        'type': 'mark',
        'mark': mark
    })


# In[12]:


add_field_edits = []
for fieldtype in ['q', 'n']:
    if (fieldtype == 'q'):
        for transform in ['raw', 'bin', 'agg']:
            add_field_edits.append({
                'type': 'add_field',
                'fieldtype': fieldtype,
                'transform': transform
            })
            
    else:
        add_field_edits.append({
            'type': 'add_field',
            'fieldtype': fieldtype,
            'transform': 'raw'
        })


# In[13]:


bin_edits = [
    {
        'type': 'bin'
    }
]


# In[14]:


agg_edits = []
for agg in aggs:
    agg_edits.append(
        {
            'type': 'agg',
            'agg': agg
        }
    )


# In[15]:


edits = mark_edits + add_field_edits + bin_edits + agg_edits


# In[16]:


def edit_dziban(dzi, edit):
    edited_chart = dzi['chart']
    etype = edit['type']
    
    if etype == 'mark':
        edited_chart = edited_chart.mark(edit['mark'])
    elif etype == 'add_field':
        available_fields = dzi['available_fields']
        field = available_fields[edit['fieldtype']].pop(0)
        
        if (edit['fieldtype'] not in dzi['used_fields']):
            dzi['used_fields'][edit['fieldtype']] = []
        dzi['used_fields'][edit['fieldtype']].append(field)
        
        props = get_props_from_transform(edit['transform'])
        
        edited_chart = edited_chart.field(field, **props)
    elif etype == 'bin':
        used_fields = dzi['used_fields']
        
        if ('q' not in used_fields):
            return None
        
        field_to_bin = used_fields['q'][0]
        
        edited_chart = edited_chart.field(field_to_bin, bin=True)
    elif etype == 'agg':
        used_fields = dzi['used_fields']
        
        if ('q' not in used_fields):
            return None
        
        field_to_agg = used_fields['q'][0]
        edited_chart = edited_chart.field(field_to_agg, aggregate=edit['agg'])
        
    cold = edited_chart
    anchored = edited_chart.anchor_on(dzi['chart'])
    
    return {
        'prior': dzi['chart'],
        'prior_query': dzi['query'],
        'edit': edit,
        'cold': cold,
        'anchored': anchored,
        'available_fields': dzi['available_fields'],
        'used_fields': dzi['used_fields']
    }


# In[17]:


nexts = []
for chart in charts:
    for edit in edits:
        prior = deepcopy(chart)
        edited = edit_dziban(prior, edit)
        if edited is not None:
            nexts.append(edited)


# In[ ]:


with_differences = []
for i in tqdm(range(len(nexts))):
    n = nexts[i]
    cold = n['cold']
    anchored = n['anchored']
    
    if not cold.is_satisfiable():
        continue
        
    if not anchored.is_satisfiable():
        print(n['prior']._get_vegalite())
        print(n['edit'])
        print('\n'.join(n['anchored']._get_full_query()))
        print(n['cold']._get_asp_complete())
        break
        
    cold_graphscape = set(n['cold'] - n['prior'])
    anchored_graphscape = set(n['anchored']._get_graphscape_list())
    
    left_diff = cold_graphscape - anchored_graphscape
    right_diff = anchored_graphscape - cold_graphscape
    
    n['left_diff'] = left_diff
    n['right_diff'] = right_diff
    
    n['cold_draco_rank'] = cold._get_draco_rank()
    n['cold_graphscape_rank'] = cold._get_graphscape_rank(n['prior'])
    
    n['anchored_draco_rank'] = anchored._get_draco_rank()
    n['anchored_draco_rank'] = anchored._get_graphscape_rank()

    


# In[ ]:


def stringify_query(query):
    result = ''
    for i, field in enumerate(query):
        if (i > 0):
            result += ' x '
    
        fieldtype = field['fieldtype']
        transform = field['transform']
        
        if fieldtype == 'n':
            result += 'n'
        elif fieldtype == 'q':
            if transform == 'raw':
                result += 'q'
            else:  
                result += '{0}({1})'.format(field['transform'], field['fieldtype'])
        
    return result


# In[ ]:


def stringify_edit(prior, edit):
    etype = edit['type']
    
    if etype == 'mark':
        return '{0} <> {1}'.format(prior._get_vegalite()['mark'], edit['mark'])
    elif etype == 'add_field':
        return '+ {0}({1})'.format(edit['transform'], edit['fieldtype'])
    elif etype == 'bin':
        return '<- bin(q)'
    elif etype == 'agg':
        return '<- agg(q)'


# In[ ]:


data = []
for i in tqdm(range(len(nexts))):
    n = nexts[i]
    prior_query = stringify_query(n['prior_query'])
    edit = stringify_edit(n['prior'], n['edit'])
    
    left_diff = None
    if ('left_diff' in n):
        left_diff = json.dumps([x[0][5:] for x in n['left_diff']])
        right_diff = json.dumps([x[0][5:] for x in n['right_diff']])
    
    data.append({
        'prior_query': prior_query,
        'edit': edit,
        'left_diff': left_diff,
        'right_diff': right_diff
    })


# In[ ]:


df = pd.DataFrame(data, columns=['prior_query', 'edit', 'left_diff', 'right_diff'])
df.head(len(df))


# In[ ]:




