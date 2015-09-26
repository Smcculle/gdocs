import ast
import traceback

def insert(old, new, i):
    #in log, index starts at 1
    i = i - 1
    return old[:i] + new + old[i:]

def delete(old, si, ei):
    #in log, index starts at 1
    si = si - 1
    return old[:si] + old[ei:]

def write(s):
    with open('pt.txt', 'w') as f:
        f.write(s)

with open('output/454_456_out.txt', 'r') as f:
    log = f.read().split('\n')
#s.decode('string_escape')
#p = re.compile(r'\\u00\w\w')  for intermixed unicode marks

plain_text = ''
logdict = ast.literal_eval(log[log.index('chunkedSnapshot') + 1])
cs_string = logdict['string']
cs_string = cs_string.decode('unicode-escape')    
plain_text += cs_string
cl_index = log.index('changelog') + 1

for line in log[cl_index:]:    
    try:
        si = line.index('{')
        actiondict = ast.literal_eval(line[si:])
    
        if actiondict['type'] == 'is':
            i = actiondict['insert_before_index']
            s = actiondict['string']
            print i,s
            plain_text = insert(plain_text, s, i)
            
        elif actiondict['type'] == 'ds':
            print 'not happening'
            si = actiondict['starting_index']
            ei = actiondict['ending_index']
            plain_text = delete(plain_text, si, ei)
    except:
        pass #get rid of last empty line
    
write(plain_text)
