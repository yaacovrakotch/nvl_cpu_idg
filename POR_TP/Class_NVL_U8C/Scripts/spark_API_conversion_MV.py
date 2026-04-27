import os
import sys
import subprocess

def create_VPO_submission_file(BaseTP,STPL,PLIST,tp_branch,VPO_description_path):

    #Getting stplDirectory
    output = subprocess.check_output(['net', 'use', 'I:'], shell=True)
    output_lines = output.decode('utf-8').split('\n')
    pg_flag = False
    for line in output_lines:
        if 'Remote name' in line:
            if 'jf' in line:
                print('JF Drive is mapped')
                if 'I:/' in BaseTP:
                    BaseTP = BaseTP.replace('I:/','\\\\\\\\amr.corp.intel.com\\\\ec\\\\proj\\\\mdl\\\\jf\\\\intel\\\\')
                    BaseTP = BaseTP.replace('/','\\\\')
            if 'pg' in line:
                print('PG Drive is mapped')
                pg_flag = True
                if 'I:/' in BaseTP:
                    BaseTP = BaseTP.replace('I:/','\\\\\\\\gar.corp.intel.com\\\\ec\\\\proj\\\\mdl\\\\pg\\\\intel\\\\')
                    BaseTP = BaseTP.replace('/','\\\\')
    
    path_stpl = STPL.split('/')[0] + '\\\\' + STPL.split('/')[1]
    stplDirectory = BaseTP + '\\\\' + path_stpl
    print(stplDirectory)
    
    #tp_branch process
    VPO_name = tp_branch.replace('/','_')
    if 'refs_' in VPO_name:
        VPO_name = VPO_name.replace('refs_','')
    if 'heads_' in VPO_name:
        VPO_name = VPO_name.replace('heads_','')
    
    print(f"VPO_name: {VPO_name}")
    
    # Reading the input file
    with open(VPO_description_path, 'r') as f:
        f_lines = f.readlines()
        for line in f_lines:
            if 'SourceLot:' in line:
                lot = line.split(':')[1].strip()
                print(f'SourceLot: {lot}')
            elif 'Number of Units to run:' in line:
                numOfUnitsToRun = line.split(':')[1].strip()
                print(f'Number of Units to run: {numOfUnitsToRun}')
            elif 'Stepping:' in line:
                step = line.split(':')[1].strip()
                print(f'Stepping: {step}')
            elif 'Location:' in line:
                locn = line.split(':')[1].strip()
                print(f'Location: {locn}')
            elif 'EngID:' in line:
                engid = line.split(':')[1].strip()
                print(f'EngID: {engid}')
            elif 'TAG:' in line:
                tags = line.split(':')[1].strip()
                print(f'TAG: {tags}')
            elif 'Special Instruction:' in line:
                specialInstructions = line.split(':')[1].strip()
                print(f'Special Instruction: {specialInstructions}')
            elif 'Contact:' in line:
                contact = line.split(':')[1].strip()
                print(f'Contact: {contact}')
            elif '====Instruction Guides====' in line:
                break

    #Getting bomGroupName
    bomGroupName = STPL.split('/')[2].split('_')[1] + '_' + STPL.split('/')[2].split('_')[2]
    print(f"bomGroupName: {bomGroupName}")


    #stplFileName
    stplFileName = STPL.split('/')[2]

    #Getting PLISTFileName
    PLISTFileName = PLIST.split('/')[2]

    print("Start writing the submission_vpo.json file...")

    submission_file = "C:/Temp/submission_vpo.json"

    if (os.path.exists(submission_file)):
        print("Remove old vpo submission file...")
        os.remove(submission_file)

    f = open("C:/Temp/submission_vpo.json","w")

    f.write("{\n")
    if (pg_flag):
        f.write(f"  \"segment\": \"DDG CLIENT\",\n")
        f.write(f"  \"team\": \"DDG CLIENT X10\",\n")
    else:
        f.write(f"  \"segment\": \"DDG\",\n")
        f.write(f"  \"team\": \"SORT CLASS TPI 1\",\n")
    f.write(f"  \"displayName\": \"{VPO_name}\",\n")  
    f.write(f"  \"stplDirectory\": \"{stplDirectory}\",\n")
    f.write("  \"" + "experiments" + "\": [\n")
    f.write("\t" + "{" + "\n")
    f.write(f"\t  \"displayName\": \"{VPO_name}\",\n")
    f.write(f"\t  \"experimentType\": \"Engineering\",\n")
    f.write(f"\t  \"activityType\": \"ModuleValidation\",\n")
    f.write(f"\t  \"bomGroupName\": \"{bomGroupName}\",\n")
    f.write(f"\t  \"step\": \"{step}\",\n")
    f.write(f"\t  \"tplFileName\": \"..\\\\..\\\\BaseTestPlan.tpl\",\n")
    f.write(f"\t  \"stplFileName\": \"{stplFileName}\",\n")
    f.write(f"\t  \"environmentFileName\": \"EnvironmentFile.env\",\n")
    f.write(f"\t  \"plistAllFileName\": \"{PLISTFileName}\",\n")
    f.write(f"\t  \"testTimeInSecPerUnit\": 200,\n")
    f.write(f"\t  \"retestRate\": 30,\n")
    if (pg_flag):
        f.write(f"\t  \"lab\": \"PNG\",\n")
    else:
        f.write(f"\t  \"lab\": \"ORVC\",\n")
    f.write("\t  " + "\"material\"" + ": " + "{\n")
    f.write("\t    " + "\"materialIssue\"" + ": " + "{\n")
    f.write("\t      " + "\"materialIssueIsRequired\"" + ": "  + "false" + "\n")
    f.write("\t    },\n")
    f.write("\t    " + "\"lots\"" + ": " + "[\n")
    f.write("\t      " + "{\n")
    if numOfUnitsToRun != '0':
        f.write(f"\t        \"name\": \"{lot}\",\n")
        f.write(f"\t        \"numOfUnitsToRun\": {numOfUnitsToRun}\n")
    else:
        f.write(f"\t        \"name\": \"{lot}\"\n")
    f.write("\t      " + "}\n")
    f.write("\t    " + "]\n")
    f.write("\t  " + "},\n")
    f.write("\t  " + "\"conditions\"" + ": " + "[\n")
    
    if '/' in locn:
        numOfOps = locn.count('/') + 1
    else:
        numOfOps = 1
    
    if '/' in engid:
        numOfEng = engid.count('/') + 1
    else:
        numOfEng = 1
    
    if (numOfOps != numOfEng):
        print(f"numOfOps({numOfOps}) is different than numOfEng({numOfEng}). They must be equal.")
        f.close()
        exit(1)
    
    for k in range (0,numOfOps):
        f.write("\t    " + "{\n")
        f.write("\t      " + "\"operation\"" + ": " + "\"" + locn.strip().split('/')[k] + "\",\n")
        f.write("\t      " + "\"engineeringId\"" + ": " + "\"" + engid.strip().split('/')[k] + "\",\n")
        f.write("\t      " + "\"dieSelection\"" + ": " + "\"" + "NA" + "\",\n")
        f.write("\t      " + "\"comment\"" + ": " + f"\"{specialInstructions}\",\n")
        f.write("\t      " + "\"moveUnits\"" + ": " + "\"" + "Good" + "\"\n")
        if (k+1 != numOfOps):
            f.write("\t    " + "},\n")
        else:
            f.write("\t    " + "}\n")
    f.write("\t  " + "],\n")
    f.write("\t  " + "\"flexbom\"" + ": " + "{\n")
    f.write("\t    " + "\"hri\"" + ": " + "\"" + "DEFAULT_HRI" + "\",\n")
    f.write("\t    " + "\"mrv\"" + ": " + "\"" + "000000000000" + "\"\n")
    f.write("\t  " + "},\n")
    f.write("\t  " + "\"experimentState\"" + ": " + "\"" + "Ready" + "\",\n")
    if (tags == 'BOT'):
        tags = ''
    f.write("\t  " + "\"tags\"" + ": [" + "\"BOT_" + tags + "\"],\n")
    f.write("\t  " + "\"ContactEmails\"" + ": " + f"[\"{contact}\"],\n")
    f.write("\t  " + "\"recipe\"" + ": " + "{\n")
    f.write("\t    " + "\"recipeSource\"" + ": " + "\"" + "TpGenerated" + "\"\n")
    f.write("\t  " + "}\n")
    f.write("\t" + "}\n")
    f.write("  " + "]\n")
    f.write("}")

    print("submission_vpo.json is successfully created.")        
    f.close()


def main():

    BaseTP = sys.argv[1]
    STPL = sys.argv[2]
    PLIST = sys.argv[3]
    tp_branch = sys.argv[4]
    VPO_description_path = sys.argv[5]
    
    # BaseTP = 'I:/engineering/dev/team_classtp/torch/tp_rolling/mrobot_P68C0/62'
    # STPL = 'POR_TP/Class_MTL_P68/SubTestPlan_CLASS_P68G2_g.stpl'
    # PLIST = 'POR_TP/Class_MTL_P68/PLIST_ALL_CLASS_P68G2.plist.xml'
    # tp_branch = 'refs/heads/tai/testing_GH_action'
    # VPO_description_path = 'I:/engineering/dev/sctp/users/taipham/SPARK_API/VPO_Description.txt'
    
    create_VPO_submission_file(BaseTP,STPL,PLIST,tp_branch,VPO_description_path)

if __name__ == "__main__":
    main()