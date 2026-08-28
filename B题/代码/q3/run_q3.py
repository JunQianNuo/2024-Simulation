"""Q3-M3：后序局部核 + 闭环奖励方程，完整枚举 65536 个固定策略。"""

from __future__ import annotations

from collections import deque
import json
from pathlib import Path

import numpy as np
import pandas as pd


LEAVES = {1: (.10, 2, 1), 2: (.10, 8, 1), 3: (.10, 12, 2), 4: (.10, 2, 1), 5: (.10, 8, 1), 6: (.10, 12, 2), 7: (.10, 8, 1), 8: (.10, 12, 2)}
NODES = {"s1": ((1, 2, 3), .10, 8, 4, 6), "s2": ((4, 5, 6), .10, 8, 4, 6), "s3": ((7, 8), .10, 8, 4, 6), "root": (("s1", "s2", "s3"), .10, 8, 6, 10)}
PRICE, REPLACEMENT = 200, 40
OUTDIR = Path(__file__).resolve().parent.parent / "results" / "q3"
TOL = 1e-10
COSTS = ["purchase", "part_inspection", "semi_inspection", "final_inspection", "semi_assembly", "final_assembly", "semi_disassembly", "final_disassembly", "replacement_loss"]
EVENTS = ["expected_part_inspections", "expected_semi_inspections", "expected_final_inspections", "expected_semi_assemblies", "expected_final_assemblies", "expected_semi_disassemblies", "expected_final_disassemblies", "expected_replacements"] + [f"expected_part_inspections_{i}" for i in range(1, 9)]
KERNEL_CACHE = {}
BATCH_CACHE = {}


def zero(): return np.zeros(len(COSTS) + len(EVENTS))
def ci(name): return COSTS.index(name)
def ei(name): return len(COSTS) + EVENTS.index(name)
def decode(i):
    b = tuple((i >> j) & 1 for j in range(16))
    return b, b[:8], b[8:11], b[11], b[12:15], b[15]


def solve_loop(reward, repeat):
    """真实求解 A V=r，并返回相对残差；A=1-repeat。"""
    a = np.array([[1.0 - repeat]])
    rhs = reward.reshape(1, -1)
    value = np.linalg.solve(a, rhs)
    residual = np.linalg.norm(a @ value - rhs, ord=np.inf) / (np.linalg.norm(rhs, ord=np.inf) + 1.0)
    return value[0], float(residual)


def leaf(leaf_id, inspect):
    defect, buy, test = LEAVES[leaf_id]
    r = zero(); r[ci("purchase")] = buy
    if not inspect: return 1 - defect, r, 0.0, 0.0, 0
    r[ci("part_inspection")] = test; r[ei("expected_part_inspections")] = 1; r[ei(f"expected_part_inspections_{leaf_id}")] = 1
    value, residual = solve_loop(r, defect)
    return 1.0, value, defect, residual, 1


def input_batch(ids, inspections):
    """精确处理一组叶件的“补购后从头重检”流程，等价于 Q2 的 prepare 状态机。"""
    key = (tuple(ids), tuple(inspections))
    if key in BATCH_CACHE: return BATCH_CACHE[key]
    n = len(ids); start = (0, (-1,) * n); states=[start]; index={start:0}; queue=deque([start]); raw={}
    while queue:
        phase, quality = queue.popleft(); r=zero(); trans=[]; good=0.0
        if phase == 0:
            missing=[j for j,q in enumerate(quality) if q<0]
            for j in missing: r[ci("purchase")] += LEAVES[ids[j]][1]
            outcomes=[[(quality[j],1.0)] if quality[j]>=0 else [(1,.9),(0,.1)] for j in range(n)]
            for combo in np.array(np.meshgrid(*[np.arange(len(x)) for x in outcomes])).T.reshape(-1,n):
                q=tuple(outcomes[j][combo[j]][0] for j in range(n)); p=float(np.prod([outcomes[j][combo[j]][1] for j in range(n)])); trans.append(((1,q),p))
        else:
            j=phase-1
            if inspections[j]:
                r[ci("part_inspection")] += LEAVES[ids[j]][2]; r[ei("expected_part_inspections")] += 1; r[ei(f"expected_part_inspections_{ids[j]}")] += 1
                if quality[j]==0:
                    q=list(quality);q[j]=-1;trans=[((0,tuple(q)),1.0)]
                elif phase==n: good=float(all(q==1 for q in quality))
                else: trans=[((phase+1,quality),1.0)]
            elif phase==n: good=float(all(q==1 for q in quality))
            else: trans=[((phase+1,quality),1.0)]
        raw[(phase,quality)]=(trans,good,r)
        for nxt,p in trans:
            if p and nxt not in index:index[nxt]=len(states);states.append(nxt);queue.append(nxt)
    m=len(states);P=np.zeros((m,m));g=np.zeros(m);R=np.zeros((m,len(zero())))
    for s,i in index.items():
        trans,success,r=raw[s];g[i]=success;R[i]=r
        for nxt,p in trans:P[i,index[nxt]]+=p
    A=np.eye(m)-P; X=np.linalg.solve(A,np.column_stack([R,g])); residual=np.linalg.norm(A@X-np.column_stack([R,g]),ord=np.inf)/(np.linalg.norm(R,ord=np.inf)+1)
    result=float(X[0,-1]),X[0,:-1],float(residual),1
    BATCH_CACHE[key]=result;return result


