"""Figure 1D"""

from DeepTCR.DeepTCR import DeepTCR_SS, DeepTCR_WF, DeepTCR_U
from sklearn.metrics import roc_curve, roc_auc_score
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import umap
import pickle
from scipy.stats import gaussian_kde
def GKDE(x,y,z=None):
    xy = np.vstack([x, y])
    kernel = gaussian_kde(xy,weights=z)
    z = kernel(xy)
    r = np.argsort(z)
    x ,y, z = x[r], y[r], z[r]
    return x,y,z,kernel,r

classes = ['Control','RT','9H10','Combo']
DTCR = DeepTCR_U('Rudqvist_U',device=0)
DTCR.Get_Data(directory='../../Rudqvist',Load_Prev_Data=False,
               aa_column_beta=1,count_column=2,v_beta_column=7,d_beta_column=14,j_beta_column=21)
DTCR.Train_VAE(accuracy_min=0.98,Load_Prev_Data=True)
X_2 = umap.UMAP().fit_transform(DTCR.features)
df_x2 = pd.DataFrame(X_2)
df_x2.columns = ['x','y']
df_preds = pd.read_csv('preds.csv')
df_preds = pd.concat([df_preds,df_x2],axis=1)

with open('sample_preds.pkl','rb') as f:
    DFs_pred = pickle.load(f)

sample_list = []
pred_list = []
for cl in classes:
    temp = DFs_pred[cl].groupby(['Samples']).agg({'y_test': 'first', 'y_pred': 'mean'}).reset_index()
    temp = temp[temp['y_test'] == 1]
    temp.sort_values(by='y_pred',ascending=False,inplace=True)
    sample_list.append(list(temp['Samples']))
    pred_list.append(list(temp['y_pred']))

sample_list = np.hstack(sample_list)
pred_list = np.hstack(pred_list)
df_sample_pred = pd.DataFrame()
df_sample_pred['Samples'] = sample_list
df_sample_pred['pred'] = pred_list
sample_pred_dict = dict(zip(sample_list,pred_list))

win = 10
DFs = []
for cl in classes:
    cut_top = np.percentile(df_preds[cl],100-win)
    df_top = df_preds[df_preds[cl] > cut_top]
    DFs.append(df_top)

df_preds = pd.concat(DFs)
df_preds.drop_duplicates(inplace=True)

plt.scatter(X_2[:,0],X_2[:,1])
xlim = plt.xlim()
ylim = plt.ylim()
plt.close()
fig,ax = plt.subplots(4,5,figsize=(10,10))
for ii,cl in enumerate(classes,0):
    df_class = df_preds[df_preds['label']==cl]
    sample_sel = np.unique(df_class['sample'])
    for jj,s_ in enumerate(np.array(df_sample_pred[df_sample_pred['Samples'].isin(sample_sel)]['Samples']),0):
        df_sample = df_class[df_class['sample']==s_]
        df_sample.sort_values(by=cl,ascending=False,inplace=True)
        df_sample = df_sample.iloc[0:int(np.round(len(df_sample)*0.25))]
        c = np.array(df_sample[cl])
        s = np.array(df_sample['freq'])
        idx = np.argsort(c)
        x,y = np.array(df_sample['x']),np.array(df_sample['y'])
        # ax[ii,jj].scatter(x[idx], y[idx], c=c[idx], cmap='jet', s=s[idx] * 1000)
        x,y,z,_,_ = GKDE(x,y,s)
        ax[ii,jj].scatter(x, y,c=z, cmap='jet',s=10)
        ax[ii,jj].set_xticks([])
        ax[ii,jj].set_yticks([])
        ax[ii,jj].set_xlim(xlim)
        ax[ii,jj].set_ylim(ylim)
        ax[ii,jj].set_title(str(np.round(sample_pred_dict[s_],2)))
        if jj == 0:
            ax[ii,jj].set_ylabel(cl,fontsize=18)
plt.tight_layout()
plt.savefig('unsup.eps')

# fig,ax = plt.subplots(2,2,figsize=(10,10))
# ax = np.ndarray.flatten(ax)
# for ii,cl in enumerate(DTCR.lb.classes_,0):
#     c = np.array(df_preds[cl])
#     s = np.array(df_preds['freq'])
#     idx = np.argsort(c)
#     ax[ii].scatter(X_2[idx,0],X_2[idx,1],c=c[idx],cmap='jet',s=s[idx]*1000)
#     ax[ii].set_xticks([])
#     ax[ii].set_yticks([])
#     ax[ii].set_title(cl)


