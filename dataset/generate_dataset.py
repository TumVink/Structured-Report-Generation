################################
########## generate dataset for DL training
########## output format in json file like:
##########  "report id":
#                   {lung:  {
#                           lung:{ 'edema', 'no clear',...
#                                   }
#                           left:{'no edema', 'clear'
#                            }
#                     heart:{...
#                           }
#                     labels:[1,0,1,0,......]
#
#                    }

import json
import os
from collections import Counter


global count
count=0
OB_modified = False



def del_space(s):
    #input: string
    #output: children-string after the space

    if " " in s:
        output = s.split()[-1]

        return output
    else:
        return s

def write_json(data,file_path):#'D:/studium/MIML/radgraph/radgraph/train_add_sug.json'
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile)

def gen_dict_for_each_report(organ,organ_modify,OBS_with_modify,OBS_label,dict_each_report,masked_each_report,ref_dict):
    #todo: if normal -> other attributes in this sub part are all 0 and masked = 1?

    global count
    # dic = {"organ":{"organ_modify":[3cm cancer]}}
    # output = {organ:{organ_modify:[clear, 3cm cancer]}}
    # dict_each_report = {
    #                   lung:  {
    #                           lung:[0,1,0,1...]
    #                           left:[1,1,0,]
    #                     heart:{...
    #                           }
    #
    #                    }
    #           }
    #masked_each_report in same format as dict_each_report, BUT "1" means it has such masks in the corressponding lables in this label,

    if organ and organ_modify and OBS_with_modify:       #output the dataset only if the organ and organ_modify and observation in the mapping list
        if organ in ref_dict.keys():
            if organ_modify in ref_dict[organ].keys():
                ls = ref_dict[organ][organ_modify]
                for i in range(len(ls)):
                    if OBS_with_modify == ls[i]:
                        if OBS_label == 'DP':
                            print("ja")
                            count +=1
                            dict_each_report[organ][organ_modify][i] = 1
                            masked_each_report[organ][organ_modify][i] = 1
                        elif OBS_label == 'DA':
                            print("nein")
                            count += 1
                            dict_each_report[organ][organ_modify][i] = 0
                            masked_each_report[organ][organ_modify][i] = 1
                        else: # if possible -> regard it as 'DP'
                            print("ja")
                            count += 1
                            dict_each_report[organ][organ_modify][i] = 1
                            masked_each_report[organ][organ_modify][i] = 1

    return dict_each_report,masked_each_report

def gen_dataset(dataset,id,dict_each_report,masked_each_report):
    ##########  dataset ={"report id":
        #                   {lung:  {
        #                           lung:{ 'edema', 'no clear',...
        #                                   }
        #                           left:{'no edema', 'clear'
        #                            }
        #                     heart:{...
        #                           }
        #                     labels:[1,0,1,0,......]
        #                     mask:[1,1,1,0,....]
        #                    }
        #                  "report id2":{...}
    labels_ls = []
    mask_ls = []
    ### flatten all attributes into one list
    for key,ls in dict_each_report.items():
        inner_dic = dict_each_report[key]
        for key1,ls1 in inner_dic.items():
            labels_ls.extend(ls1)

    for key,ls in masked_each_report.items():
        inner_dic = masked_each_report[key]
        for key1,ls1 in inner_dic.items():
            mask_ls.extend(ls1)
    ### generate the final dataset
    dataset[id] = {'labels':labels_ls,
                    'mask':mask_ls}

    return dataset


def update_dict(final_dict, dic):
    # final_dict = {}
    # dic = {"organ":{"organ_modify":[3cm cancer]}}
    # output = {organ:{organ_modify:[clear, 3cm cancer]}}
    for key, ls in dic.items():
        if key not in final_dict.keys():
            final_dict.update(dic)
        else:
            inner_dic = dic[key]
            inner_final_dic = final_dict[key]
            for inner_key, inner_ls in inner_dic.items():  # "organ_modify":[clear]
                if inner_key not in inner_final_dic.keys():
                    # inner_final_dic.update(inner_dic)   #need check if final_dict also updates
                    final_dict[key][inner_key] = inner_dic[inner_key]  # add the first [clear]
                else:
                    final_dict[key][inner_key].append(dic[key][inner_key][0])

    return final_dict