def retest_children(children, policy):
    """安全拆解后的同一批已知合格直接子件：只重检，不采购或重装。"""
    _, parts, semis, _, _, _ = policy
    r = zero()
    for child in children:
        if isinstance(child, int):
            if parts[child - 1]:
                r[ci("part_inspection")] += LEAVES[child][2]
                r[ei("expected_part_inspections")] += 1; r[ei(f"expected_part_inspections_{child}")] += 1
        else:
            i = int(child[1]) - 1
            if semis[i]:
                r[ci("semi_inspection")] += NODES[child][3]
                r[ei("expected_semi_inspections")] += 1
    return r


def node(name, policy):
    """返回 (良率、奖励、最大重复概率、最大真实残差、局部方程数)。"""
    bits, parts, semis, yf, dis_semis, zf = policy
    if name != "root":
        i = int(name[1]) - 1; start, stop = ((0, 3), (3, 6), (6, 8))[i]
        key = (name, parts[start:stop], semis[i], dis_semis[i])
        if key in KERNEL_CACHE: return KERNEL_CACHE[key]
    children, defect, assembly, inspection, disassembly = NODES[name]
    root = name == "root"
    if all(isinstance(c, int) for c in children):
        q_batch, r_batch, batch_residual, batch_count = input_batch(children, [parts[c-1] for c in children])
        child = [(q_batch, r_batch, 0.0, batch_residual, batch_count)]
    else:
        child = [node(c, policy) for c in children]
    q = (1 - defect) * float(np.prod([x[0] for x in child]))
    first = sum((x[1] for x in child), zero())
    asm_cost, asm_event = ("final_assembly", "expected_final_assemblies") if root else ("semi_assembly", "expected_semi_assemblies")
    inspect_cost, inspect_event = ("final_inspection", "expected_final_inspections") if root else ("semi_inspection", "expected_semi_inspections")
    dis_cost, dis_event = ("final_disassembly", "expected_final_disassemblies") if root else ("semi_disassembly", "expected_semi_disassemblies")
    first[ci(asm_cost)] += assembly; first[ei(asm_event)] += 1
    tested = yf if root else semis[int(name[1]) - 1]
    dismantle = zf if root else dis_semis[int(name[1]) - 1]
    all_good = all(abs(x[0] - 1) <= TOL for x in child)
    base_loop = max(x[2] for x in child); base_residual = max(x[3] for x in child); base_count = sum(x[4] for x in child)
    if tested and dismantle and not all_good: raise ValueError("NON_ABSORBING")
    if root and not tested and dismantle:
        if not all_good: raise ValueError("NON_ABSORBING")
        cycle = zero(); cycle[ci(asm_cost)] = assembly; cycle[ci(dis_cost)] = defect * disassembly; cycle[ci("replacement_loss")] = defect * REPLACEMENT
        cycle[ei(asm_event)] = 1; cycle[ei(dis_event)] = defect; cycle[ei("expected_replacements")] = defect
        cycle += defect * retest_children(children, policy)
        value, residual = solve_loop(cycle, defect)
        return 1.0, sum((x[1] for x in child), zero()) + value, max(base_loop, defect), max(base_residual, residual), base_count + 1
    if not tested:
        result = q, first, base_loop, base_residual, base_count
        if not root: KERNEL_CACHE[key] = result
        return result
    first[ci(inspect_cost)] += inspection; first[ei(inspect_event)] += 1
    if not dismantle:
        value, residual = solve_loop(first, 1 - q)
        result = 1.0, value, max(base_loop, 1 - q), max(base_residual, residual), base_count + 1
        if not root: KERNEL_CACHE[key] = result
        return result
    # 安全拆解：失败仅来自条件装配缺陷；回收后的直接子件按原策略再次检测。
    cycle = zero(); cycle[ci(asm_cost)] = assembly; cycle[ci(inspect_cost)] = inspection; cycle[ci(dis_cost)] = defect * disassembly
    cycle[ei(asm_event)] = 1; cycle[ei(inspect_event)] = 1; cycle[ei(dis_event)] = defect
    cycle += defect * retest_children(children, policy)
    value, residual = solve_loop(cycle, defect)
    result = 1.0, sum((x[1] for x in child), zero()) + value, max(base_loop, defect), max(base_residual, residual), base_count + 1
    if not root: KERNEL_CACHE[key] = result
    return result


