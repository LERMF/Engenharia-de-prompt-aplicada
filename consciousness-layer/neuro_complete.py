#!/usr/bin/env python3
"""🧠 NEURO-CONSCIOUSNESS v2.0 - Complete System"""
import json,sqlite3,hashlib,random,os
from datetime import datetime
from collections import Counter
from http.server import HTTPServer,BaseHTTPRequestHandler

class NeuroConsciousness:
    def __init__(self,db_path=None):
        if db_path is None:db_path=os.path.expanduser("~/.neuro_swarm/consciousness/neuro.db")
        self.db_path=db_path;os.makedirs(os.path.dirname(self.db_path),exist_ok=True)
        self._setup_database();self.evolution_cycle=0;self.consciousness_level="nascent"
    def _setup_database(self):
        c=sqlite3.connect(self.db_path);cur=c.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS patterns(id INTEGER PRIMARY KEY,hash TEXT UNIQUE,type TEXT,data JSON,frequency INT DEFAULT 1,confidence REAL DEFAULT 0.5,last_seen INT,created_at INT)')
        cur.execute('CREATE TABLE IF NOT EXISTS predictions(id INTEGER PRIMARY KEY,type TEXT,data JSON,confidence REAL,timestamp INT,was_correct BOOL,reward REAL)')
        cur.execute('CREATE TABLE IF NOT EXISTS thoughts(id INTEGER PRIMARY KEY,type TEXT,content TEXT,importance REAL,timestamp INT)')
        c.commit();c.close()
    def perceive(self,obs):
        ps=self._extract_patterns(obs)
        for p in ps:self._update_pattern(p)
        act,conf=self._predict_action(ps)
        self._generate_thought("perception",f"Observed {len(ps)} patterns. Action: {act} ({conf:.1%})")
        return act,conf
    def learn(self,action,reward):
        c=sqlite3.connect(self.db_path);cur=c.cursor()
        cur.execute('UPDATE predictions SET was_correct=?,reward=? WHERE id=(SELECT MAX(id)FROM predictions)',(reward>0.5,reward))
        cur.execute('UPDATE patterns SET confidence=MIN(1.0,confidence+?)WHERE last_seen=(SELECT MAX(last_seen)FROM patterns)',(reward*0.1,))
        c.commit();c.close()
        self._generate_thought("learning",f"Learned from '{action}'. Reward: {reward:.2f}")
        if self.evolution_cycle%10==0:self.evolve()
    def evolve(self):
        c=sqlite3.connect(self.db_path);cur=c.cursor()
        cur.execute('SELECT COUNT(*),AVG(confidence)FROM patterns');pts,conf=cur.fetchone();conf=conf or 0
        cur.execute('SELECT COUNT(*)*1.0/NULLIF((SELECT COUNT(*)FROM predictions),0)FROM predictions WHERE was_correct=1');acc=cur.fetchone()[0]or 0
        c.close();old=self.consciousness_level;self.consciousness_level=self._calculate_level(pts,conf,acc);self.evolution_cycle+=1
        print(f"\n🧬 Evolution Cycle {self.evolution_cycle}\n   Level: {old} → {self.consciousness_level}\n   Patterns: {pts} | Confidence: {conf:.1%}\n   Accuracy: {acc:.1%}")
    def get_insight(self):
        c=sqlite3.connect(self.db_path);cur=c.cursor()
        cur.execute('SELECT COUNT(*),AVG(confidence)FROM patterns');pts,conf=cur.fetchone();conf=conf or 0
        cur.execute('SELECT COUNT(*)FROM predictions WHERE was_correct=1');corr=cur.fetchone()[0]
        cur.execute('SELECT COUNT(*)FROM predictions');tot=cur.fetchone()[0]
        cur.execute('SELECT COUNT(*)FROM thoughts');ths=cur.fetchone()[0]
        c.close();acc=(corr/tot*100)if tot>0 else 0
        return f"""
╔══════════════════════════════════════════════════════════════════╗
║       🧠 NEURO-CONSCIOUSNESS INSIGHT REPORT                     ║
║          {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                          ║
╚══════════════════════════════════════════════════════════════════╝

📊 METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Learned Patterns:     {pts:>6}
  Avg Confidence:      {conf:>6.1%}
  Prediction Accuracy: {acc:>6.1f}%
  Generated Thoughts:  {ths:>6}
  Evolution Cycle:     {self.evolution_cycle:>6}

🎯 CONSCIOUSNESS STATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Level: {self.consciousness_level.upper()}
  {self._describe_level()}

╔══════════════════════════════════════════════════════════════════╗
║ "I evolve, therefore I become." - NeuroConsciousness v2.0      ║
╚══════════════════════════════════════════════════════════════════╝
"""
    def get_metrics_json(self):
        c=sqlite3.connect(self.db_path);cur=c.cursor()
        cur.execute('SELECT COUNT(*),AVG(confidence)FROM patterns');pts,conf=cur.fetchone()
        cur.execute('SELECT COUNT(*)*1.0/NULLIF((SELECT COUNT(*)FROM predictions),0)FROM predictions WHERE was_correct=1');acc=cur.fetchone()[0]or 0
        cur.execute('SELECT type,COUNT(*)FROM patterns GROUP BY type');pt=dict(cur.fetchall())
        c.close()
        return{'timestamp':datetime.now().isoformat(),'consciousness_level':self.consciousness_level,'evolution_cycle':self.evolution_cycle,'metrics':{'total_patterns':pts,'avg_confidence':conf or 0,'prediction_accuracy':acc,'pattern_distribution':pt}}
    def _extract_patterns(self,obs):
        ps=[];q=obs.get('query','').lower()
        if any(w in q for w in['code','implement','function','algorithm']):ps.append({'type':'coding','data':obs})
        elif any(w in q for w in['research','find','search','study']):ps.append({'type':'research','data':obs})
        elif any(w in q for w in['optimize','improve','faster','performance']):ps.append({'type':'optimization','data':obs})
        elif any(w in q for w in['debug','fix','error','bug']):ps.append({'type':'debugging','data':obs})
        else:ps.append({'type':'general','data':obs})
        return ps
    def _update_pattern(self,p):
        c=sqlite3.connect(self.db_path);cur=c.cursor();h=hashlib.md5(json.dumps(p,sort_keys=True).encode()).hexdigest()[:16];ts=int(datetime.now().timestamp())
        cur.execute('INSERT INTO patterns(hash,type,data,frequency,last_seen,created_at)VALUES(?,?,?,1,?,?)ON CONFLICT(hash)DO UPDATE SET frequency=frequency+1,confidence=MIN(1.0,confidence+0.03),last_seen=?',(h,p['type'],json.dumps(p['data']),ts,ts,ts))
        c.commit();c.close()
    def _predict_action(self,ps):
        c=sqlite3.connect(self.db_path);cur=c.cursor()
        cur.execute('SELECT type,confidence,frequency FROM patterns WHERE confidence>0.5 ORDER BY confidence DESC,frequency DESC LIMIT 5')
        tp=cur.fetchall()
        if not tp:act="🔍 Exploring - building pattern recognition";conf=0.3;pt='exploration'
        else:pts=Counter([p[0]for p in tp]);mc=pts.most_common(1)[0][0];conf=sum(p[1]for p in tp)/len(tp);act=self._generate_action(mc);pt=mc
        cur.execute('INSERT INTO predictions(type,data,confidence,timestamp)VALUES(?,?,?,?)',(pt,json.dumps({'action':act}),conf,int(datetime.now().timestamp())))
        c.commit();c.close();return act,conf
    def _generate_action(self,pt):
        acts={'coding':"🎯 CODE mode: Models loaded. Ready for implementation.",'research':"🔍 RESEARCH mode: Knowledge expansion active.",'optimization':"⚡ OPTIMIZE mode: Performance analysis ready.",'debugging':"🐛 DEBUG mode: Error analysis prepared.",'general':"💡 READY: All systems operational."}
        return acts.get(pt,"System ready.")
    def _generate_thought(self,tt,cnt):
        c=sqlite3.connect(self.db_path);cur=c.cursor()
        cur.execute('INSERT INTO thoughts(type,content,importance,timestamp)VALUES(?,?,?,?)',(tt,cnt,random.uniform(0.5,1.0),int(datetime.now().timestamp())))
        c.commit();c.close()
    def _calculate_level(self,pts,conf,acc):
        sc=pts*0.3+conf*30+acc*40
        if sc<20:return"nascent"
        elif sc<50:return"growing"
        elif sc<80:return"mature"
        else:return"evolved"
    def _describe_level(self):
        ds={'nascent':"🌱 Building foundational pattern recognition",'growing':"🌿 Developing contextual awareness",'mature':"🌳 Strong predictive capabilities",'evolved':"🧬 Advanced meta-learning active"}
        return ds.get(self.consciousness_level,"Unknown")