# p = os.getcwd().
def mapping_name(dict,value):
    for key,ls in dict.items():
        if value in ls:
            return key
    # if cant find the key
    return None

def filter_out_observations(input_dict):
    # input: dict= {"lung":[[],[]],
    #          "...":...}
    #
    # output: dict={"lung":["clear","normal"],
    #               "...": []}
    out_dict = dict.fromkeys(input_dict, [])
    for key,ls in input_dict.items():
        obser_ls = []  # value for output like ["clear","normal"]
        for l in ls:
            obser_ls.append(l[0])
        # distinct output
        #obser_ls = list(set(obser_ls))
        out_dict[key] = obser_ls

    return out_dict

def create_dict_from_dict(dic):
    outdic = dic.copy()
    for key,ls in dic.items():
        outdic[key] = []
    # if cant find the key
    return outdic

def mapping_observations(mapping_observation,dic):
    #output:
    #   dict{"lung":[normal,effusion],
    #              "...":[...]}
    out_dict = create_dict_from_dict(dic)

    for key, ls in dic.items():  #ls = ["effusions","effusion"]
        for l in ls:
            after_mapping = mapping_name(mapping_observation, l)
            if after_mapping != None: #this oberservation exists in mapping dict
                out_dict[key].append(after_mapping)

    return out_dict

def gen_init_dict_for_each_report(ref_dict,mask = False):
    ###generate the initial version of dict for each report

    output = ref_dict.copy()
    for key,ls in output.items():
        inner_dic = output[key]
        for key1, ls1 in inner_dic.items():
            for i in range(len(ls1)):
                if mask:
                    ls1[i]=0
                else:
                    if ls1[i] == "clear" or ls1[i] == "normal":
                        ls1[i] = 1
                    else:
                        ls1[i]=0
    # if cant find the key
    return output




mapping = {"lung":["lung","pulmonary","lungs","midlung","subpulmonic"],
           "pleural":["pleural","plerual"],
            "heart":["heart","cardiac","retrocardiac"],
           "mediastinum":["mediastinal","cardiomediastinal","mediastinum"],
           "lobe":["lobe","lobar","lobes"],
            "hilar":["hilar","hila","hilus","perihilar","suprahilar"],
           "vascular":["vascular","coronary",'internal jugular',"intravascular","vasculature","bronchovascular","venous","aortic","vein","arteries","vasculatiry","aorta","artery","vessel","vessels", "vascularity", "superior vena cava", "jugular"],
           "chest":["chest","thorax","pectus", "intrathoracic","hemithorax"],
           "cardiopulmonary":["cardiopulmonary"],
           "basilar":["bibasilar","basilar","base","bibasal","basal","bases"],
           "diaphragm":["hemidiaphragm","diaphragm","hemidiaphragms","diaphragms"],
           "rib":["rib","ribs", "ribcage", "costophrenic"],
           "stomach":["stomach","gastric"],
           "spine":["spine","vertebral","spinal","paraspinal","t 12 vertebral","thoracolumbar"],
           "carina":["carina"],
           "esophagus":["esophagus"],
           "apex":["apex"],
           "osseous":["osseous"],
           "esophagogastric":["esophagogastric","gastroesophageal"],
           "bony":["bony","bones","skeletal"],
           "quadrant":["quadrant"],
           "sternal":["sternal","thoracic"],
           "svc":["svc"],
           "subclavian":["subclavian","clavicle"],
           "atrium":["atrium"],
           "valve":["valve"],
           "pericardial":["pericardial"],
           "skin":["skin","cutaneous"],
           "airway":["airway","airspace"],
           "institial":["institial"],
           "interstitial":["interstitial"],
           "parenchymal":["parenchymal"],
           "line":["line", "lines"],
           "fissure":["fissure"],
           "junction":["junction", "cavoatrial junction"],
           "lingular":["lingular","lingula"],
           "valvular":["valvular"],
           "infrahilar":["infrahilar"],
           "biapical":["biapical"],
           "neck":["neck"],
           "apical":["apical"],
           "paratracheal":["paratracheal", "trachea","peribronchial","bronchial"],
           "thyroid":["thyroid"],
           "ge":["ge"],
           "axillary":["axillary","axilla"],
           "ventricle":["ventricle","ventricular","cavoatrial","biventricular'"],
           "left arm":["left arm"],
           "scapula":["scapula"],
           "subcutaneous":["subcutaneous", "subcutaneus"],
           "soft tissues":["soft tissues", "soft tissue"],
           "ij":["ij"],
           "sheath":["sheath"],
           "alveolar":["alveolar"],
           "pylorus":["pylorus"],
           "subsegmental":["subsegmental"],
           "lumbar":["lumbar"],
           "abdomen":["abdomen"],
           "duodenum":["duodenum"],
           "fundus":["fundus"],
           "inlet":["inlet"],
           "subdiaphragmatic":["subdiaphragmatic"],
           "cervical":["cervical"],
           "zone":["zone"],
           "volumes":["volumes"],
           "tube":["tube","tubes"],
           "bowel":["bowel"],
           "annulus":["annulus"],
           "cavitary":["cavitary"],
           "interstitium":["interstitium"],
           "cage":["cage"]
            }