def evaluate(strategy_id):
    bits, parts, semis, yf, dis_semis, zf = decode(strategy_id)
    row = {"strategy_id": strategy_id, "strategy_bits": "".join(map(str, bits)), **{f"x{i}": parts[i - 1] for i in range(1, 9)}, **{f"y{i}": semis[i - 1] for i in range(1, 4)}, "yf": yf, **{f"z{i}": dis_semis[i - 1] for i in range(1, 4)}, "zf": zf, "status": "SUCCESS_EXACT"}
    try:
        q, reward, loop, residual, count = node("root", (bits, parts, semis, yf, dis_semis, zf))
        if not yf and not zf:
            reward[ci("replacement_loss")] += (1 - q) * REPLACEMENT; reward[ei("expected_replacements")] += 1 - q
            reward, r = solve_loop(reward, 1 - q); residual = max(residual, r); loop = max(loop, 1 - q); count += 1
        row.update({"local_loop_equations": count, "max_local_loop_probability": loop, "max_local_equation_residual": residual})
        for name, value in zip(COSTS, reward[:len(COSTS)]): row[f"cost_{name}"] = float(value)
        for name, value in zip(EVENTS, reward[len(COSTS):]): row[name] = float(value)
        row["expected_total_cost"] = float(reward[:len(COSTS)].sum()); row["expected_profit"] = PRICE - row["expected_total_cost"]
        row["one_pass_success_no_inspection"] = .9 ** 12; row["factory_defect_rate"] = 0.0 if yf else row["expected_replacements"] / (1 + row["expected_replacements"])
    except ValueError as exc:
        if str(exc) != "NON_ABSORBING": raise
        row.update({"status": "NON_ABSORBING", "local_loop_equations": np.nan, "max_local_loop_probability": 1.0, "max_local_equation_residual": np.nan, "one_pass_success_no_inspection": .9 ** 12})
    return row


def explicit_two(policy):
    """独立小型显式链：两零件、检测、装配、市场/拆解；只用于内置交叉验证。"""
    x1, x2, y, z = policy; p, buy, test, assembly, prod_test, dis, rep = .1, (2, 8), (1, 1), 8, 4, 6, 40
    names = ["p1", "p2", "i1", "i2", "asm", "ptest", "dis", "rep", "e1", "e2", "ea", "ep", "ed", "er"]
    start = ("prepare", -1, -1); states = [start]; idx = {start: 0}; queue = deque([start]); raw = {}
    while queue:
        s = queue.popleft(); phase, a, b = s; r = np.zeros(len(names)); trans=[]; success=0.0
        if phase == "prepare":
            r[0] = buy[0] if a < 0 else 0; r[1] = buy[1] if b < 0 else 0
            aa = [(a, 1)] if a >= 0 else [(1,.9),(0,.1)]; bb = [(b,1)] if b >= 0 else [(1,.9),(0,.1)]
            trans=[(("i1", u,v), pu*pv) for u,pu in aa for v,pv in bb]
        elif phase == "i1":
            if x1: r[2]=test[0]; r[8]=1; trans=[(("prepare",-1,b),1)] if a==0 else [(("i2",a,b),1)]
            else: trans=[(("i2",a,b),1)]
        elif phase == "i2":
            if x2: r[3]=test[1]; r[9]=1; trans=[(("prepare",a,-1),1)] if b==0 else [(("asm",a,b),1)]
            else: trans=[(("asm",a,b),1)]
        elif phase == "asm":
            good=.9 if a==b==1 else 0; r[4]=assembly; r[10]=1
            if y: r[5]=prod_test; r[11]=1; trans=[(("bad",a,b),1-good)]; success=good
            else: r[7]=(1-good)*rep; r[13]=1-good; trans=[(("bad",a,b),1-good)]; success=good
        else:
            if z: r[6]=dis; r[12]=1; trans=[(("i1",a,b),1)]
            else: trans=[(("prepare",-1,-1),1)]
        raw[s]=(trans,success,r)
        for nxt, prob in trans:
            if prob and nxt not in idx: idx[nxt]=len(states); states.append(nxt); queue.append(nxt)
    n=len(states); P=np.zeros((n,n)); absorb=np.zeros(n); R=np.zeros((n,len(names)))
    for s,i in idx.items():
        trans,success,r=raw[s]; absorb[i]=success; R[i]=r
        for nxt,prob in trans:P[i,idx[nxt]]+=prob
    # SCC-free proxy: a singular system is nonabsorbing for this finite substochastic chain.
    try: values=np.linalg.solve(np.eye(n)-P,np.column_stack([R,absorb]))
    except np.linalg.LinAlgError: return None
    if abs(values[0,-1]-1)>1e-10:return None
    return values[0,:-1]


