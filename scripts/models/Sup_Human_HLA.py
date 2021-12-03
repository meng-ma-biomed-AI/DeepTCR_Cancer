"""This script is used to train the HLA-only model on the CheckMate-038 Clinical Trial Data."""

from DeepTCR.DeepTCR import DeepTCR_WF
import numpy as np
import os

gpu = 1
os.environ["CUDA DEVICE ORDER"] = 'PCI_BUS_ID'
os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu)

DTCR = DeepTCR_WF('HLA')
DTCR.Get_Data(directory='../../Data',Load_Prev_Data=False,
               aa_column_beta=1,count_column=2,v_beta_column=7,d_beta_column=14,j_beta_column=21,data_cut=1.0,
              hla='../../Data/HLA_Ref_sup_AB.csv')

folds = 100
LOO = 6
epochs_min = 10
size_of_net = 'small'
num_concepts=64
hinge_loss_t = 0.3
train_loss_min=0.1
seeds = np.array(range(folds))
graph_seed = 0
#
DTCR.Monte_Carlo_CrossVal(folds=folds,LOO=LOO,epochs_min=epochs_min,size_of_net=size_of_net, num_concepts=num_concepts,
                          combine_train_valid=True,hinge_loss_t=hinge_loss_t,train_loss_min=train_loss_min,seeds=seeds,
                          graph_seed=graph_seed,use_only_hla=True)
DTCR.DFs_pred['crpr'].to_csv('sample_hla.csv',index=False)