#!/usr/bin/env python
import pandas as pd
import os
import sys
crate = sys.argv[1] 
outDir = sys.argv[2]
des = sys.argv[3]
outdirxlxs = os.path.join(outDir,'xlxs')
outdirtext = os.path.join(outDir,'text')
outdirtext_aligned = os.path.join(outDir,'text_aligned')

if not os.path.exists(outdirxlxs) : os.makedirs(outdirxlxs)
if not os.path.exists(outdirtext) : os.makedirs(outdirtext)
if not os.path.exists(outdirtext_aligned) : os.makedirs(outdirtext_aligned)


correct_order =['Side','Eta','Phi','dPhi','Depth','Det','RBX','Sect','Pix','Let_Code','QIE8','QIECH','RM','RM_FI',
                'FI_CH','Block_Coupler','Crate','uHTR','MTP','uHTR_fib','FEDid','QIE8id']

FEDID_dict = {"c23left"  : 1124,
              "c23right" : 1125,
              "c26left"  : 1128,
              "c26right" : 1129,
              "c27left"  : 1126,
              "c27right" : 1127,
              "c38left"  : 1130,
              "c38right" : 1131
            }

mapping_uhtr = pd.read_excel("patch.xlsx", sheet_name='uhtr_side_c'+crate)
mapping_phi = pd.read_excel("patch.xlsx", sheet_name='det_side_c'+crate)
oldlMap = pd.read_excel("Lmap_HO_L_20190208.xlsx",sheet_name='HTR')
outxlxs = os.path.join(outdirxlxs,'mapping_phi.xlsx')


Calib_Lmap = pd.read_excel("ngHOcalib.xlsx", sheet_name='Lmap_HOcalib')
Calib_Emap = pd.read_excel("ngHOcalib.xlsx", sheet_name='Emap_HOcalib')

couplers_convert = {0:6,1:5,2:4,3:3,4:2,5:1}

if os.path.exists(outxlxs) : 
    if ( "y" in des or "Y" in des or "Yes" in des) :
        os.remove(outxlxs)
    elif ( "N" in des or  "n" in des or  "No" in des ): print(outxlxs , "will be ovewritten -- take care"  )
    else :
    	raise ValueError( "do not understand your potion")    

columns = []
for i in range(1,36+1) : 
    columns.append("C"+str(i))
mapping_phi_2 = pd.DataFrame(columns=columns,index=[0,1,2,3,4,5])

for j,col in enumerate(columns) :
    for i in range(0,6):
        val = str(mapping_phi[col][i].strip())
        if 'XX' in val : continue 
        rm = val.split(' ')[1].replace('RM','')
        rbx = val.split(' ')[0]
        ring = rbx.replace('HO','')[0]
        side = -9
        if rbx.replace('HO','')[1] == 'M' : 
            side = '-'+ring
        elif rbx.replace('HO','')[1] == 'P' :
            side = '+'+ring
        else :
            side = '0'
        rbx_no = rbx[-2:] if not rbx[-2] == '0' else rbx[-1]
        #print(side , ring, rbx,rbx_no, rm)
        rm_fi = j+2 
        if (rm_fi > 7 and rm_fi <= 13) : 
            rm_fi = rm_fi - 6 
        elif (rm_fi > 13 and rm_fi <= 19) : 
            rm_fi = rm_fi - 12
        elif (rm_fi > 19 and rm_fi <= 25) : 
            rm_fi = rm_fi - 18
        elif (rm_fi > 25 and rm_fi <= 31) : 
            rm_fi = rm_fi - 24
        elif (rm_fi > 31 and rm_fi <= 37) : 
            rm_fi = rm_fi - 30
        if rm == '5' : rm_fi = 1
        code = side+rbx_no+'-'+rm+str(rm_fi)

        #print(j, side , ring, rbx,rbx_no, rm,code)

        mapping_phi_2[col][i]  = code

mode = 'a' if os.path.exists(outxlxs) else 'W'
with pd.ExcelWriter(outxlxs,mode=mode ) as writer : 
    mapping_phi_2.to_excel(writer,sheet_name='block_phi_c'+crate,index=False)