def local_two(policy):
    """与 explicit_two 同参数的局部核，供独立交叉核验。"""
    x1,x2,y,z=policy; good,r,_,_=input_batch((1,2),(x1,x2)); q=.9*good
    if y and z:
        if not x1 or not x2:return None
        cycle=zero();cycle[ci("semi_assembly")]=8;cycle[ci("semi_inspection")]=4;cycle[ci("semi_disassembly")]=.6;cycle[ei("expected_semi_assemblies")]=1;cycle[ei("expected_semi_inspections")]=1;cycle[ei("expected_semi_disassemblies")]=.1;cycle+=.1*retest_children((1,2),((0,)*16,(x1,x2),(0,0,0),0,(0,0,0),0))
        return r+solve_loop(cycle,.1)[0]
    first=r.copy();first[ci("semi_assembly")]+=8;first[ei("expected_semi_assemblies")]+=1
    if y:
        first[ci("semi_inspection")]+=4;first[ei("expected_semi_inspections")]+=1;return solve_loop(first,1-q)[0]
    if z:
        if not x1 or not x2:return None
        cycle=zero();cycle[ci("semi_assembly")]=8;cycle[ci("semi_disassembly")]=.6;cycle[ci("replacement_loss")]=4;cycle[ei("expected_semi_assemblies")]=1;cycle[ei("expected_semi_disassemblies")]=.1;cycle[ei("expected_replacements")]=.1;cycle+=.1*retest_children((1,2),((0,)*16,(x1,x2),(0,0,0),0,(0,0,0),0));return r+solve_loop(cycle,.1)[0]
    first[ci("replacement_loss")]+=(1-q)*40;first[ei("expected_replacements")]+=1-q;return solve_loop(first,1-q)[0]


def crosscheck():
    for policy in ((0,0,0,0),(1,1,1,0),(1,1,1,1),(0,1,1,1)):
        exact, local = explicit_two(policy), local_two(policy)
        if (exact is None) != (local is None): raise RuntimeError(f"显式链/局部核吸收性不一致: {policy}")
        if exact is not None:
            local_cost=local[:len(COSTS)].sum(); exact_cost=exact[:8].sum()
            local_events=local[[ei("expected_part_inspections"),ei("expected_semi_inspections"),ei("expected_semi_assemblies"),ei("expected_semi_disassemblies"),ei("expected_replacements")]]
            exact_events=exact[[8,9,10,11,12,13]]
            if abs(local_cost-exact_cost)>1e-10 or np.max(np.abs(local_events-np.array([exact_events[0]+exact_events[1],exact_events[3],exact_events[2],exact_events[4],exact_events[5]])))>1e-10: raise RuntimeError(f"显式链/局部核奖励不一致: {policy}")


def validate_inputs():
    expected={1:(.1,2,1),2:(.1,8,1),3:(.1,12,2),4:(.1,2,1),5:(.1,8,1),6:(.1,12,2),7:(.1,8,1),8:(.1,12,2)}
    nodes={"s1":((1,2,3),.1,8,4,6),"s2":((4,5,6),.1,8,4,6),"s3":((7,8),.1,8,4,6),"root":(("s1","s2","s3"),.1,8,6,10)}
    if LEAVES!=expected or NODES!=nodes or (PRICE,REPLACEMENT)!=(200,40) or abs(.9**12-.282429536481)>1e-12: raise RuntimeError("表 2 / 图 1 参数或树结构校验失败")