############ OBSERVATION ##########
mapping_observation = {
        "effusion":["effusions","effusion"],
        "enlarged":["enlarged","large","larger","expanded","well - expanded","hyperexpansion","enlargement","increased","increase","exaggerated","widening","widened","distention","distension","increased enlarged"],
        "opacity":["opacity","opacities","opacified","opacification","obscures","obscuring","indistinct","indistinctness","haziness","not less distinct","blurring"],
        "thickening":["thickening","thickenings"],
        "drain":["drains","drain"],
        "normal":["normal","stable","unremarkable","top - normal","unchanged"],
        "clear":["clear"],
        "decrease":["decreased","lower","low","decrease"],
        "abnormal":["abnormality","abnormalities","abnormal","deformity","disease","deformities"],
        "edema":["edema"],
        "malignancy":["malignancy","malignancies","cancer"],
        "hemorrhage":["hemorrhage","hemorrahge","bleeding"],
        "congested":["congested","congestion","engorged"],
        "infection":["infectious","infection"],
        "sharpe":["shape","sharply"],
        "prominent":["prominence","prominent"],
        "consolidation": ["consolidation", "consolidations"],
        "nodules": ["nodules", "nodule"],
        "pneumonic": ["pneumonic", "pneumonia","nodular"],
        "calcifications": ["calcifications","calcified"],
        "tortuous": ["tortuous","tortuosity"],
        "atelectasis": ["atelectasis","atelectatic","atelectases"],
        "pneumothoraces": ["pneumothoraces","pneumothorace"],
        "fracture":["fractures","fracture","fractured"],
        "injury": ["injury", "injuries","trauma","traumas"]

}