print ("Fiber allocation in the patch pannel has been done")
print (10*"--")
print ("now to Lmap")
print (10*"--")

outxlxsLmap = os.path.join(outdirxlxs,'Lmap.xlsx')

if os.path.exists(outxlxsLmap) : 
    if ( "y" in des or "Y" in des or "Yes" in des) :
        os.remove(outxlxsLmap)
    elif ( "N" in des or  "n" in des or  "No" in des ): print(outxlxsLmap , "will be ovewritten -- take care"  )
    else :
    	raise ValueError( "do not understand your potion")    

new_Map = oldlMap.drop(columns=['Unnamed: 28','oSLBmap', 'oSLB_lnk', 'oSLB_bit','HTR', 'HTRTB', 'HTR_FI'])
new_Map = new_Map.dropna()
# drop the unused elements
idx_Drop = new_Map.loc[(new_Map['Block_Coupler'] == 0)].index 
new_Map = new_Map.drop(axis=0,index=idx_Drop)
idx_Drop_2 = new_Map.loc[(new_Map['Det'] == 'HOXX')].index 
new_Map = new_Map.drop(axis=0,index=idx_Drop_2)

new_Map = new_Map.loc[(new_Map['Crate'] == int(crate)-20)]
new_Map['Crate'] = int(crate)
new_Map['uHTR'] = ''
#new_Map['uhtr_fib'] = ''
new_Map['MTP'] = ''
new_Map['mtp_fib'] = ''
new_Map['uHTR_fib'] = ''
new_Map['Block_Coupler']=''
new_Map['rbx_no'] = new_Map['RBX'].str[-2:].astype(int) #if not new_Map['RBX'].str[-2] == '0' else new_Map['RBX'].str[-1]
new_Map['ring'] = ''
new_Map['code'] = ''

ringM_idx = new_Map.loc[(new_Map['RBX'].str[-3] == "M")].index
ringP_idx = new_Map.loc[(new_Map['RBX'].str[-3] == "P")].index
ring0_idx = new_Map.loc[(new_Map['RBX'].str[-3] == "0")].index


new_Map.loc[ringM_idx,'ring']= "-"+new_Map["RBX"][ringM_idx].str[2]
new_Map.loc[ringP_idx,'ring']= '+'+new_Map["RBX"][ringP_idx].str[2]
new_Map.loc[ring0_idx,'ring']= new_Map["RBX"][ring0_idx].str[2]

new_Map['code'] = new_Map['ring']+new_Map['rbx_no'].astype(str) +'-'+ new_Map['RM'].astype(str)+new_Map['RM_FI'].astype(str)

for index, colval in new_Map.iterrows():
    rloc , cloc ,cidx= -999 ,-999,-999
    match = False
    #print(row['code'])
    for row_ in range(mapping_phi_2.shape[0]): # df is the DataFrame
        if match == True : break 
        for cidx_, col_ in enumerate(mapping_phi_2.columns):
            if mapping_phi_2[col_][row_] == colval['code']:
                rloc , cloc,cidx = row_, col_ ,cidx_
                match = True
                break
    #
    if (rloc == -999 or cloc == -999 or cidx_ == -999) : continue
    #print(mapping_uhtr[cloc][rloc])
    new_Map.loc[index,'uHTR'] = int(mapping_uhtr[cloc][rloc].split("-")[0])
    new_Map.loc[index,'MTP'] = int(mapping_uhtr[cloc][rloc].split("-")[1])
    new_Map.loc[index,'mtp_fib'] = mapping_uhtr[cloc][rloc].split("-")[2]
    new_Map.loc[index,'Block_Coupler']= str(couplers_convert[rloc])+","+str(cidx+1)
    new_Map.loc[index,'uHTR_fib'] = (int(new_Map.loc[index,'mtp_fib'])  - 1 )+ (12* int(new_Map.loc[index,'MTP']))
    if new_Map.loc[index,'Crate'] == 33 : 
        new_Map.loc[index,'Crate'] = 38 

new_Map = new_Map.drop(columns=['ring','rbx_no','code','DCC_SL','Spigot','DCC','mtp_fib'])
new_Map = new_Map[correct_order]
new_Map = (new_Map.replace(r'^\s*$', "#N/A", regex=True))

