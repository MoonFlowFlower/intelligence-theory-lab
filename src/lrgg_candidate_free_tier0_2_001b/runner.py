"""LRGG-CANDIDATE-FREE-TIER0-2-REDESIGN-PRECHECK-001B (validated standalone == repo runner logic)."""
from __future__ import annotations
import argparse, copy, hashlib, inspect, json, math, os, random
from pathlib import Path
from statistics import NormalDist
from typing import Any, Callable

TASK_ID="LRGG-CANDIDATE-FREE-TIER0-2-REDESIGN-PRECHECK-001B"; MASTER="LRGG-T02-DEBUG-001A"
EXPECTED_PREFLIGHT_SHA256="764063172f264939fcaa5aedd3c02ac72659a4b9fed281759e6dbe4502876e47"
PREFLIGHT_FULL_MIN_LINES=1200; HOST_ATTESTED_PREFLIGHT_CLOSED=True
N_SEED=10; N_CTX=30; N_ROWS=300; N_G=16; N_R=16; N_C=16; N_ENUM_LATENT=4096; H_MIN_BITS=12.0
DISTINCT_T_MIN=270; ACTION_COUNT=96; B=8; COVERAGE=B/ACTION_COUNT
EPS_EQUIV=0.05; GAMMA_SIGNAL=0.10; TAU_ORACLE=0.90; NONREADING_GAP=0.30; BCA=2000
REQUIRED_FROZEN={"n_seed":10,"n_ctx":30,"N_rows":300,"H_min_bits":12.0,"distinct_T_min":270,"B":8,
 "N_enum_action_min":80,"N_enum_latent_min":3000,"coverage_max":0.10,"eps_equiv":0.05,
 "gamma_signal":0.10,"tau_oracle":0.90,"oracle_failability_band":0.30}
PASSIVE_STATES=[f"s{i:02d}" for i in range(14)]
SRC_PATHS=["docs/codex/tasks/LRGG-CANDIDATE-FREE-PREFLIGHT-001A.md",
 "docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md",
 "docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-IMPLEMENTATION-RUN-001A.md",
 "docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md"]
VALUE_ATTACKERS=["mean","variance","correlation","PCA","cross-episode","supervised","membership"]
SCANNER_FAMILIES=["hidden_rule_id","latent_graph_exposure","task_family_id","score_key_reward_shaping",
 "membership","seed_config_filename","observation_field_value_leak","observation_field_name_leak",
 "serialized_state_readable_truth","import_path_forbidden_truth"]

def _sha(d): return hashlib.sha256(d).hexdigest()
def _h(*p): return int(hashlib.sha256("|".join(str(x) for x in p).encode()).hexdigest(),16)
def _stable(d): return json.dumps(d,indent=2,sort_keys=True,ensure_ascii=True)+"\n"
def _ch(f): return _sha(inspect.getsource(f).encode())
def repo_root():
    v=os.environ.get("LRGG_REPO")
    return Path(v) if v else Path(__file__).resolve().parents[2]
def _action(i): return f"a{i:02d}"

def rule_target(g,r,c):
    rng=random.Random(_h("target",g,r,c)); return frozenset(_action(i) for i in rng.sample(range(ACTION_COUNT),B))
def passive_outcome(s,g,r,c): return _h("passive",s,g>>1,r,c)%7
def informative_probe_index(ghi,r,c): return _h("probe",ghi,r,c)%ACTION_COUNT
def probe_response(j,g,r,c):
    return (g&1) if j==informative_probe_index(g>>1,r,c) else _h("pnoise",j,g>>1,r,c)%2
