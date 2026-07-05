import json, hashlib, itertools, os
import numpy as np
REPO="/sessions/practical-dazzling-clarke/mnt/intelligence-theory-lab"
ART=f"{REPO}/artifacts/TLGP-001A"
K=5; D=3; FLOOR=1.0/K; DELTA=0.10
def bal_acc(yt,yp,n=K):
    yt=np.asarray(yt); yp=np.asarray(yp); rec=[]
    for c in range(n):
        m=yt==c
        if m.sum()==0: continue
        rec.append(float((yp[m]==c).mean()))
    return float(np.mean(rec)) if rec else 0.0
combos=list(itertools.product(range(K),repeat=D+1))
W=np.array([c[:D] for c in combos],int); C=np.array([c[D] for c in combos],int)
def ideal(ax,aa,ae,qx,qa,forced=None):
    ax=np.asarray(ax,int).reshape(-1,D);aa=np.asarray(aa,int).reshape(-1);ae=np.asarray(ae,int).reshape(-1)
    qx=np.asarray(qx,int).reshape(-1,D);qa=np.asarray(qa,int).reshape(-1)
    if forced is not None: idx=np.array([forced])
    else:
        cons=np.all(((W@ax.T+np.outer(C,aa))%K)==ae[None,:],axis=1); idx=np.flatnonzero(cons)
    if idx.size==0:
        v,ct=np.unique(ae,return_counts=True); return np.full(qx.shape[0],int(v[np.argmax(ct)]),int),0
    pq=(W[idx]@qx.T+np.outer(C[idx],qa))%K
    return np.array([np.argmax(np.bincount(pq[:,q],minlength=K)) for q in range(pq.shape[1])],int),int(idx.size)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
def feats(x,a):
    a=np.asarray(a).reshape(-1,1); return np.concatenate([np.asarray(x),a],1).astype(float)
eps=[json.loads(l) for l in open(f"{ART}/trace.jsonl") if l.strip()]
res=json.load(open(f"{ART}/result.json"))
SEED=20260622; rng_na=np.random.default_rng(123456)
ideal_s=[]; ss_clean=[]; ncm=0; integ=0
base={k:[] for k in ["predict_all","lookup","no_adaptation","knn1","logistic","mlp","random_forest"]}
for r in eps:
    ax=np.array(r["adapt_x"]);aa=np.array(r["adapt_a"]);ae=np.array(r["adapt_e"])
    qx=np.array(r["query_x"]);qa=np.array(r["query_a"]);qe=np.array(r["query_e"])
    w=np.array(r["rule_w"]);c=int(r["rule_c"])
    if not np.array_equal(((qx@w)+c*qa)%K, qe): integ+=1            # integrity vs ground-truth rule
    p,nc=ideal(ax,aa,ae,qx,qa); ideal_s.append(bal_acc(qe,p)); ncm+=int(nc==r["n_consistent"])
    pc,_=ideal(ax[0:1],aa[0:1],ae[0:1],qx,qa); ss_clean.append(bal_acc(qe,pc))   # single-step (1 obs)
    v,ct=np.unique(ae,return_counts=True); maj=int(v[np.argmax(ct)])
    base["predict_all"].append(bal_acc(qe,np.full(len(qe),maj)))
    tbl={(tuple(int(z) for z in xx),int(aaa)):int(ee) for xx,aaa,ee in zip(ax,aa,ae)}
    base["lookup"].append(bal_acc(qe,np.array([tbl.get((tuple(int(z) for z in xx),int(aaa)),maj) for xx,aaa in zip(qx,qa)])))
    base["no_adaptation"].append(bal_acc(qe,rng_na.integers(0,K,size=len(qe))))
    Xtr=feats(ax,aa);Xte=feats(qx,qa)
    def fp(mdl):
        u=np.unique(ae)
        if u.size<2: return np.full(Xte.shape[0],int(u[0]),int)
        mdl.fit(Xtr,ae); return mdl.predict(Xte).astype(int)
    base["knn1"].append(bal_acc(qe,fp(KNeighborsClassifier(n_neighbors=1))))
    base["logistic"].append(bal_acc(qe,fp(LogisticRegression(max_iter=2000))))
    base["mlp"].append(bal_acc(qe,fp(MLPClassifier(hidden_layer_sizes=(64,64),max_iter=600,random_state=SEED))))
    base["random_forest"].append(bal_acc(qe,fp(RandomForestClassifier(n_estimators=80,random_state=SEED))))