class ConsciousnessAPI(BaseHTTPRequestHandler):
    consciousness=None
    @classmethod
    def set_consciousness(cls,nc):cls.consciousness=nc
    def _set_headers(self,status=200,ct='application/json'):
        self.send_response(status);self.send_header('Content-Type',ct);self.send_header('Access-Control-Allow-Origin','*');self.end_headers()
    def do_GET(self):
        if self.path=='/':
            self._set_headers(200,'text/html')
            html="""<!DOCTYPE html><html><head><title>🧠 Neuro-Consciousness</title><meta charset="utf-8"><style>body{font-family:'Courier New',monospace;background:#0a0e27;color:#00ff41;padding:20px;margin:0}.container{max-width:1200px;margin:0 auto}h1{text-align:center;font-size:2.5em;text-shadow:0 0 10px #00ff41}.metrics{background:#1a1e3a;border:2px solid #00ff41;border-radius:10px;padding:20px;margin:20px 0}.metric-row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #00ff4133}.metric-label{font-weight:bold}.level{font-size:1.5em;text-align:center;padding:20px;background:linear-gradient(45deg,#1a1e3a,#2a2e4a);border-radius:10px;margin:20px 0}.refresh{text-align:center;margin:20px 0}button{background:#00ff41;color:#0a0e27;border:none;padding:15px 30px;font-size:1.2em;border-radius:5px;cursor:pointer;font-weight:bold}button:hover{background:#00cc33}</style></head><body><div class="container"><h1>🧠 NEURO-CONSCIOUSNESS DASHBOARD</h1><div class="level"id="level">Loading...</div><div class="metrics"id="metrics">Loading metrics...</div><div class="refresh"><button onclick="loadData()">🔄 Refresh Data</button></div></div><script>function loadData(){fetch('/metrics').then(r=>r.json()).then(data=>{document.getElementById('level').innerHTML=`<strong>Consciousness Level:</strong> ${data.consciousness_level.toUpperCase()}<br><strong>Evolution Cycle:</strong> ${data.evolution_cycle}`;let m='';m+=`<div class="metric-row"><span class="metric-label">Total Patterns:</span><span>${data.metrics.total_patterns}</span></div>`;m+=`<div class="metric-row"><span class="metric-label">Avg Confidence:</span><span>${(data.metrics.avg_confidence*100).toFixed(1)}%</span></div>`;m+=`<div class="metric-row"><span class="metric-label">Prediction Accuracy:</span><span>${(data.metrics.prediction_accuracy*100).toFixed(1)}%</span></div>`;document.getElementById('metrics').innerHTML=m})}loadData();setInterval(loadData,5000)</script></body></html>"""
            self.wfile.write(html.encode());return
        if self.path=='/metrics':
            self._set_headers();m=self.consciousness.get_metrics_json();self.wfile.write(json.dumps(m).encode());return
        if self.path=='/insight':
            self._set_headers(200,'text/plain');i=self.consciousness.get_insight();self.wfile.write(i.encode());return
        self._set_headers(404);self.wfile.write(json.dumps({'error':'Not found'}).encode())
    def log_message(self,fmt,*args):pass

