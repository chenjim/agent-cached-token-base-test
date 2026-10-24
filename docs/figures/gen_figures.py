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

# 数据：三轮
tok={
 "werkzeug":{"opencode":[425480,330881,1048565],"pi":[418531,723875,567988],"hermes":[1669977,1796397,770543]},
 "pytest":{"opencode":[265593,319834,502043],"pi":[270190,282030,389662],"hermes":[1040104,615141,366588]},
}
cost={
 "werkzeug":{"opencode":[0.010345014,0.013508076,0.014898042],
             "pi":[0.011717886,0.011733954,0.014645460],
             "hermes":[0.034707564,0.041385720,0.016861578]},
 "pytest":{"opencode":[0.006405840,0.012120447,0.010876644],
           "pi":[0.010470486,0.008598534,0.009300882],
           "hermes":[0.029315946,0.017207556,0.012677220]},
}
hit={
 "werkzeug":{"opencode":[91.51,81.33,95.51],"pi":[89.53,94.11,88.58],"hermes":[94.19,92.01,93.56]},
 "pytest":{"opencode":[90.83,83.74,94.54],"pi":[89.87,87.70,93.78],"hermes":[91.02,92.35,90.10]},
}
ROUNDS=[1,2,3]

# 图1：总 token（三轮均值 + 最小/最大范围）
fig,axes=plt.subplots(1,2,figsize=(11,4.2))
for ax,(proj,title) in zip(axes,[("werkzeug","werkzeug（#3234 ETag 修复）"),("pytest","pytest（#15150 junitxml 截断）")]):
    means=[np.mean(tok[proj][c])/1000 for c in CL]
    lo=[(np.mean(tok[proj][c])-min(tok[proj][c]))/1000 for c in CL]
    hi=[(max(tok[proj][c])-np.mean(tok[proj][c]))/1000 for c in CL]
    bars=ax.bar(CL,means,color=[C[c] for c in CL],width=0.55,
                yerr=[lo,hi],capsize=5,error_kw={"ecolor":"#555","lw":1.2})
    for b,v,h_,c in zip(bars,means,hi,CL):
        ax.text(b.get_x()+b.get_width()/2,v+h_+10,f"{v:.0f}K",ha="center",va="bottom",fontsize=10)
    ax.set_title(title,fontsize=11)
    ax.set_ylabel("总 token（千）")
    ax.set_ylim(0,max(max(tok[proj][c]) for c in CL)/1000*1.18)
    ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True)
fig.suptitle("三轮平均总 token（误差棒为三轮最小—最大范围）",fontsize=13)
fig.tight_layout()
fig.savefig(f"{OUT}/01-tokens.png",bbox_inches="tight")
plt.close(fig)

# 图2：缓存命中率（均值 + 范围）
fig,ax=plt.subplots(figsize=(8,4))
x=np.arange(2); w=0.26
for i,(proj,name) in enumerate([("werkzeug","werkzeug"),("pytest","pytest")]):
    for j,c in enumerate(CL):
        v=hit[proj][c]; m=np.mean(v)
        lo=m-min(v); hi=max(v)-m
        ax.bar(i+(j-1)*w,m,width=w,color=C[c],label=c if i==0 else None,
               yerr=[[lo],[hi]],capsize=4,error_kw={"ecolor":"#444","lw":1.0})
        ax.text(i+(j-1)*w,max(v)+1.5,f"{m:.1f}%",ha="center",fontsize=8.5)
ax.set_xticks(x); ax.set_xticklabels(["werkzeug","pytest"])
ax.set_ylabel("缓存命中率 %"); ax.set_ylim(0,100)
ax.set_title("缓存命中率：三端都在 89%–93%，差异小于波动范围",fontsize=11)
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
        ax.text(i+(j-1)*w,v+0.08,f"${v:.1f}",ha="center",fontsize=8.5)
ax.set_xticks([0,1]); ax.set_xticklabels(["werkzeug","pytest"])
ax.set_ylabel("单次任务成本（美分）")
ax.set_ylim(0,max(np.mean(cost[p][c]) for p in ("werkzeug","pytest") for c in CL)*100*1.18)
ax.set_title("单次任务成本（三轮均值）",fontsize=11)
ax.legend(ncol=3,frameon=False,loc="upper right")
ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(f"{OUT}/03-cost.png",bbox_inches="tight")
plt.close(fig)

# 图4：三轮方差
fig,axes=plt.subplots(1,2,figsize=(11,4.0))
for ax,proj in zip(axes,["werkzeug","pytest"]):
    for c in CL:
        v=[x/1000 for x in tok[proj][c]]
        ax.plot(ROUNDS,v,"o-",color=C[c],markersize=6,lw=1.8)
        for xi,yi in zip(ROUNDS,v):
            ax.annotate(f"{yi:.0f}K",(xi,yi),textcoords="offset points",
                        xytext=(0,10 if c!="pi" else -16),fontsize=8,color=C[c],ha="center")
    ax.set_xticks(ROUNDS); ax.set_xticklabels([f"第 {r} 轮" for r in ROUNDS])
    ax.set_xlim(0.7,3.3)
    ax.set_ylim(0,max(max(tok[proj][c]) for c in CL)/1000*1.28)
    ax.set_title(proj); ax.set_ylabel("总 token（千）")
    ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True)
from matplotlib.lines import Line2D
handles=[Line2D([0],[0],color=C[c],marker="o",lw=1.8,label=c) for c in CL]
fig.legend(handles=handles,ncol=3,frameon=False,loc="lower center",bbox_to_anchor=(0.5,0.0))
fig.suptitle("三轮之间最大差 2.5 倍，单轮数据不能下结论",fontsize=12)
fig.tight_layout(rect=(0,0.07,1,1))
fig.savefig(f"{OUT}/04-variance.png",bbox_inches="tight")
plt.close(fig)
print("done")
