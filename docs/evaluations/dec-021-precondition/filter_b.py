import json,sys
KT={'requirement','evidence','claim','decision','authority'}
KR={'implemented_by','observed_on','depends_on','supports','supersedes'}
out=[]
for l in open(sys.argv[1]):
    if not l.strip() or l.startswith('//'): continue
    r=json.loads(l)
    if r['type'] not in KT: continue
    if 'relations' in r: r['relations']=[x for x in r['relations'] if x['rel'] in KR]
    out.append(json.dumps(r))
open(sys.argv[2],'w').write('\n'.join(out)+'\n')