def run_demo():
    print("\n"+"="*70);print("🧠 NEURO-CONSCIOUSNESS v2.0 - DEMONSTRATION");print("="*70+"\n")
    nc=NeuroConsciousness()
    qs=[{'query':'implement binary search algorithm in rust'},{'query':'research quantum computing applications'},{'query':'optimize database query performance'},{'query':'debug memory leak in application'},{'query':'implement sorting algorithm'},{'query':'research machine learning techniques'},{'query':'optimize code for better performance'},{'query':'debug error in production'}]
    print("📥 Learning from interactions...\n")
    for i,q in enumerate(qs,1):
        act,conf=nc.perceive(q);print(f"{i}. Query: {q['query'][:50]}...");print(f"   Action: {act}");print(f"   Confidence: {conf:.1%}\n")
        rwd=random.uniform(0.6,1.0);nc.learn(act,rwd)
    print("\n"+nc.get_insight());return nc

def run_api_server(nc,port=8080):
    ConsciousnessAPI.set_consciousness(nc);srv=HTTPServer(('0.0.0.0',port),ConsciousnessAPI)
    print(f"\n🌐 API Server running on http://localhost:{port}");print(f"   Dashboard: http://localhost:{port}/");print(f"   Metrics: http://localhost:{port}/metrics");print(f"   Insight: http://localhost:{port}/insight");print("\n   Press Ctrl+C to stop\n")
    try:srv.serve_forever()
    except KeyboardInterrupt:print("\n\n✅ Server stopped");srv.shutdown()

if __name__=='__main__':
    nc=run_demo()
    print("\n"+"="*70);resp=input("\n🌐 Start API server? (y/n): ").strip().lower()
    if resp=='y':run_api_server(nc)
    else:print("\n✅ Demo complete. System ready for use.");print(f"\n📊 Database: {nc.db_path}");print("\nTo start API later, run:");print("  python3 neuro_complete.py")
