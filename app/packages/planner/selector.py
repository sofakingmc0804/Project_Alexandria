#!/usr/bin/env python3
import json, yaml
from pathlib import Path
from typing import List, Dict, Any

def load_outline(jdir):
    with open(Path(jdir)/'outline.yaml') as f: return yaml.safe_load(f)

def load_segments(jdir):
    with open(Path(jdir)/'segments.json') as f: return json.load(f).get('segments',[])

def load_graph(jdir):
    with open(Path(jdir)/'graph.json') as f: return json.load(f)

def select_segments(jdir):
    jpath = Path(jdir)
    outline = load_outline(jdir)
    segments = load_segments(jdir)
    graph = load_graph(jdir)
    
    seg_map = {s['id']:s for s in segments}
    duplicates = set()
    for dup in graph.get('duplicates',[]):
        duplicates.add(dup['segment2_id'])
    
    selection = []
    used = set()
    
    for ch in outline.get('chapters',[]):
        ch_sel = {'chapter_id':ch['chapter_id'],'title':ch['title'],'segments':[]}
        for sid in ch['segment_ids']:
            if sid not in used and sid not in duplicates and sid in seg_map:
                ch_sel['segments'].append(seg_map[sid])
                used.add(sid)
        selection.append(ch_sel)
    
    result = {'job_id':jpath.name,'selection':selection,'num_selected':len(used),'num_duplicates_skipped':len(duplicates)}
    with open(jpath/'selection.json','w') as f: json.dump(result,f,indent=2)
    print(f' Selected {len(used)} segments across {len(selection)} chapters')
    return result

if __name__=='__main__':
    import sys
    select_segments(sys.argv[1] if len(sys.argv)>1 else 'tests/fixtures/phase2_test')
