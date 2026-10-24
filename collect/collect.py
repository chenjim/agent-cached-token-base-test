import argparse, json, sqlite3, glob, os, time

def load_prices(model='deepseek-v4.1-flash'):
    try:
        d=json.load(open(os.path.expanduser('~/.pi/agent/models-store.json')))
        m=[x for x in d['opencode-go']['models'] if x['id']==model][0]
        c=m['cost']
        return {'input':c.get('input',0),'output':c.get('output',0),'cacheRead':c.get('cacheRead',0),'cacheWrite':c.get('cacheWrite',0)}
    except Exception:
        return {'input':0,'output':0,'cacheRead':0,'cacheWrite':0}

PRICES=load_prices()

def est_cost(inp,out,rs,cr,cw):
    return (inp*PRICES['input']+(out+rs)*PRICES['output']+cr*PRICES['cacheRead']+cw*PRICES['cacheWrite'])/1e6

def collect_opencode(project, since):
    db=os.path.expanduser("~/.local/share/opencode/opencode.db")
    con=sqlite3.connect(db)
    rows=con.execute("""
      SELECT id,directory,time_created,tokens_input,tokens_output,tokens_reasoning,
             tokens_cache_read,tokens_cache_write,cost
      FROM session
      WHERE directory=? AND time_created>=?
      ORDER BY time_created DESC
    """,(project,since*1000)).fetchall()
    con.close()
    return [{"client":"opencode","session_id":r[0],"dir":r[1],"ts":r[2],
             "input":r[3],"output":r[4],"reasoning":r[5],
             "cache_read":r[6],"cache_write":r[7],"cost":r[8],
             "estimated_cost":est_cost(r[3],r[4],r[5],r[6],r[7])} for r in rows]

def collect_hermes(project, since):
    db=os.path.expanduser("~/.hermes/state.db")
    con=sqlite3.connect(db)
    rows=con.execute("""
      SELECT s.id,s.started_at,smu.model,smu.api_call_count,smu.input_tokens,smu.output_tokens,
             smu.reasoning_tokens,smu.cache_read_tokens,smu.cache_write_tokens,smu.actual_cost_usd
      FROM sessions s
      LEFT JOIN session_model_usage smu ON smu.session_id=s.id
      WHERE s.cwd=? AND s.started_at>=?
      ORDER BY s.started_at DESC
    """,(project,since)).fetchall()
    con.close()
    return [{"client":"hermes","session_id":r[0],"ts":r[1],"model":r[2],
             "api_calls":r[3],"input":r[4],"output":r[5],"reasoning":r[6],
             "cache_read":r[7],"cache_write":r[8],"cost":r[9],
             "estimated_cost":est_cost(r[4],r[5],r[6],r[7],r[8])} for r in rows]

def collect_pi(session_dir, since):
    out=[]
    for f in glob.glob(os.path.join(session_dir,"**","*.jsonl"),recursive=True):
        if os.path.getmtime(f) < since: continue
        inp=outt=cr=cw=rs=0; calls=0
        for line in open(f):
            try: m=json.loads(line)
            except: continue
            u=m.get("message",{}).get("usage")
            if u:
                calls+=1
                inp+=u.get("input",0); outt+=u.get("output",0)
                cr+=u.get("cacheRead",0); cw+=u.get("cacheWrite",0)
                rs+=u.get("reasoning",0)
        out.append({"client":"pi","file":f,"api_calls":calls,
                    "input":inp,"output":outt,"reasoning":rs,
                    "cache_read":cr,"cache_write":cw,
                    "estimated_cost":est_cost(inp,outt,rs,cr,cw)})
    return out

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--client",choices=["opencode","hermes","pi","all"],default="all")
    ap.add_argument("--project",required=True,help="absolute project path")
    ap.add_argument("--since",type=float,default=time.time()-3600,help="epoch seconds")
    ap.add_argument("--pi-session-dir",default=None)
    args=ap.parse_args()
    res={}
    if args.client in ("opencode","all"):
        res["opencode"]=collect_opencode(args.project,args.since)
    if args.client in ("hermes","all"):
        res["hermes"]=collect_hermes(args.project,args.since)
    if args.client in ("pi","all"):
        sd=args.pi_session_dir or "/vol1/1000/Project/agent-cached-token-base-test/results/pi-sessions"
        res["pi"]=collect_pi(sd,args.since)
    print(json.dumps(res,indent=2,ensure_ascii=False))
