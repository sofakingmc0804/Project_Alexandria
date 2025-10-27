#!/usr/bin/env python3
import json, yaml
from pathlib import Path
from typing import List, Dict, Any

def load_config(p):
    with open(p, encoding='utf-8-sig') as f: return yaml.safe_load(f)

def load_segments(j):
    with open(Path(j)/'segments.json') as f: return json.load(f).get('segments',[])

def est_dur(s): return (s['end_ms']-s['start_ms'])/60000

def create_chapters(segs, target, mode='full'):
    if not segs:
        return [], target

    # Apply length mode to determine actual target duration
    mode_multipliers = {
        'full': 1.0,        # 60 min (100%)
        'condensed': 0.33,  # 20 min (33%)
        'topic_focus': 0.17 # 10 min (17%)
    }
    multiplier = mode_multipliers.get(mode, 1.0)
    actual_target = target * multiplier

    # Sort segments by relevance/importance if not in full mode
    # For condensed/topic_focus, prioritize segments with more text content
    if mode != 'full':
        segs = sorted(segs, key=lambda s: len(s.get('text', '')), reverse=True)

    # Select segments to meet target duration
    selected, accum = [], 0.0
    for s in segs:
        dur = est_dur(s)
        if accum + dur <= actual_target * 1.1:  # Allow 10% overage
            selected.append(s)
            accum += dur
        if accum >= actual_target * 0.9:  # Stop when we hit 90% of target
            break

    if not selected:
        selected = segs[:1]  # Always include at least one segment

    # Create chapters from selected segments
    total = sum(est_dur(s) for s in selected)
    n = 1 if total<8 else max(1,int(total/10))
    per = max(1,len(selected)//n)
    chs, idx = [], 0
    for i in range(n):
        end = len(selected) if i==n-1 else min(idx+per,len(selected))
        cseg = selected[idx:end]
        if not cseg: break
        txt = cseg[0]['text']
        chs.append({'chapter_id':f'ch{i+1:02d}','title':f'Chapter {i+1}','description':txt[:50]+'...' if len(txt)>50 else txt,'segment_ids':[s['id'] for s in cseg],'duration_minutes':round(sum(est_dur(s) for s in cseg),2),'order':i+1})
        idx=end
    return chs, actual_target

def validate_outline(chs, target):
    tot = sum(c['duration_minutes'] for c in chs)
    ok = target*0.9 <= tot <= target*1.1
    return {'passed':ok,'total_duration':round(tot,2),'target_duration':target,'num_chapters':len(chs)}

def generate_outline(jdir):
    jpath = Path(jdir)
    cfg = load_config('configs/output_menu.yaml')
    target, mode = cfg.get('target_duration_minutes',60), cfg.get('length_mode','full')
    segs = load_segments(jdir)
    if not segs:
        return {'job_id':jpath.name,'target_duration_minutes':target,'actual_target_minutes':target,'length_mode':mode,'chapters':[],'validation':{'passed':False,'total_duration':0,'target_duration':target,'num_chapters':0}}
    chs, actual_target = create_chapters(segs,target,mode)
    val = validate_outline(chs,actual_target)
    out = {'job_id':jpath.name,'target_duration_minutes':target,'actual_target_minutes':actual_target,'length_mode':mode,'chapters':chs,'validation':val}
    with open(jpath/'outline.yaml','w') as f: yaml.dump(out,f,default_flow_style=False,sort_keys=False)
    print(f' Created {len(chs)} chapters, {val["total_duration"]} min')
    return out

if __name__=='__main__':
    import sys
    generate_outline(sys.argv[1] if len(sys.argv)>1 else 'tests/fixtures/phase2_test')