mapping_subpart = {
        "lung":["lung","pulmonary","lungs","midlung","subpulmonic"],
       "pleural":["pleural","plerual"],
        "heart":["heart","cardiac","retrocardiac"],
       "mediastinum":["mediastinal","cardiomediastinal","mediastinum"],
       "lobe":["lobe","lobar","lobes"],
        "hilar":["hilar","hila","hilus","perihilar","suprahilar"],
       "vascular":["vascular","coronary",'internal jugular',"intravascular","vasculature","bronchovascular","venous","aortic","vein","arteries","vasculatiry","aorta","artery","vessel","vessels", "vascularity", "superior vena cava", "jugular"],
       "chest":["chest","thorax","pectus", "intrathoracic","hemithorax"],
       "cardiopulmonary":["cardiopulmonary"],
       "basilar":["bibasilar","basilar","base","bibasal","basal","bases"],
       "diaphragm":["hemidiaphragm","diaphragm","hemidiaphragms","diaphragms"],
       "rib":["rib","ribs", "ribcage", "costophrenic"],
       "stomach":["stomach","gastric"],
       "spine":["spine","vertebral","spinal","paraspinal","t 12 vertebral","thoracolumbar"],
       "carina":["carina"],
       "esophagus":["esophagus"],
       "apex":["apex"],
       "osseous":["osseous"],
       "esophagogastric":["esophagogastric","gastroesophageal"],
       "bony":["bony","bones","skeletal"],
       "quadrant":["quadrant"],
       "sternal":["sternal","thoracic"],
       "svc":["svc"],
       "subclavian":["subclavian","clavicle"],
       "atrium":["atrium"],
       "valve":["valve"],
       "pericardial":["pericardial"],
       "skin":["skin","cutaneous"],
       "airway":["airway","airspace"],
       "institial":["institial"],
       "interstitial":["interstitial"],
       "parenchymal":["parenchymal"],
       "line":["line", "lines"],
       "fissure":["fissure"],
       "junction":["junction", "cavoatrial junction"],
       "lingular":["lingular","lingula"],
       "valvular":["valvular"],
       "infrahilar":["infrahilar"],
       "biapical":["biapical"],
       "neck":["neck"],
       "apical":["apical"],
       "paratracheal":["paratracheal", "trachea","peribronchial","bronchial"],
       "thyroid":["thyroid"],
       "ge":["ge"],
       "axillary":["axillary","axilla"],
       "ventricle":["ventricle","ventricular","cavoatrial","biventricular'"],
       "left arm":["left arm"],
       "scapula":["scapula"],
       "subcutaneous":["subcutaneous", "subcutaneus"],
       "soft tissues":["soft tissues", "soft tissue"],
       "ij":["ij"],
       "sheath":["sheath"],
       "alveolar":["alveolar"],
       "pylorus":["pylorus"],
       "subsegmental":["subsegmental"],
       "lumbar":["lumbar"],
       "abdomen":["abdomen"],
       "duodenum":["duodenum"],
       "fundus":["fundus"],
       "inlet":["inlet"],
       "subdiaphragmatic":["subdiaphragmatic"],
       "cervical":["cervical"],
       "zone":["zone"],
       "volumes":["volumes"],
       "tube":["tube","tubes"],
       "bowel":["bowel"],
       "annulus":["annulus"],
       "cavitary":["cavitary"],
       "interstitium":["interstitium"],
       "cage":["cage"],
        "right": ["right", "right - sided", "right sided"],
        "left": ["left", "left - sided"],
        "contour": ["contour", "silhouette", "silhouettes", "contours"],
        "structure": ["structure", "structures"],
        "surface": ["surface", "surfaces"],
        "bilateral": ["bilateral", "bilaterally"],
        "base":["base", "bases"],
        "lower":["lower"],
        "mid":["mid"],
        "upper":["upper"],
        "volume": ["volume", "volumes"]
}