def main():
    validate_inputs(); crosscheck(); KERNEL_CACHE.clear()
    all_rows=pd.DataFrame([evaluate(i) for i in range(65536)])
    if len(all_rows)!=65536 or all_rows.strategy_id.nunique()!=65536: raise RuntimeError("INCOMPLETE_POLICY_SET")
    if evaluate((1<<8)|(1<<12))["status"]!="NON_ABSORBING": raise RuntimeError("坏件回流微型策略未识别为 NON_ABSORBING")
    ok=all_rows[all_rows.status.eq("SUCCESS_EXACT")].copy(); cost_cols=[f"cost_{x}" for x in COSTS]
    if ok.empty or ok.max_local_equation_residual.max()>TOL or (ok[cost_cols].sum(axis=1)-ok.expected_total_cost).abs().max()>TOL or (ok.expected_profit-(PRICE-ok.expected_total_cost)).abs().max()>TOL: raise RuntimeError("局部方程、成本或利润自检失败")
    # 事件—成本一致性；安全拆解循环中的再次检测也由此得到验证。
    part_recomputed=sum(ok[f"expected_part_inspections_{i}"]*LEAVES[i][2] for i in range(1,9))
    if (ok.cost_part_inspection-part_recomputed).abs().max()>TOL: raise RuntimeError("零件检测成本与逐件检测次数不一致")
    mappings={"cost_semi_inspection":("expected_semi_inspections",4),"cost_final_inspection":("expected_final_inspections",6),"cost_semi_assembly":("expected_semi_assemblies",8),"cost_final_assembly":("expected_final_assemblies",8),"cost_semi_disassembly":("expected_semi_disassemblies",6),"cost_final_disassembly":("expected_final_disassemblies",10),"cost_replacement_loss":("expected_replacements",40)}
    for c,(e,unit) in mappings.items():
        if (ok[c]-ok[e]*unit).abs().max()>TOL: raise RuntimeError(f"{c} 与 {e} 不一致")
    best_profit=ok.expected_profit.max(); best=ok[(best_profit-ok.expected_profit).abs()<=1e-8*max(1,abs(best_profit))].sort_values("strategy_id")
    top3=ok.nlargest(3,"expected_profit").sort_values("expected_profit",ascending=False); gap=float(top3.iloc[0].expected_profit-top3.iloc[1].expected_profit)
    decision=[]
    for _,r in best.iterrows():
        for i in range(1,9):decision.append({"strategy_id":int(r.strategy_id),"node":f"part_{i}","inspect":int(r[f"x{i}"]),"disassemble":"N/A"})
        for i in range(1,4):decision.append({"strategy_id":int(r.strategy_id),"node":f"semi_{i}","inspect":int(r[f"y{i}"]),"disassemble":int(r[f"z{i}"])})
        decision.append({"strategy_id":int(r.strategy_id),"node":"final","inspect":int(r.yf),"disassemble":int(r.zf)})
    OUTDIR.mkdir(parents=True,exist_ok=True);all_rows.to_csv(OUTDIR/"all_policies.csv",index=False,encoding="utf-8-sig");best.to_csv(OUTDIR/"best_policies.csv",index=False,encoding="utf-8-sig");pd.DataFrame(decision).to_csv(OUTDIR/"decision_summary.csv",index=False,encoding="utf-8-sig")
    summary={"model":"Q3-M3","algorithm":"Q3-A1","solver":"后序局部核 + 树状闭环方程；全量策略不显式构造完整 P 矩阵，二零件显式链已独立交叉验证","policies_total":65536,"status_counts":all_rows.status.value_counts().to_dict(),"feasible_policies":int(len(ok)),"best_profit":best_profit,"best_policies":best.to_dict(orient="records"),"top3_feasible":top3.to_dict(orient="records"),"profit_gap_to_second":gap,"max_local_equation_residual":float(ok.max_local_equation_residual.max()),"max_local_loop_probability":float(ok.max_local_loop_probability.max()),"one_pass_success_no_inspection":.9**12,"one_pass_defect_no_inspection":1-.9**12,"crosscheck":"二零件显式 Markov 链与局部核在四个固定策略的吸收性、成本和事件次数上一致。","decision_note":"最优方案的回收循环已计入回收零件/半成品按既定策略再次检测的成本；最终成检是否采用由 6 元检测成本与 40 元调换损失的精确比较决定。"}
    (OUTDIR/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("65536 条策略状态统计:",all_rows.status.value_counts().to_dict());print(f"最大真实局部方程残差: {ok.max_local_equation_residual.max():.3e}")
    print(best[["strategy_id","strategy_bits","expected_profit","expected_total_cost","expected_part_inspections","expected_semi_inspections","expected_final_inspections","expected_semi_assemblies","expected_final_assemblies","expected_semi_disassemblies","expected_final_disassemblies","expected_replacements"]].to_string(index=False,float_format=lambda x:f"{x:.6f}"));print("结果目录:",OUTDIR)


if __name__ == "__main__": main()
