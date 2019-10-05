#!/usr/bin/env python
import pandas as pd
import os
import sys
crate = sys.argv[1]
outDir = sys.argv[2]
outdirxlxs = os.path.join(outDir,'xlxs')
outdirtext = os.path.join(outDir,'text')
outdirtext_aligned = os.path.join(outDir,'text_aligned')

if not os.path.exists(outdirxlxs) : os.makedirs(outdirxlxs)
if not os.path.exists(outdirtext) : os.makedirs(outdirtext)
if not os.path.exists(outdirtext_aligned) : os.makedirs(outdirtext_aligned)


correct_order =['Side','Eta','Phi','dPhi','Depth','Det','RBX','Sect','Pix','Let_Code','QIE8','QIECH','RM','RM_FI',
                'FI_CH','Block_Coupler','Crate','uHTR','MTP','uHTR_fib','FEDid','QIE8id']


mapping_uhtr = pd.read_excel("patch.xlsx", sheet_name='uhtr_side_c'+crate)
mapping_phi = pd.read_excel("patch.xlsx", sheet_name='det_side_c'+crate)
oldlMap = pd.read_excel("Lmap_HO_L_20190208.xlsx",sheet_name='HTR')
outxlxs = os.path.join(outdirxlxs,'mapping_phi.xlsx')

couplers_convert = {0:6,1:5,2:4,3:3,4:2,5:1}

if os.path.exists(outxlxs) : 
    des = input("out file exists: "+outxlxs+' would you like to remove it ? Y/N: ') 
    if ( "y" in des or "Y" in des or "Yes" in des) :
        os.remove(outxlxs)
    elif ( "N" in des or  "n" in des or  "No" in des ): print(outxlxs , "will be ovewritten -- take care"  )
    else :
    	raise ValueError( "do not understand your potion")    
des = ''

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
    des = input("out file exists: "+outxlxsLmap+' would you like to remove it ? Y/N: ') 
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
    new_Map.loc[index,'uHTR'] = mapping_uhtr[cloc][rloc].split("-")[0]
    new_Map.loc[index,'MTP'] = mapping_uhtr[cloc][rloc].split("-")[1]
    new_Map.loc[index,'mtp_fib'] = mapping_uhtr[cloc][rloc].split("-")[2]
    new_Map.loc[index,'Block_Coupler']= str(couplers_convert[rloc])+","+str(cidx+1)
    new_Map.loc[index,'FEDid']= new_Map.loc[index,'FEDid'] + 400
    new_Map.loc[index,'uHTR_fib'] = (int(new_Map.loc[index,'mtp_fib'])  - 1 )+ (12* int(new_Map.loc[index,'MTP']))
    if new_Map.loc[index,'Crate'] == 33 : 
        new_Map.loc[index,'Crate'] = 38 
        new_Map.loc[index,'FEDid'] = new_Map.loc[index,'FEDid'] + 4
new_Map = new_Map.drop(columns=['ring','rbx_no','code','DCC_SL','Spigot','DCC','mtp_fib'])
new_Map = new_Map[correct_order]
new_Map = (new_Map.replace(r'^\s*$', "#N/A", regex=True))

mode = 'a' if os.path.exists(outxlxsLmap) else 'W'
with pd.ExcelWriter(outxlxsLmap,mode=mode ) as writer : 
    new_Map.to_excel(writer,sheet_name='Lmap_c'+crate,index=False)

new_Map.to_csv(os.path.join(outdirtext,'Lmap_c'+crate+'.txt'), sep='\t',header=True, index=False)
# to align the coloumns with the wight spaces
file = open(os.path.join(outdirtext_aligned,'Lmap_c'+crate+'_aligned.txt'),"w") 
with open(os.path.join(outdirtext,'Lmap_c'+crate+'.txt'), 'r') as f:
    for line in f:
        data = line.split()
        x = [str(x) for x in range(1,26)]
        #print(data.formate(*x))
        file.write('{0[0]:<7}{0[1]:<7}{0[2]:<5}{0[3]:<7}{0[4]:<7}{0[5]:<7}{0[6]:<7}{0[7]:<7}{0[8]:<7}{0[9]:<10}{0[10]:<7}{0[11]:<7}{0[12]:<7}{0[13]:<7}{0[14]:<7}{0[15]:<15}{0[16]:<7}{0[17]:<7}{0[18]:<7}{0[19]:<10}{0[20]:<7}{0[21]:<7}'.format(data))
        file.write('\n')
f.close()

print (10*"--")
print ("now to Emap")
print (10*"--")

# now to the Emap
correct_order =['i','cr','sl','tb','dcc','spigot','fib/slb','fibch/slbch','subdet','eta','phi','dep']
LMap = pd.read_excel(outxlxsLmap,sheet_name='Lmap_c'+crate)
outxlxsEmap = os.path.join(outdirxlxs,'Emap_ngHO.xlsx')

if os.path.exists(outxlxsEmap) : 
    des = input("out file exists: "+outxlxsEmap+' would you like to remove it ? Y/N: ') 
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
Emap['dcc'] = '0'
Emap['spigot'] = '0'
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

Emap.to_csv(os.path.join(outdirtext,'Emap_ngHO_c'+crate+'.txt'), sep='\t',header=True, index=False)
file = open(os.path.join(outdirtext_aligned,'Emap_ngHO_c'+crate+'_aligned.txt'),"w") 
with open(os.path.join(outdirtext,'Emap_ngHO_c'+crate+'.txt'), 'r') as f:
    for line in f:
        data = line.split()
        x = [str(x) for x in range(1,13)]
        #print(data.formate(*x))
        file.write('{0[0]:<12}{0[1]:<7}{0[2]:<5}{0[3]:<7}{0[4]:<7}{0[5]:<7}{0[6]:<12}{0[7]:<12}{0[8]:<12}{0[9]:<10}{0[10]:<7}{0[11]:<7}'.format(data))
        file.write('\n')
f.close()


print (10*"--")
print ("all Done, Relaxxxxxx")
print (10*"--")