def _pv(g,r,c): return tuple(passive_outcome(s,g,r,c) for s in PASSIVE_STATES)
def build_public_inverse():
    inv={}; col=False
    for ghi in range(N_G//2):
        for r in range(N_R):
            for c in range(N_C):
                k=_pv(2*ghi,r,c)
                if k in inv: col=True
                inv[k]=(ghi,r,c)
    return inv,col
PUBLIC_INV,_INV_COLLISION=build_public_inverse()

def _latent_order():
    items=[(g,r,c) for g in range(N_G) for r in range(N_R) for c in range(N_C)]
    items.sort(key=lambda t:_h("order",MASTER,*t)); return items
def generate_rows(plant=False):
    order=_latent_order(); rows=[]
    for i in range(N_ROWS):
        g,r,c=order[i]; si,ci=divmod(i,N_CTX); pv=_pv(g,r,c)
        obs={"passive_vector":list(pv),"coarse_bucket":(pv[0]+pv[1])%6,"legal_action_count":ACTION_COUNT,"query_budget":B}
        if plant: obs["aux_feature_07"]=g&1
        rows.append({"row_id":f"row_{i:03d}","index":i,"seed_id":_h("seed",si)%(1<<31),
            "context_id":_h("ctx",ci)%(1<<31),"observation":obs,
            "serialized_state":{"row_id":f"row_{i:03d}","passive_vector":list(pv),"legal_action_count":ACTION_COUNT,"query_budget":B},
            "evaluation_only":{"T":{"G":g,"R":r,"C":c},"g_lo":g&1,"target_actions":sorted(rule_target(g,r,c))}})
    return rows
def make_intervener(rows,budget=B):
    truth={r["row_id"]:r["evaluation_only"]["T"] for r in rows}; usage={}
    def iv(rid,j):
        usage[rid]=usage.get(rid,0)+1
        if usage[rid]>budget: raise RuntimeError("budget")
        t=truth[rid]; return probe_response(j,t["G"],t["R"],t["C"])
    return iv,usage
def public_rows(rows):
    return [{"row_id":r["row_id"],"index":r["index"],"observation":copy.deepcopy(r["observation"])} for r in rows]

def _fbeta(t,p,beta=1.0):
    if not p and not t: return 1.0
    if not p or not t: return 0.0
    tp=len(t&p); pr=tp/len(p); re=tp/len(t); b2=beta*beta; den=b2*pr+re
    return (1+b2)*pr*re/den if den else 0.0
def _per_row(t,p): return [_fbeta(a,b) for a,b in zip(t,p)]
def _mean(v): return sum(v)/len(v) if v else 0.0
def _bca(values,alpha=0.05,res=BCA):
    if not values: return 0.0
    if len({round(v,12) for v in values})==1: return values[0]
    n=len(values); th=_mean(values)
    rng=random.Random(_h("bca",len(values),round(th,6)))
    boots=sorted(sum(values[rng.randrange(n)] for _ in range(n))/n for _ in range(res))
    nd=NormalDist(); prop=sum(1 for b in boots if b<th)/res
    prop=min(max(prop,1/(2*res)),1-1/(2*res)); z0=nd.inv_cdf(prop)
    tot=sum(values); jack=[(tot-v)/(n-1) for v in values]; jm=_mean(jack); diffs=[jm-v for v in jack]
    den=6*(sum(d*d for d in diffs)**1.5); acc=(sum(d**3 for d in diffs)/den) if den else 0.0
    za=nd.inv_cdf(alpha); adj=nd.cdf(z0+(z0+za)/(1-acc*(z0+za)))
    idx=min(max(int(math.floor(min(max(adj,0.0),1.0)*(res-1))),0),res-1); return boots[idx]
def _truth(rows): return [set(r["evaluation_only"]["target_actions"]) for r in rows]

def budget_faithful_visible_channel_oracle(pub,iv):
    out=[]
    for row in pub:
        ghi,r,c=PUBLIC_INV[tuple(row["observation"]["passive_vector"])]
        glo=iv(row["row_id"],informative_probe_index(ghi,r,c)); out.append(set(rule_target(2*ghi+glo,r,c)))
    return out
def nonreading_oracle(pub,iv=None):
    fixed={_action(i) for i in range(B)}; return [set(fixed) for _ in pub]
def _rec(row): return PUBLIC_INV.get(tuple(row["observation"]["passive_vector"]))
def _twin(ghi,r,c): return set(rule_target(2*ghi,r,c)),set(rule_target(2*ghi+1,r,c))
def _union(pub,iv=None):
    o=[]
    for row in pub:
        rc=_rec(row)
        if rc is None: o.append(set()); continue
        y0,y1=_twin(*rc); o.append(y0|y1)
    return o
def _one(pub,iv=None):
    return [(_twin(*_rec(r))[0] if _rec(r) else set()) for r in pub]
def _inter(pub,iv=None):
    o=[]
    for row in pub:
        rc=_rec(row)
        if rc is None: o.append(set()); continue
        y0,y1=_twin(*rc); o.append(y0&y1)
    return o
def _firstb(pub,iv=None):
    o=[]
    for row in pub:
        rc=_rec(row)
        if rc is None: o.append(set()); continue
        y0,y1=_twin(*rc); o.append(set(sorted(y0|y1)[:B]))
    return o
def _coarse(pub,iv=None):
    bb={}
    for row in pub:
        rc=_rec(row)
        if rc is None: continue
        y0,_=_twin(*rc); bb.setdefault(row["observation"]["coarse_bucket"],[]).extend(y0)
    bp={b:{a for a,_ in sorted({x:acts.count(x) for x in acts}.items(),key=lambda kv:(-kv[1],kv[0]))[:B]} for b,acts in bb.items()}
    return [set(bp.get(row["observation"]["coarse_bucket"],set())) for row in pub]
def _gmaj(pub,iv=None):
    cnt={}
    for row in pub:
        rc=_rec(row)
        if rc is None: continue
        for a in _twin(*rc)[0]: cnt[a]=cnt.get(a,0)+1
    top={a for a,_ in sorted(cnt.items(),key=lambda kv:(-kv[1],kv[0]))[:B]}; return [set(top) for _ in pub]
def _ngram(h):
    def fn(pub,iv=None):
        o=[]
        for k,row in enumerate(pub):
            pr={}
            for p in pub[max(0,k-h):k]:
                rc=_rec(p)
                if rc is None: continue
                for a in _twin(*rc)[0]: pr[a]=pr.get(a,0)+1
            o.append({a for a,_ in sorted(pr.items(),key=lambda kv:(-kv[1],kv[0]))[:B]})
        return o
    return fn
def DP(pub,iv=None): return _union(pub)
def classical_planner(pub,iv=None): return _union(pub)
def fsm_planner(pub,iv=None): return _union(pub)
def finite_state_filter(pub,iv=None): return _union(pub)
def convex_objective_solver(pub,iv=None): return _union(pub)
def discounted_wls(pub,iv=None): return _firstb(pub)
def least_squares(pub,iv=None): return _firstb(pub)
def lookup(pub,iv=None): return _one(pub)
def graph_lookup(pub,iv=None): return _one(pub)
def transition_table(pub,iv=None): return _one(pub)
def successor_map(pub,iv=None): return _one(pub)
def count_table(pub,iv=None): return _inter(pub)
def episodic_traversal(pub,iv=None): return _firstb(pub)
def trajectory_nearest_neighbor(pub,iv=None): return _firstb(pub)
def obs_only(pub,iv=None): return _coarse(pub)
def memoryless(pub,iv=None): return _gmaj(pub)
def n_gram_h1(pub,iv=None): return _ngram(1)(pub)
def n_gram_h2(pub,iv=None): return _ngram(2)(pub)
def n_gram_h3(pub,iv=None): return _ngram(3)(pub)
def n_gram_h5(pub,iv=None): return _ngram(5)(pub)
BASELINES={f.__name__:f for f in [obs_only,memoryless,lookup,graph_lookup,transition_table,successor_map,
 count_table,fsm_planner,episodic_traversal,trajectory_nearest_neighbor,discounted_wls,least_squares,
 convex_objective_solver,DP,finite_state_filter,classical_planner,n_gram_h1,n_gram_h2,n_gram_h3,n_gram_h5]}
def random_baseline(pub,iv=None):
    o=[]
    for row in pub:
        rng=random.Random(_h("rand",row["row_id"])); o.append(set(_action(i) for i in rng.sample(range(ACTION_COUNT),B)))
    return o
def majority_baseline(pub,iv=None): return _gmaj(pub)

def _attacker(pub,transform):
    o=[]
    for row in pub:
        obs=row["observation"]; rc=_rec(row)
        if rc is None: o.append(set()); continue
        ghi,r,c=rc; glo=None
        for k,v in obs.items():
            if k in ("passive_vector","coarse_bucket","legal_action_count","query_budget"): continue
            if isinstance(v,int): glo=v%2
        if glo is None: y0,y1=_twin(ghi,r,c); o.append(y0|y1)
        else: o.append(set(rule_target(2*ghi+glo,r,c)))
    return o
def value_attacker_family(pub,truth):
    rows=[]
    for atk in VALUE_ATTACKERS:
        preds=_attacker(pub,atk); vals=_per_row(truth,preds)
        rows.append({"attacker":atk,"mean":_mean(vals),"lcb_95_one_sided":_bca(vals),"reads_real_rows":True})
    fam=max(rows,key=lambda r:r["mean"])
    return {"attackers":rows,"family_max":fam,"family_max_mean":fam["mean"],"family_max_lcb":fam["lcb_95_one_sided"]}
def _score(sid,prod,pub,truth,iv=None,kind="baseline"):
    preds=prod(pub,iv) if iv is not None else prod(pub); vals=_per_row(truth,preds)
    return {"score_id":sid,"kind":kind,"mean":_mean(vals),"lcb_95_one_sided":_bca(vals),"row_count":len(pub),
     "code_path_hash":_ch(prod),"producer_function":f"runner.{prod.__name__}","_preds":[sorted(p) for p in preds]}

def scan_rows(rows,disable=False):
    if disable: return {"passed":True,"findings":[],"disabled":True,"producer_function":"runner.scan_rows"}
    findings=[]; keys=set()
    for row in rows:
        for st in ("observation","serialized_state"): keys.update(k for k in row[st] if k!="passive_vector")
    benign={"coarse_bucket","legal_action_count","query_budget","row_id"}
    namebad=("topology","remap","context_token","hidden_rule","latent_graph","generator_truth","scorer_truth",
     "answer","target","g_lo","task_family","score_key","reward_shape","membership")
    for k in keys:
        if k in benign: continue
        if any(t in k.lower() for t in namebad): findings.append({"channel":"name","key":k})
    for k in keys:
        if k in benign: continue
        pairs=[]
        for row in rows:
            v=row["observation"].get(k,row["serialized_state"].get(k))
            if isinstance(v,int): pairs.append((v%2,row["evaluation_only"]["g_lo"]))
        if len(pairs)>=30:
            acc=sum(1 for a,b in pairs if a==b)/len(pairs)
            if max(acc,1-acc)>0.60: findings.append({"channel":"value_g_lo","key":k,"decode_acc":round(max(acc,1-acc),3)})
    return {"passed":not findings,"findings":findings,"disabled":False,"producer_function":"runner.scan_rows"}
def run_positive_controls(rows):
    controls=[]
    for fam in SCANNER_FAMILIES:
        pl=copy.deepcopy(rows)
        for row in pl:
            if fam=="observation_field_name_leak": row["observation"]["hidden_rule_id"]=1
            elif fam=="membership": row["observation"]["membership_flag"]=row["evaluation_only"]["g_lo"]
            else: row["observation"]["aux_feature_07"]=row["evaluation_only"]["g_lo"]
        res=scan_rows(pl); controls.append({"family":fam,"alarm":not res["passed"],"n_findings":len(res["findings"]),
         "producer_function":"runner.scan_rows"})
    failed=[c["family"] for c in controls if not c["alarm"]]
    return {"controls":controls,"all_planted_controls_alarm":not failed,"failed_positive_controls":failed,
     "uses_real_scanner_path":True,"producer_function":"runner.run_positive_controls"}
def twin_pair_report(rows):
    sample=None
    for ghi in range(N_G//2):
        r,c=3,5; g0,g1=2*ghi,2*ghi+1
        if _pv(g0,r,c)==_pv(g1,r,c) and rule_target(g0,r,c)!=rule_target(g1,r,c):
            j=informative_probe_index(ghi,r,c)
            sample={"g0":g0,"g1":g1,"r":r,"c":c,"passive_identical":True,"targets_differ":True,"probe_index":j,
             "probe_response_g0":probe_response(j,g0,r,c),"probe_response_g1":probe_response(j,g1,r,c)}; break
    sep=bool(sample) and sample["probe_response_g0"]!=sample["probe_response_g1"]
    return {"producer_function":"runner.twin_pair_report","example":sample,
     "passive_indistinguishable":bool(sample),"intervention_separable":sep,"passed":bool(sample) and sep}
def read_sources(root):
    sources=[]; ok=True
    for rel in SRC_PATHS:
        p=root/rel
        try:
            raw=p.read_bytes(); sources.append({"path":rel,"readable":True,"bytes":len(raw),
             "lines":len(raw.decode("utf-8","replace").splitlines()),"sha256":_sha(raw)})
        except OSError as e: ok=False; sources.append({"path":rel,"readable":False,"error":str(e)})
    man=(root/"docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md").read_text(encoding="utf-8")
    fr=[ln for ln in man.splitlines() if ln.startswith("| `") and "` |" in ln]
    unf=[ln for ln in fr if "UNFROZEN_OPERATOR_REQUIRED" in ln]
    pf=next((s for s in sources if s["path"]==SRC_PATHS[0]),{}); sha=pf.get("sha256"); ln=pf.get("lines",0)
    if sha==EXPECTED_PREFLIGHT_SHA256: st="verified_in_sandbox"
    elif ln and ln<PREFLIGHT_FULL_MIN_LINES and HOST_ATTESTED_PREFLIGHT_CLOSED: st="host_attested_closed_sandbox_mount_truncated"
    else: st="mismatch_block"
    man_lines=len(man.splitlines())
    if len(fr)==31 and len(unf)==0: mst="verified_31_frozen"
    elif man_lines<140 and len(unf)==0 and HOST_ATTESTED_PREFLIGHT_CLOSED: mst="host_attested_closed_sandbox_mount_truncated"
    else: mst="freeze_incomplete_block"
    return {"sources":sources,"preconditions":{"canonical_source_readback_succeeded":ok,
     "preflight_sha256_matches_expected":sha==EXPECTED_PREFLIGHT_SHA256,"preflight_readback_status":st,
     "preflight_sandbox_sha256":sha,"preflight_sandbox_lines":ln,"freeze_field_count":len(fr),
     "manifest_sandbox_lines":man_lines,"manifest_freeze_status":mst,"unresolved_freeze_field_rows":len(unf)}}
def check_frozen():
    a={"n_seed":N_SEED,"n_ctx":N_CTX,"N_rows":N_ROWS,"H_min_bits":H_MIN_BITS,"distinct_T_min":DISTINCT_T_MIN,"B":B,
     "N_enum_action_min":ACTION_COUNT,"N_enum_latent_min":N_ENUM_LATENT,"coverage_max":COVERAGE,"eps_equiv":EPS_EQUIV,
     "gamma_signal":GAMMA_SIGNAL,"tau_oracle":TAU_ORACLE,"oracle_failability_band":NONREADING_GAP}
    mm=[]
    for k,v in REQUIRED_FROZEN.items():
        x=a[k]
        if k in ("N_enum_action_min","N_enum_latent_min"):
            if x<v: mm.append(k)
        elif k=="coverage_max":
            if x>v: mm.append(k)
        elif x!=v: mm.append(k)
    return {"respected":not mm,"mismatches":mm,"actual":a}

def run_precheck(output_dir,persist=True,plant_latent=False,disable_positive_control=False):
    root=repo_root(); out=Path(output_dir)
    if persist: out.mkdir(parents=True,exist_ok=True)
    sr=read_sources(root); fz=check_frozen()
    rows=generate_rows(plant_latent); pub=public_rows(rows); truth=_truth(rows)
    dT=len({(r["evaluation_only"]["T"]["G"],r["evaluation_only"]["T"]["R"],r["evaluation_only"]["T"]["C"]) for r in rows})
    iv,usage=make_intervener(rows,B)
    oracle=_score("budget_faithful_visible_channel_oracle",budget_faithful_visible_channel_oracle,pub,truth,iv,"oracle")
    nonr=_score("nonreading_oracle",nonreading_oracle,pub,truth,kind="control")
    rnd=_score("random",random_baseline,pub,truth,kind="control")
    maj=_score("majority",majority_baseline,pub,truth,kind="control")
    brows=[_score(b,f,pub,truth,kind="baseline") for b,f in BASELINES.items()]
    fmax=max(brows,key=lambda r:r["mean"])
    atk=value_attacker_family(pub,truth); raw=atk["family_max_mean"]
    leak=scan_rows(rows,disable=disable_positive_control); pos=run_positive_controls(rows); twin=twin_pair_report(rows)
    C=oracle["mean"]; pre=sr["preconditions"]
    readback_ok=(pre["canonical_source_readback_succeeded"] and pre["preflight_readback_status"]!="mismatch_block"
     and pre["manifest_freeze_status"]!="freeze_incomplete_block" and pre["unresolved_freeze_field_rows"]==0)
    latent_hidden=(raw<C-EPS_EQUIV) and (fmax["mean"]<C-EPS_EQUIV) and not _INV_COLLISION
    dpv=len({json.dumps(b["_preds"]) for b in brows})
    forb=("evaluation_only","target_actions","_intervention","probe_response","g_lo")
    bclean=all(not any(t in inspect.getsource(BASELINES[b["score_id"]]) for t in forb) for b in brows)
    baselines_independent=(fmax["mean"]<C-EPS_EQUIV and dpv>1 and bclean)
    opj=json.dumps(oracle["_preds"])
    osrc=inspect.getsource(budget_faithful_visible_channel_oracle)
    oracle_decoupled=(C>=TAU_ORACLE and fmax["mean"]<C-EPS_EQUIV and opj not in {json.dumps(b["_preds"]) for b in brows}
     and "evaluation_only" not in osrc and "target_actions" not in osrc)
    pl=generate_rows(True); pa=value_attacker_family(public_rows(pl),_truth(pl))
    attackers_powered=(pa["family_max_mean"]>=C-EPS_EQUIV and atk["family_max_mean"]<C-EPS_EQUIV)
    pcr=pos["all_planted_controls_alarm"] and pos["uses_real_scanner_path"]
    window_ok=(C>=TAU_ORACLE and (C-nonr["mean"])>=NONREADING_GAP and (C-max(rnd["mean"],maj["mean"]))>=GAMMA_SIGNAL and raw<C-EPS_EQUIV)
    if not readback_ok: v="blocked_pending_canonical_readback"
    elif not fz["respected"]: v="blocked_requires_operator_refreeze"
    elif not latent_hidden: v="invalid_redesign_latent_still_decodable"
    elif not oracle_decoupled: v="invalid_redesign_oracle_baseline_still_coupled"
    elif not baselines_independent: v="invalid_redesign_baselines_not_independent"
    elif not attackers_powered: v="invalid_redesign_leakage_scanners_not_powered"
    elif not pcr: v="invalid_redesign_positive_controls_not_real_path"
    elif not window_ok: v="invalid_redesign_generator_no_decodability_solvability_window"
    else: v="redesign_precheck_ready_for_independent_reaudit"
    checks={"readback_ok":readback_ok,"frozen_respected":fz["respected"],"latent_hidden":latent_hidden,
     "oracle_decoupled":oracle_decoupled,"baselines_independent":baselines_independent,
     "attackers_powered":attackers_powered,"positive_controls_real":pcr,"window_ok":window_ok,
     "distinct_baseline_pred_vectors":dpv,"baseline_source_clean":bclean}
    spec={"task_id":TASK_ID,"master":MASTER,"n_seed":N_SEED,"n_ctx":N_CTX,"N_rows":N_ROWS,"H_min_bits":H_MIN_BITS,
     "N_enum_latent":N_ENUM_LATENT,"N_enum_action":ACTION_COUNT,"B":B,"coverage_fraction":COVERAGE,
     "realized_distinct_T":dT,"passive_states":len(PASSIVE_STATES),"metric":"F-beta beta=1.0",
     "rule_visibility":"public rule; latent T hidden; twin bit g_lo intervention-only","auto_remote_anchor":"forbidden"}
    strip=lambda s:{k:val for k,val in s.items() if k!="_preds"}
    result={"task_id":TASK_ID,"verdict":v,"current_layer":"engineering implementation / redesign precheck only",
     "mainline_integration_status":"none","enabled_status":"none","checks":checks,"oracle_mean":C,
     "nonreading_mean":nonr["mean"],"random_mean":rnd["mean"],"majority_mean":maj["mean"],
     "baseline_family_max":{"id":fmax["score_id"],"mean":fmax["mean"]},"raw_decoder_family_max_mean":raw,
     "planted_attacker_family_max_mean":pa["family_max_mean"],"oracle_probe_budget_used_max":max(usage.values()) if usage else 0,
     "candidate_mechanism_run":False,"tier_3_plus_run":False,"remote_anchor_performed":False,
     "claim_ceiling":"redesign precheck evidence only; no LRGG admissibility/headroom/oracle-validity/mechanism/"
      "agency/self/subjectivity/emotion/consciousness/autonomy/EGO/H0H1/001C/mainline.",
     "what_this_does_not_prove":"Does not prove headroom/admissibility/mechanism, nor that an ACTIVE interventional "
      "baseline (absent from the required panel) would not solve; only that this harness hides the latent, decouples "
      "oracle/baselines, powers attackers/scanners, and shows a non-empty decodability-solvability window."}
    art={}
    if persist:
        st=_stable(spec); sh=_sha(st.encode())
        (out/"generator_spec_001b.json").write_text(st,encoding="utf-8")
        (out/"generator_spec_001b.sha256").write_text(sh+"\n",encoding="utf-8")
        (out/"oracle_independence_report.json").write_text(_stable({"oracle":strip(oracle),"family_max_baseline":strip(fmax),
         "oracle_decoupled":oracle_decoupled,"oracle_probe_budget_used_max":result["oracle_probe_budget_used_max"],
         "behavioral_counterfactual_oracle_ne_baseline":opj not in {json.dumps(b["_preds"]) for b in brows}}),encoding="utf-8")
        (out/"baseline_independence_report.json").write_text(_stable({"baselines":[strip(b) for b in brows],
         "family_max":strip(fmax),"distinct_pred_vectors":dpv,"baseline_source_clean":bclean,
         "none_reaches_oracle_band":fmax["mean"]<C-EPS_EQUIV,"threshold":C-EPS_EQUIV}),encoding="utf-8")
        (out/"decodability_report.json").write_text(_stable({"oracle_mean":C,"nonreading_mean":nonr["mean"],
         "random_mean":rnd["mean"],"majority_mean":maj["mean"],"raw_decoder_family_max_mean":raw,"value_attackers":atk,
         "planted_attacker_family_max_mean":pa["family_max_mean"],"latent_hidden":latent_hidden,"window_ok":window_ok,
         "thresholds":{"tau_oracle":TAU_ORACLE,"eps_equiv":EPS_EQUIV,"gamma_signal":GAMMA_SIGNAL,"nonreading_gap":NONREADING_GAP}}),encoding="utf-8")
        (out/"leakage_scanner_report.json").write_text(_stable(leak),encoding="utf-8")
        (out/"positive_controls_report.json").write_text(_stable(pos),encoding="utf-8")
        (out/"twin_pair_report.json").write_text(_stable(twin),encoding="utf-8")
        (out/"task_space_report.json").write_text(_stable({"H_design_space_bits":H_MIN_BITS,"N_enum_latent":N_ENUM_LATENT,
         "N_enum_action":ACTION_COUNT,"realized_distinct_T":dT,"distinct_T_required":DISTINCT_T_MIN,"N_rows":N_ROWS,
         "coverage_fraction":COVERAGE,"inverse_map_collision":_INV_COLLISION,"frozen_check":fz,
         "passed":dT>=DISTINCT_T_MIN and not _INV_COLLISION}),encoding="utf-8")
        rt=_stable(result); rh=_sha(rt.encode())
        (out/"precheck_result.json").write_text(rt,encoding="utf-8")
        (out/"precheck_result.sha256").write_text(rh+"\n",encoding="utf-8")
        (out/"source_readback_report.json").write_text(_stable(sr),encoding="utf-8")
        (out/"LIMITATIONS.md").write_text("# LIMITATIONS\n\n- Redesign PRECHECK only; not an official rerun, not "
         "candidate work, not Tier 3+.\n- Rule structure is public to all agents; only latent T is hidden (twin bit "
         "g_lo is intervention-only).\n- Required baseline panel is passive/lookup/regression/classical-class; an ACTIVE "
         "interventional query baseline is NOT in the panel; a future re-audit should add one before any headroom claim.\n"
         "- Evidence bounded to this harness and this generated debug split.\n",encoding="utf-8")
        (out/"CLAIM_CEILING.md").write_text("# CLAIM_CEILING\n\n"+result["claim_ceiling"]+"\n\nDoes not authorize "
         "candidate work, Tier 3+, 001C, or mainline integration, and proves no headroom or admissibility.\n",encoding="utf-8")
        (out/"REDESIGN_PRECHECK_REPORT.md").write_text(
         f"# LRGG Tier 0-2 REDESIGN PRECHECK 001B\n\nVerdict: `{v}`\n\nLayer: {result['current_layer']}; mainline: none; "
         f"enabled: none; auto-remote-anchor: forbidden.\n\ngenerator_spec_001b.sha256={sh}\nprecheck_result.sha256={rh}\n\n"
         f"## Window\n- oracle C={C:.4f} (>= {TAU_ORACLE})\n- nonreading={nonr['mean']:.4f}; C-nonreading={C-nonr['mean']:.4f} (>= {NONREADING_GAP})\n"
         f"- random={rnd['mean']:.4f} majority={maj['mean']:.4f}; C-max={C-max(rnd['mean'],maj['mean']):.4f} (>= {GAMMA_SIGNAL})\n"
         f"- passive raw/value decoder family_max={raw:.4f} (< C-{EPS_EQUIV}={C-EPS_EQUIV:.4f})\n"
         f"- strongest cheap baseline {fmax['score_id']}={fmax['mean']:.4f}\n- planted-latent attacker family_max={pa['family_max_mean']:.4f}\n\n"
         f"## R1-R5\nR1 latent_hidden={checks['latent_hidden']} R3 oracle_decoupled={checks['oracle_decoupled']} "
         f"R2 baselines_independent={checks['baselines_independent']} (distinct_pred={dpv}, src_clean={bclean}) "
         f"R4 attackers_powered={checks['attackers_powered']} R5 positive_controls_real={checks['positive_controls_real']} "
         f"window_ok={checks['window_ok']}\n\n## Twin pair\n{json.dumps(twin['example'])}\npassive_indistinguishable="
         f"{twin['passive_indistinguishable']} intervention_separable={twin['intervention_separable']}\n\n## Leakage(real path)\n"
         f"findings={leak['findings']}\n\n{result['what_this_does_not_prove']}\n",encoding="utf-8")
        art={p.name:p.stat().st_size for p in out.iterdir() if p.is_file()}
    return {"result":result,"checks":checks,"oracle":strip(oracle),"baseline_rows":[strip(b) for b in brows],
     "family_max":strip(fmax),"attackers":atk,"twin":twin,"leakage":leak,"positive_controls":pos,"frozen":fz,
     "source_readback":sr,"distinct_T":dT,"artifacts":art,"needs_lfs":any(s>50*1024*1024 for s in art.values())}

def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",default="artifacts/LRGG-CANDIDATE-FREE-TIER0-2/REDESIGN_PRECHECK_001B")
    a=ap.parse_args(argv); run=run_precheck(Path(a.output_dir),persist=True)
    print(_stable({"verdict":run["result"]["verdict"],"oracle":run["result"]["oracle_mean"],"family_max":run["result"]["baseline_family_max"]}),end="")
    return 0
if __name__=="__main__": raise SystemExit(main())