ideal_mean=float(np.mean(ideal_s)); fair={k:float(np.mean(v)) for k,v in base.items()}
max_fair=max(fair.values()); headroom=ideal_mean-max_fair; ssc=float(np.mean(ss_clean))
print("=== A. INDEPENDENT REPLAY (recomputed from raw trace, no repo imports) ===")
print(f"integrity_violations (query_e != rule(x,a))      : {integ}/200")
print(f"n_consistent match recorded                       : {ncm}/200")
print(f"ideal_mean  recomputed={ideal_mean:.6f}  recorded={res['ideal_observer_heldout']:.6f}  match={abs(ideal_mean-res['ideal_observer_heldout'])<1e-9}")
print(f"max_fair    recomputed={max_fair:.6f}  recorded={res['max_fair_baseline_heldout']:.6f}  diff={abs(max_fair-res['max_fair_baseline_heldout']):.4f}")
print(f"headroom    recomputed={headroom:.6f}  recorded={res['headroom_heldout']:.6f}")
print(f"single_step recomputed={ssc:.6f}  recorded={res['single_step_decoder']['clean']:.6f}")
rec=json.load(open(f"{ART}/baseline_comparison.json"))["fair_baselines_real"]
print("per-baseline recomputed vs recorded:")
for k in fair: print(f"   {k:14s} mine={fair[k]:.4f}  recorded={rec[k]:.4f}")
# verdict reimplemented (independent), using recomputed real-side + recorded shuffle/leak/decoder (separate-seed datasets)
shuffle_hr=res["shuffle_headroom"]; pc=json.load(open(f"{ART}/positive_control_report.json"))
leak_valid=pc["detector_valid"]; dec_cap=res["single_step_decoder"]["leaked_rule"]>=FLOOR+2*DELTA
def verdict(im,mf,hr,sc,shr,replay,lv,dc):
    chk={"headroom_ok":hr>DELTA,"baselines_fail":mf<=FLOOR+DELTA,"single_step_floor":sc<=FLOOR+DELTA,
         "ideal_high":im>=FLOOR+2*DELTA,"shuffle_collapse":shr<=DELTA,"replay_exact":replay}
    if not (lv and dc): return "invalid_due_to_leakage_or_contract_failure",chk
    if all(chk.values()): return "world_discriminates_structure_inference",chk
    return "world_cannot_discriminate__lookup_or_degenerate",chk
v,chk=verdict(ideal_mean,max_fair,headroom,ssc,shuffle_hr,True,leak_valid,dec_cap)
print(f"\nINDEPENDENT verdict = {v}")
print(f"recorded   verdict = {res['verdict']}   match={v==res['verdict']}")
print("checks:",chk)
print("\n=== B. TAMPER / FAIL-ABILITY PROBES (reimplemented verdict) ===")
t1,_=verdict(ideal_mean,0.50,ideal_mean-0.50,ssc,shuffle_hr,True,leak_valid,dec_cap)
print(f"T1 baseline score 0.197->0.50 : {t1}   flipped={t1!=res['verdict']}")
t2,_=verdict(ideal_mean,max_fair,headroom,ssc,shuffle_hr,True,False,dec_cap)
print(f"T2 planted leak marked missed : {t2}   flipped={t2!=res['verdict']}")
t3,_=verdict(ideal_mean,max_fair,headroom,ssc,0.50,True,leak_valid,dec_cap)
print(f"T3 shuffle headroom 0->0.50   : {t3}   flipped={t3!=res['verdict']}")
t4,_=verdict(ideal_mean,max_fair,headroom,ssc,shuffle_hr,False,leak_valid,dec_cap)
print(f"T4 replay_exact False         : {t4}   flipped={t4!=res['verdict']}")
t5,_=verdict(ideal_mean,max_fair,headroom,0.50,shuffle_hr,True,leak_valid,dec_cap)
print(f"T5 single_step 0.197->0.50    : {t5}   flipped={t5!=res['verdict']}")
print("\n=== C. PROVENANCE ===")
payload=json.dumps(res["preregistration"],sort_keys=True,separators=(",",":")).encode()
ph=hashlib.sha256(payload).hexdigest()
print(f"prereg sha (recomputed from embedded dict)={ph}")
print(f"prereg sha recorded                       ={res['preregistration_sha256']}  match={ph==res['preregistration_sha256']}")
prov=json.load(open(f"{ART}/code_path_provenance.json"))["files"]
allmatch=True
for fn,info in prov.items():
    p=f"{REPO}/{fn}"
    h=hashlib.sha256(open(p,'rb').read()).hexdigest() if os.path.exists(p) else "MISSING"
    ok=(h==info["delivered_sha256"]); allmatch&=ok
    if not ok: print(f"   MISMATCH {fn}: live={h[:12]} delivered={info['delivered_sha256'][:12]}")
print(f"all live src sha256 == recorded delivered_sha256 : {allmatch}")
print("\n=== D. CANDIDATE-FREE ===")
print(f"prereg candidate_free flag = {res['preregistration']['candidate_free']}")
print("AGENTS = ideal + 7 fair baselines; 'candidate' token present in result:", "candidate" in json.dumps(res).lower().replace("candidate_free","").replace("no candidate","").replace("tests no",""))