new_Map.loc[new_Map.loc[(new_Map['Crate'] == 23) & (new_Map['uHTR'].astype(int) <= 6)].index,'FEDid'] = FEDID_dict["c23left"]
new_Map.loc[new_Map.loc[(new_Map['Crate'] == 23) & (new_Map['uHTR'].astype(int) >  6)].index,'FEDid'] = FEDID_dict["c23right"]
new_Map.loc[new_Map.loc[(new_Map['Crate'] == 26) & (new_Map['uHTR'].astype(int) <= 6)].index,'FEDid'] = FEDID_dict["c26left"]
new_Map.loc[new_Map.loc[(new_Map['Crate'] == 26) & (new_Map['uHTR'].astype(int) >  6)].index,'FEDid'] = FEDID_dict["c26right"]
new_Map.loc[new_Map.loc[(new_Map['Crate'] == 27) & (new_Map['uHTR'].astype(int) <= 6)].index,'FEDid'] = FEDID_dict["c27left"]
new_Map.loc[new_Map.loc[(new_Map['Crate'] == 27) & (new_Map['uHTR'].astype(int) >  6)].index,'FEDid'] = FEDID_dict["c27right"]
new_Map.loc[new_Map.loc[(new_Map['Crate'] == 38) & (new_Map['uHTR'].astype(int) <= 6)].index,'FEDid'] = FEDID_dict["c38left"]
new_Map.loc[new_Map.loc[(new_Map['Crate'] == 38) & (new_Map['uHTR'].astype(int) >  6)].index,'FEDid'] = FEDID_dict["c38right"]



mode = 'a' if os.path.exists(outxlxsLmap) else 'W'
with pd.ExcelWriter(outxlxsLmap,mode=mode ) as writer : 
    new_Map.to_excel(writer,sheet_name='Lmap_c'+crate,index=False)

xl = pd.ExcelFile(outxlxsLmap)
sheetlist = xl.sheet_names 

if not 'Calib_Lmap' in  sheetlist : 
    print ("ngHO calibration map is not existing in ",outxlxsLmap,"will add it")
    with pd.ExcelWriter(outxlxsLmap,mode='a' ) as writer : 
        Calib_Lmap.to_excel(writer,sheet_name='Calib_Lmap',index=False)
        Calib_Lmap = Calib_Lmap.drop(columns=['dodeca'])
        Calib_Lmap.to_csv(os.path.join(outdirtext,'Lmap_ngHOCalib.txt'), sep='\t',header=True, index=False)
        file = open(os.path.join(outdirtext_aligned,'Lmap_ngHOCalib_aligned.txt'),"w") 
        with open(os.path.join(outdirtext,'Lmap_ngHOCalib.txt'), 'r') as f:
            for line in f:
                data = line.split()
                x = [str(x) for x in range(1,26)]
                #print(data.formate(*x))
                file.write('{0[0]:<7}{0[1]:<7}{0[2]:<5}{0[3]:<7}{0[4]:<7}{0[5]:<12}{0[6]:<10}{0[7]:<7}{0[8]:<7}{0[9]:<10}{0[10]:<7}{0[11]:<7}{0[12]:<7}{0[13]:<7}{0[14]:<7}{0[15]:<15}{0[16]:<7}{0[17]:<7}{0[18]:<7}{0[19]:<10}{0[20]:<7}{0[21]:<7}'.format(data))
                file.write('\n')
        f.close()


new_Map.to_csv(os.path.join(outdirtext,'Lmap_c'+crate+'.txt'), sep='\t',header=True, index=False)
# to align the coloumns with the wight spaces
file = open(os.path.join(outdirtext_aligned,'Lmap_c'+crate+'_aligned.txt'),"w") 
with open(os.path.join(outdirtext,'Lmap_c'+crate+'.txt'), 'r') as f:
    for line in f:
        data = line.split()
        x = [str(x) for x in range(1,26)]
        #print(data.formate(*x))
        file.write('{0[0]:<7}{0[1]:<7}{0[2]:<5}{0[3]:<7}{0[4]:<7}{0[5]:<12}{0[6]:<10}{0[7]:<7}{0[8]:<7}{0[9]:<10}{0[10]:<7}{0[11]:<7}{0[12]:<7}{0[13]:<7}{0[14]:<7}{0[15]:<15}{0[16]:<7}{0[17]:<7}{0[18]:<7}{0[19]:<10}{0[20]:<7}{0[21]:<7}'.format(data))
        file.write('\n')