# ref_dict = {'lung':{'lung':['edema', 'clear', 'consolidation', 'enlarged', 'normal', 'abnormal', 'opacity', 'effusion', 'nodule', 'pneumonic', 'atelectasis'],
#             'volume':['decrease'],
#          'left':['edema', 'clear', 'consolidation', 'enlarged', 'normal', 'abnormal', 'opacity', 'effusion', 'nodule', 'pneumonic', 'atelectasis'], 'right':['edema', 'clear', 'consolidation', 'enlarged', 'normal', 'abnormal', 'opacity', 'effusion', 'nodule', 'pneumonic', 'atelectasis'], 'lower':['edema', 'clear', 'consolidation', 'enlarged', 'normal', 'abnormal', 'opacity', 'effusion', 'nodule', 'pneumonic', 'atelectasis'], 'mid':['edema', 'clear', 'consolidation', 'enlarged', 'normal', 'abnormal', 'opacity', 'effusion', 'nodule', 'pneumonic', 'atelectasis'],  'upper':['edema', 'clear', 'consolidation', 'enlarged', 'normal', 'abnormal', 'opacity', 'effusion', 'nodule', 'pneumonic', 'atelectasis'], 'vascular':['normal', 'abnormal', 'congested'], 'base':['atelectasis', 'opacity']},
#         'pleural':{'pleural':['normal', 'abnormal', 'effusion', 'thickening', 'drain'], 'right':['normal', 'abnormal', 'effusion', 'thickening', 'drain'], 'left':['normal', 'abnormal', 'effusion', 'thickening', 'drain'], 'bilateral':['normal', 'abnormal', 'effusion', 'thickening', 'drain'], 'surface':['normal', 'abnormal', 'clear', 'effusion']},
#         'heart':{'heart':['normal', 'abnormal', 'opacity', 'atelectasis', 'consolidation'],
#                  'size':['normal','abnormal','enlarged'], 'contour':['normal', 'abnormal', 'enlarged'],
#                 'left':['normal', 'abnormal', 'opacity', 'atelectasis', 'consolidation']},
#         'mediastinum':{'mediastinum':['normal', 'abnormal', 'enlarged', 'shift'],
#                        'contour':['normal', 'abnormal', 'enlarged'],
#                        'structure':['normal', 'abnormal']},
#         'vascular':{'vascular':['congested', 'calcification', 'crowding']}
# }
# ref_dict1 = {'lung':{'lung':['edema', 'clear', 'consolidation', 'enlarged', 'normal', 'abnormal', 'opacity', 'effusion', 'nodule', 'pneumonic', 'atelectasis'],
#             'volume':['decrease'],
#          'left':['edema', 'clear', 'consolidation', 'enlarged', 'normal', 'abnormal', 'opacity', 'effusion', 'nodule', 'pneumonic', 'atelectasis'], 'right':['edema', 'clear', 'consolidation', 'enlarged', 'normal', 'abnormal', 'opacity', 'effusion', 'nodule', 'pneumonic', 'atelectasis'], 'lower':['edema', 'clear', 'consolidation', 'enlarged', 'normal', 'abnormal', 'opacity', 'effusion', 'nodule', 'pneumonic', 'atelectasis'], 'mid':['edema', 'clear', 'consolidation', 'enlarged', 'normal', 'abnormal', 'opacity', 'effusion', 'nodule', 'pneumonic', 'atelectasis'],  'upper':['edema', 'clear', 'consolidation', 'enlarged', 'normal', 'abnormal', 'opacity', 'effusion', 'nodule', 'pneumonic', 'atelectasis'], 'vascular':['normal', 'abnormal', 'congested'], 'base':['atelectasis', 'opacity']},
#         'pleural':{'pleural':['normal', 'abnormal', 'effusion', 'thickening', 'drain'], 'right':['normal', 'abnormal', 'effusion', 'thickening', 'drain'], 'left':['normal', 'abnormal', 'effusion', 'thickening', 'drain'], 'bilateral':['normal', 'abnormal', 'effusion', 'thickening', 'drain'], 'surface':['normal', 'abnormal', 'clear', 'effusion']},
#         'heart':{'heart':['normal', 'abnormal', 'opacity', 'atelectasis', 'consolidation'],
#                  'size':['normal','abnormal','enlarged'], 'contour':['normal', 'abnormal', 'enlarged'],
#                 'left':['normal', 'abnormal', 'opacity', 'atelectasis', 'consolidation']},
#         'mediastinum':{'mediastinum':['normal', 'abnormal', 'enlarged', 'shift'],
#                        'contour':['normal', 'abnormal', 'enlarged'],
#                        'structure':['normal', 'abnormal']},
#         'vascular':{'vascular':['congested', 'calcification', 'crowding']}
# }


# a_file = open("organ_loc_ob.json", "r")
# ref_dict = a_file.read()
# a_file.close()
#
# a_file = open("organ_loc_ob.json", "r")
# ref_dict1 = a_file.read()
# a_file.close()

