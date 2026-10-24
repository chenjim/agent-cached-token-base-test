import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import numpy as np, os

FONT="/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
fm.fontManager.addfont(FONT)
plt.rcParams["font.family"]="WenQuanYi Zen Hei"
plt.rcParams["axes.unicode_minus"]=False
plt.rcParams["figure.dpi"]=150

OUT=os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT,exist_ok=True)

C={"opencode":"#2f6f9f","pi":"#c46a2f","hermes":"#6b8f3a"}
CL=["opencode","pi","hermes"]

# 数据
tok={
 "werkzeug":{"opencode":[425480,330881],"pi":[418531,723875],"hermes":[1669977,1796397]},
 "pytest":{"opencode":[265593,319834],"pi":[270190,282030],"hermes":[1040104,615141]},
}
cost={
 "werkzeug":{"opencode":[0.010345014,0.013508076],"pi":[0.011033886,0.011031354],"hermes":[0.034707564,0.041385720]},
 "pytest":{"opencode":[0.006405840,0.012120447],"pi":[0.008288286,0.007895934],"hermes":[0.029315946,0.017207556]},
}
hit={
 "werkzeug":{"opencode":[91.51,81.33],"pi":[89.53,94.11],"hermes":[94.19,92.01]},
 "pytest":{"opencode":[90.83,83.74],"pi":[89.87,87.70],"hermes":[91.02,92.35]},
}

# 图1：总 token（两轮均值）
fig,axes=plt.subplots(1,2,figsize=(11,4.2))
for ax,(proj,title) in zip(axes,[("werkzeug","werkzeug（#3234 ETag 修复）"),("pytest","pytest（#15150 junitxml 截断）")]):
    means=[np.mean(tok[proj][c])/1000 for c in CL]
    errs=[[abs(means[i]-min(tok[proj][c])/1000) for i,c in enumerate(CL)],
          [abs(max(tok[proj][c])/1000-means[i]) for i,c in enumerate(CL)]]
    bars=ax.bar(CL,means,color=[C[c] for c in CL],width=0.55,
                yerr=errs,capsize=5,error_kw={"ecolor":"#555","lw":1.2})
    for b,v,c in zip(bars,means,CL):
        ax.text(b.get_x()+b.get_width()/2,v+errs[1][CL.index(c)]+8,f"{v:.0f}K",ha="center",va="bottom",fontsize=10)
    ax.set_title(title,fontsize=11)
    ax.set_ylabel("总 token（千）")
    ax.set_ylim(0,max(max(tok[proj][c])/1000 for c in CL)*1.18)
    ax.grid(axis="y",alpha=.25)
    ax.set_axisbelow(True)
fig.suptitle("两轮平均总 token 消耗：Hermes 明显更高",fontsize=13)
fig.tight_layout()
fig.savefig(f"{OUT}/01-tokens.png",bbox_inches="tight")
plt.close(fig)

# 图2：缓存命中率
fig,ax=plt.subplots(figsize=(8,4))
x=np.arange(2); w=0.26
for i,(proj,name) in enumerate([("werkzeug","werkzeug"),("pytest","pytest")]):
    for j,c in enumerate(CL):
        v=hit[proj][c]
        ax.bar(i+(j-1)*w,np.mean(v),width=w,color=C[c],label=c if i==0 else None)
        ax.text(i+(j-1)*w,np.mean(v)+2.2,f"{np.mean(v):.1f}%",ha="center",fontsize=8.5)
        ax.plot([i+(j-1)*w-0.09,i+(j-1)*w+0.09],[v[0]]*2,color="#333",lw=0.9,alpha=.6)
        ax.plot([i+(j-1)*w-0.09,i+(j-1)*w+0.09],[v[1]]*2,color="#333",lw=0.9,alpha=.6)
ax.set_xticks(x); ax.set_xticklabels(["werkzeug","pytest"])
ax.set_ylabel("缓存命中率 %"); ax.set_ylim(0,100)
ax.set_title("缓存命中率：三端都在 86%–93%，差异很小（零轴起，横线为两轮实际值）",fontsize=11)
ax.legend(ncol=3,frameon=False,loc="lower center",bbox_to_anchor=(0.5,-0.22))
ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(f"{OUT}/02-cache-hit.png",bbox_inches="tight")
plt.close(fig)

# 图3：成本
fig,ax=plt.subplots(figsize=(8,4))
for i,proj in enumerate(["werkzeug","pytest"]):
    for j,c in enumerate(CL):
        v=np.mean(cost[proj][c])*100
        ax.bar(i+(j-1)*w,v,width=w,color=C[c],label=c if i==0 else None)
        ax.text(i+(j-1)*w,v+0.1,f"${v:.1f}",ha="center",fontsize=8.5)
ax.set_xticks([0,1]); ax.set_xticklabels(["werkzeug","pytest"])
ax.set_ylabel("单次任务成本（美分）")
ax.set_title("单次任务成本：Hermes 为 opencode 的 2.5–4.5 倍",fontsize=11)
ax.legend(ncol=3,frameon=False,loc="upper right")
ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(f"{OUT}/03-cost.png",bbox_inches="tight")
plt.close(fig)

# 图4：两轮方差（散点连线）
fig,axes=plt.subplots(1,2,figsize=(11,4.0))
for ax,proj in zip(axes,["werkzeug","pytest"]):
    for c in CL:
        v=[x/1000 for x in tok[proj][c]]
        ax.plot([0,1],v,"o-",color=C[c],label=c,markersize=6,lw=1.8)
        off={"opencode":(-14,10),"pi":(-4,-18),"hermes":(-6,10)}
        ax.annotate(f"{v[0]:.0f}K",(0,v[0]),textcoords="offset points",
                    xytext=off[c],fontsize=8.5,color=C[c],ha="center")
        off2={"opencode":(14,10),"pi":(14,-16),"hermes":(14,8)}
        ax.annotate(f"{v[1]:.0f}K",(1,v[1]),textcoords="offset points",
                    xytext=off2[c],fontsize=8.5,color=C[c],ha="center")
    ax.set_xticks([0,1]); ax.set_xticklabels(["第 1 轮","第 2 轮"]); ax.set_xlim(-0.35,1.35)
    ax.set_ylim(0,max(max(tok[proj][c]) for c in CL)/1000*1.25)
    ax.set_title(proj); ax.set_ylabel("总 token（千）")
    ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True)
axes[0].legend(frameon=False,loc="center left")
fig.suptitle("同一配置两轮之间差异可达 1–2 倍，单轮结果不可下结论",fontsize=12)
fig.tight_layout()
fig.savefig(f"{OUT}/04-variance.png",bbox_inches="tight")
plt.close(fig)

print("done")