f.close()

print (10*"--")
print ("now to Emap")
print (10*"--")

# now to the Emap
correct_order =['i','cr','sl','tb','dcc','dodeca','fib/slb','fibch/slbch','subdet','eta','phi','dep']
LMap = pd.read_excel(outxlxsLmap,sheet_name='Lmap_c'+crate)
outxlxsEmap = os.path.join(outdirxlxs,'Emap_ngHO.xlsx')

if os.path.exists(outxlxsEmap) : 
    if ( "y" in des or "Y" in des or "Yes" in des) :
        os.remove(outxlxsEmap)
    elif ( "N" in des or  "n" in des or  "No" in des ): print(outxlxsEmap , "will be ovewritten -- take care"  )
    else :
    	raise ValueError( "do not understand your potion")    

#Side Eta Phi dPhi	Depth	Det	RBX	Sect Pix Let_Code QIE8 QIECH RM	RM_FI FI_CH	Block_Coupler Crate	uHTR MTP uHTR_fib FEDid	QIE8id
Emap = pd.DataFrame(columns=correct_order)

Emap['cr'] = LMap['Crate']
Emap.loc[Emap.loc[(Emap['cr'] == 33)].index,'cr'] = 38
Emap['sl'] = LMap['uHTR']
Emap['tb'] = 'u' 
Emap['dcc'] = 0
Emap['dodeca'] = 0
Emap['fib/slb'] = LMap['uHTR_fib']
Emap['fibch/slbch'] = LMap['FI_CH']
Emap['subdet'] = LMap['Det']
Emap['eta'] = LMap['Eta']*LMap['Side']
Emap['phi'] = LMap['Phi'] 
Emap['dep'] = LMap['Depth']
Emap.loc[Emap.loc[(Emap['subdet'] == 'HOX')].index,'dep'] = -999
Emap['i'] = '4200458C'

#Eidx_Drop = Emap.loc[(Emap['sl'] == '#N/A')].index 
#Emap = Emap.drop(axis=0,index=Eidx_Drop)

Emap = Emap.dropna()
Emap['sl'] = Emap['sl'].astype(int)
Emap['fib/slb'] = Emap['fib/slb'].astype(int)

# convert floats to int

Emap = Emap[correct_order]
#Emap = (Emap.replace(r'^\s*$', "#N/A", regex=True))

mode = 'a' if os.path.exists(outxlxsEmap) else 'W'

with pd.ExcelWriter(outxlxsEmap,mode=mode ) as writer :
    Emap.to_excel(writer,sheet_name='Emap_ngHO_c'+crate,index=False)

xl = pd.ExcelFile(outxlxsEmap)
sheetlist = xl.sheet_names 

if not 'Calib_Emap' in sheetlist : 
    print ("ngHO calibration map is not existing in ",outxlxsEmap,"will add it")
    with pd.ExcelWriter(outxlxsEmap,mode='a' ) as writer : 
        Calib_Emap.to_excel(writer,sheet_name='Calib_Emap',index=False)
        Calib_Emap.to_csv(os.path.join(outdirtext,'Emap_ngHOCalib.txt'), sep='\t',header=True, index=False)
        file = open(os.path.join(outdirtext_aligned,'Emap_ngHOCalib_aligned.txt'),"w") 
        with open(os.path.join(outdirtext,'Emap_ngHOCalib.txt'), 'r') as f:
            for line in f:
                data = line.split()
                x = [str(x) for x in range(1,13)]
                #print(data.formate(*x))
                file.write('{0[0]:<12}{0[1]:<7}{0[2]:<5}{0[3]:<7}{0[4]:<7}{0[5]:<12}{0[6]:<12}{0[7]:<12}{0[8]:<12}{0[9]:<10}{0[10]:<7}{0[11]:<7}'.format(data))
                file.write('\n')
        f.close()

