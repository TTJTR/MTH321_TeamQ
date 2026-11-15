"""Publication-sized figures from the archived log and common-point replay."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;O=R.parents[1]/'figures';O.mkdir(exist_ok=True)
d=json.loads((R/'comparison.json').read_text())
colors=['#aaaaaa','#666666','#222222'];seeds=[11,22,33]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,'axes.labelsize':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(6.35,2.7),layout='constrained')
for seed,col,style in zip(seeds,colors,["-","--",":"]):
 with (R/f'archive/interface_c10_seed{seed}/training.csv').open() as f:rows=[r for r in csv.DictReader(f) if r['stage']=='adam']
 ax.semilogy([int(r['step']) for r in rows],[float(r['total']) for r in rows],color=col,ls=style,lw=1.3,label=f'Seed {seed}')
ax.set(xlabel='Adam step',ylabel='Weighted total training loss',xlim=(0,10000));ax.grid(color='#dce4ea',lw=.6);ax.legend(frameon=False,ncol=3,loc='upper right',fontsize=8)
fig.savefig(O/'fig08_pinn_training.pdf');fig.savefig(O/'fig08_pinn_training.png',dpi=300);plt.close(fig)
fig,axes=plt.subplots(2,1,figsize=(6.35,3.5),layout='constrained')
for ax,key,title in zip(axes,['relative_l2','flux_max_error'],['Sampled relative solution error','Maximum absolute interface-flux error']):
 vals=[d[m][key] for m in ['FDM','FEM','Interface PINN']]
 for i,(v,col) in enumerate(zip(vals,['#196b91','#c7642b','#8175BE'])):
  ax.scatter(v,i,s=34,color=col,zorder=3)
  ax.annotate(f'{v:.2e}',(v,i),xytext=(7,0),textcoords='offset points',va='center',fontsize=8,color=col)
 ax.set_xscale('log');ax.set_xlim(1e-16,.1);ax.set_ylim(2.45,-.45)
 ax.set_yticks(range(3),['Harmonic FDM','Fitted P1 FEM','Interface PINN'])
 ax.set_xticks([1e-15,1e-12,1e-9,1e-6,1e-3]);ax.tick_params(length=0,labelsize=8)
 ax.grid(axis='x',color='#dce4ea',lw=.6);ax.set_title(title,loc='left',pad=8)
 for sp in ax.spines.values():sp.set_visible(False)
fig.savefig(O/'fig09_pinn_accuracy.pdf');fig.savefig(O/'fig09_pinn_accuracy.png',dpi=300);plt.close(fig)
print('Saved report-sized training and accuracy figures.')