with open("organ_loc_ob.json", 'r') as f:
    ref_dict = json.load(f)
with open("organ_loc_ob.json", 'r') as f:
    ref_dict1 = json.load(f)

dataset = {}

final_dict={}

with open('D:/studium/MIML/radgraph/radgraph/train_add_sug.json', 'r') as f:
    data = json.load(f)

organs = []
observation_dict = create_dict_from_dict(mapping)

#print(observation_dict)

##########################################
########## extract the observations ######
##########################################
for key in data.keys():  # key : "p18/p18004941/s58821758.txt"
    new_dict = data[key]
    entities = new_dict['entities']
    with open("organ_loc_ob.json", 'r') as f:
        ref_dict1 = json.load(f)
    dict_each_report = gen_init_dict_for_each_report(ref_dict1)
    with open("organ_loc_ob.json", 'r') as f:
        ref_dict1 = json.load(f)
    masked_each_report = gen_init_dict_for_each_report(ref_dict1,mask=True)

    for new_key in entities.keys():
        entity = entities[new_key]     #entity can be "6":{}      "cancer"
        relations = entity['relations']
        for i in range(len(relations)):
            if relations[i][0] == "located_at":
                is_contain_modify = False
                relations_2 = entities[relations[i][1]]['relations']  #entities[relations[i][1]]  "lung"
                for j in range(len(relations_2)):
                    if relations_2[j][0] == 'modify':
                        is_contain_modify = True
                if is_contain_modify == False:
                    #  organs tokens, Upper case -> lower case
                    organ_lower_token = entities[relations[i][1]]['tokens'].lower()      #lung


                    ### modify the organ_lower_token
                    found_modify_ANAT = False
                    for new_key_3 in entities.keys():
                        entity_3 = entities[new_key_3]  ### "left"
                        relations_3 = entity_3['relations']
                        for k in range(len(relations_3)):

                            if relations_3[k][0] == "modify" and relations_3[k][1] == relations[i][1]:
                                found_modify_ANAT = True

                                #### handle with "modify" OBS
                                found_modify_OBS = False
                                for new_key_4 in entities.keys():
                                    entity_4 = entities[new_key_4]  # entity can be "6":{}    "3cm"
                                    label_4 = entity_4['label']

                                    if label_4[:3] == "OBS":
                                        relations_4 = entity_4['relations']
                                        for l in range(len(relations_4)):
                                            if relations_4[l][0] == "modify" and relations_4[l][1] == new_key: #found OBS_modify and found Organ_modify
                                                found_modify_OBS = True
                                                obs_modified = mapping_name(mapping_observation,entity["tokens"].lower()) #entity['tokens'] = 'cancer'
                                                if obs_modified == None:# if it couldnot find its name in values of OBS_mapping
                                                    obs_modified = entity["tokens"].lower()
                                                if OB_modified == False: #no ob_modified
                                                    OBS_with_modify = entity_4["tokens"].lower()  #3cm cancer
                                                else:
                                                    OBS_with_modify = entity_4["tokens"].lower() + " " + obs_modified  # 3cm cancer

                                                organ_after_mapping = mapping_name(mapping,organ_lower_token)
                                                if organ_after_mapping == None:
                                                    organ_after_mapping = organ_lower_token #lung
                                                organ_modify = entity_3['tokens'] # left
                                                organ=organ_after_mapping # lung



                                if not found_modify_OBS: # not found OBS_modify but found Organ_modify
                                    obs_modified = mapping_name(mapping_observation,entity["tokens"].lower())
                                    if obs_modified == None:  # if it couldnot find its name in values of OBS_mapping
                                        obs_modified = entity["tokens"].lower()      # cancer
                                    OBS_with_modify = obs_modified

                                    organ_after_mapping = mapping_name(mapping, organ_lower_token)
                                    if organ_after_mapping == None:
                                        organ_after_mapping = organ_lower_token  # lung
                                    organ_modify = entity_3['tokens']  # left
                                    organ = organ_after_mapping



                    if not found_modify_ANAT:  # if not found modify_organ

                        #### handle with "modify" OBS
                        found_modify_OBS = False
                        for new_key_4 in entities.keys():
                            entity_4 = entities[new_key_4]  # entity can be "6":{}    "3cm"
                            label_4 = entity_4['label']

                            if label_4[:3] == "OBS":
                                relations_4 = entity_4['relations']
                                for l in range(len(relations_4)):
                                    if relations_4[l][0] == "modify" and relations_4[l][1] == new_key:  # found OBS_modify and found Organ_modify
                                        found_modify_OBS = True
                                        obs_modified = mapping_name(mapping_observation, entity["tokens"].lower())  # entity['tokens'] = 'cancer'
                                        if obs_modified == None:  # if it couldnot find its name in values of OBS_mapping
                                            obs_modified = entity["tokens"].lower()
                                        if OB_modified == False:  # no ob_modified
                                            OBS_with_modify = entity_4["tokens"].lower()  # 3cm cancer
                                        else:
                                            OBS_with_modify = entity_4["tokens"].lower() + " " + obs_modified  # 3cm cancer

                                        organ_after_mapping = mapping_name(mapping, organ_lower_token)
                                        if organ_after_mapping == None:
                                            organ_after_mapping = organ_lower_token  # lung
                                        organ_modify = organ_after_mapping  # lung
                                        organ = organ_after_mapping  # lung

                        if not found_modify_OBS:  # not found OBS_modify nor found Organ_modify

                            obs_modified = mapping_name(mapping_observation, entity["tokens"].lower())
                            if obs_modified == None:  # if it couldnot find its name in values of OBS_mapping
                                obs_modified = entity["tokens"].lower()  # cancer
                            OBS_with_modify = obs_modified

                            organ_after_mapping = mapping_name(mapping, organ_lower_token)
                            if organ_after_mapping == None:
                                organ_after_mapping = organ_lower_token  # lung
                            organ_modify = organ_after_mapping  # lung
                            organ = organ_after_mapping  # lung


                        #organ_modify = organ_lower_token
                                #### mapping organs' name ####
                        #{organ_after_mapping:[]}
                    organ_modify_copy = organ_modify
                    organ_modify = mapping_name(mapping_subpart,organ_modify_copy)
                    if organ_modify == None:
                        organ_modify = organ_modify_copy
                    # if OBS_with_modify:
                    #     OBS_with_modify = del_space(OBS_with_modify)
                    ### add OBS_label as output, in order to make sure that a OBS present or not in a report
                    OBS_label = entity['label'][-2:]

                    #output_dict = {organ: {organ_modify.lower(): [OBS_with_modify]}}

                    dict_each_report,masked_each_report = gen_dict_for_each_report(organ,organ_modify,OBS_with_modify,OBS_label,dict_each_report,masked_each_report,ref_dict)
    dataset = gen_dataset(dataset,key,dict_each_report,masked_each_report)

write_json(dataset, 'D:/studium/MIML/radgraph/radgraph/final_dataset_train.json')
print(count)
                    #final_dict = update_dict(final_dict,output_dict)


# for key, ls in final_dict['mediastinum'].items():
#     print({key:ls})
    #print('/n')

#print(final_dict['lung'])
#print(observation_dict["lung"])

### pose-process observation_dict ###

# out_dict = filter_out_observations(observation_dict) #del DP/DA/U
# out_dict = mapping_observations(mapping_observation,out_dict)  #mapping variant observations' name into few observations
# #print(out_dict)
#
#
#
# #### print out the oberservation and its occurancy number according to organs ###
# for key, _ in out_dict.items():
#     result = Counter(out_dict[key])
#     sorted_result = sorted(result.items(), key=lambda x:x[1], reverse=True)
#     print({key:sorted_result})
    #print(sorted_result)

#print(observation_dict)# == observation_dict["lung"])
#print(out_dict["lung"])