Emap.to_csv(os.path.join(outdirtext,'Emap_ngHO_c'+crate+'.txt'), sep='\t',header=True, index=False)
file = open(os.path.join(outdirtext_aligned,'Emap_ngHO_c'+crate+'_aligned.txt'),"w") 
with open(os.path.join(outdirtext,'Emap_ngHO_c'+crate+'.txt'), 'r') as f:
    for line in f:
        data = line.split()
        x = [str(x) for x in range(1,13)]
        #print(data.formate(*x))
        file.write('{0[0]:<12}{0[1]:<7}{0[2]:<5}{0[3]:<7}{0[4]:<7}{0[5]:<12}{0[6]:<12}{0[7]:<12}{0[8]:<12}{0[9]:<10}{0[10]:<7}{0[11]:<7}'.format(data))
        file.write('\n')
f.close()

print (10*"--")
print ("now to Trigger allocation Lmap")
print (10*"--")

Trig_LMap = LMap.copy()
HOX_idx = Trig_LMap.loc[(Trig_LMap['Det'] == "HOX")].index
Trig_LMap = Trig_LMap.drop(HOX_idx).reset_index(drop=True)
Trig_LMap['Type'] = 0
Trig_LMap.loc[Trig_LMap.loc[(Trig_LMap['uHTR'] == 1) | (Trig_LMap['uHTR'] == 3)| (Trig_LMap['uHTR'] == 6)| (Trig_LMap['uHTR'] == 8) ].index,'Type'] = 1
Trig_LMap.loc[Trig_LMap.loc[(Trig_LMap['uHTR'] == 2) | (Trig_LMap['uHTR'] == 5)| (Trig_LMap['uHTR'] == 7) ].index,'Type'] = 2
Trig_LMap.loc[Trig_LMap.loc[(Trig_LMap['uHTR'] == 4)].index,'Type'] = 3
Trig_LMap['Tx_1'] = 0
Trig_LMap['Tx_2']  = 0
Trig_LMap['Tx_3']  = 0
Trig_LMap['Tx_fib']  = 0

Trig_LMap.loc[Trig_LMap.loc[(Trig_LMap['Eta'] < 5)].index,'Tx_1'] = 7
Trig_LMap.loc[Trig_LMap.loc[(Trig_LMap['Eta'] >= 5)].index,'Tx_1'] = ((Trig_LMap['Phi']+1)/3 % 3).astype(int) + 4 
Trig_LMap['Tx_2'] = ((Trig_LMap['Phi']+1)/3 % 2).astype(int) + 5 + Trig_LMap['Side'] 
#=MOD(INT((C2045+1)/3),2)+4
Trig_LMap['Tx_3'] = ((Trig_LMap['Phi']+1)/3 % 2).astype(int) + 4 

Trig_LMap.loc[Trig_LMap.loc[(Trig_LMap['Type'] == 1)].index,'Tx_fib'] = Trig_LMap.loc[Trig_LMap.loc[(Trig_LMap['Type'] == 1)].index,'Tx_1']
Trig_LMap.loc[Trig_LMap.loc[(Trig_LMap['Type'] == 2)].index,'Tx_fib'] = Trig_LMap.loc[Trig_LMap.loc[(Trig_LMap['Type'] == 2)].index,'Tx_2']
Trig_LMap.loc[Trig_LMap.loc[(Trig_LMap['Type'] == 3)].index,'Tx_fib'] = Trig_LMap.loc[Trig_LMap.loc[(Trig_LMap['Type'] == 3)].index,'Tx_3']

Trig_LMap['Tx_LC'] = Trig_LMap['Tx_fib'] - 3 
#=2*INT(MOD(C2+1;72)/6)+1
Trig_LMap['phi1'] = 2 * (((Trig_LMap['Phi']+1) % 72)/6).astype(int) + 1 
#=MID(G2;3;1)*A2+3
Trig_LMap['TM_row'] = (Trig_LMap['RBX'].str[2].astype(int)*Trig_LMap['Side']) + 3 
Trig_LMap['TM_col'] = 0
#=IF(OR(Eta>4;type=3);INT(MOD(Phi+1;72)/3)+1;phi1+IF(OR(uHTR=1;uHTR=6);0;1))
Trig_LMap.loc[Trig_LMap.loc[(Trig_LMap['Eta'] > 4) |(Trig_LMap['Type'] == 3) ].index,'TM_col'] = (((Trig_LMap['Phi']+1) % 72)/3).astype(int) + 1
Trig_LMap.loc[Trig_LMap.loc[((Trig_LMap['Eta'] <= 4) & (Trig_LMap['Type']!= 3)) & ((Trig_LMap['uHTR'] == 1 ) | (Trig_LMap['uHTR'] == 6 )) ].index,'TM_col'] = Trig_LMap['phi1'] + 0 
Trig_LMap.loc[Trig_LMap.loc[((Trig_LMap['Eta'] <= 4) & (Trig_LMap['Type']!= 3)) & ((Trig_LMap['uHTR'] != 1 ) & (Trig_LMap['uHTR'] != 6 )) ].index,'TM_col'] = Trig_LMap['phi1'] + 1 

#=(AB2-1)*24+AC2
Trig_LMap['TM_fib'] = ( (Trig_LMap['TM_row'] - 1) * 24 ) + Trig_LMap['TM_col']

# load the twinMux LUT 
Trig_LMap['TM_label']  = ''
TMux_LUT = open("TwinMux_LUT.txt","r")
for line in TMux_LUT : 
    line = line.strip()
    if line[0] == '#': continue
    (idx, label) = line.split()
    #print(idx, label)
    Trig_LMap.loc[Trig_LMap.loc[(Trig_LMap['TM_fib'] == int(idx)) ].index,'TM_label'] = label

Trig_LMap = Trig_LMap.drop(columns=['Type','Tx_1','Tx_2','Tx_3','Tx_fib','phi1'])

outxlxs_trig = os.path.join(outdirxlxs,'Trig_Lmap.xlsx')
mode = 'a' if os.path.exists(outxlxs_trig) else 'W'
with pd.ExcelWriter(outxlxs_trig,mode=mode ) as writer : 
    Trig_LMap.to_excel(writer,sheet_name='Trig_Lmap_'+crate,index=False)


Trig_LMap.to_csv(os.path.join(outdirtext,'Trig_LMap_ngHO_c'+crate+'.txt'), sep='\t',header=True, index=False)
file = open(os.path.join(outdirtext_aligned,'Trig_LMap_ngHO_c'+crate+'_aligned.txt'),"w") 
with open(os.path.join(outdirtext,'Trig_LMap_ngHO_c'+crate+'.txt'), 'r') as f:
    for line in f:
        data = line.split()
        x = [str(x) for x in range(1,13)]
        #print(data.formate(*x))
        file.write('{0[0]:<7}{0[1]:<7}{0[2]:<5}{0[3]:<7}{0[4]:<7}{0[5]:<12}{0[6]:<10}{0[7]:<7}{0[8]:<7}{0[9]:<10}{0[10]:<7}{0[11]:<7}{0[12]:<7}{0[13]:<7}{0[14]:<7}{0[15]:<15}{0[16]:<7}{0[17]:<7}{0[18]:<7}{0[19]:<10}{0[20]:<7}{0[21]:<10}{0[22]:<7}{0[23]:<7}{0[24]:<7}{0[25]:<7}{0[26]:<12}'.format(data))
        file.write('\n')
f.close()

Trig_patch = Trig_LMap.copy()
Trig_patch = Trig_patch.drop_duplicates(subset=['TM_label'], keep='first', inplace=False)

Trig_patch = Trig_patch[['uHTR','Tx_LC','TM_row','TM_col','TM_fib','TM_label']]

trig_patch_xlxs =  os.path.join(outdirxlxs,'Trig_patch.xlsx')

mode = 'a' if os.path.exists(trig_patch_xlxs) else 'W'
with pd.ExcelWriter(trig_patch_xlxs,mode=mode ) as writer : 
    Trig_patch.to_excel(writer,sheet_name='Trig_patch_'+crate,index=False)


print (10*"--")
print ("all Done, Relaxxxxxx")
print (10*"--")