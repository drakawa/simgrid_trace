import os
import glob
dirname = "./simgrid_topo"
xmls = glob.glob(os.path.join(dirname, "*.xml"))
# print(xmls)
# print(len(xmls))

txts = [xml.replace(".xml", ".txt") for xml in xmls]
bases = [xml.replace(".xml", "") for xml in xmls]
# print(txts)
# print(bases)

npb_params = list()
for line in open("./config/suite.def", "r"):
    l = line.strip().split()
    # print(line.split())
    if len(l) > 0 and l[0][0] != "#":
        # print(l)
        npb_params.append(l)
        
#print(len(npb_params))
#print(npb_params)
#exit(1)

a_exclude = ["dt"]
# print(bases)
# exit(1)
# print("# smpirun --cfg=smpi/privatize_global_variables:yes -platform torus_4_4.edges_4.xml -hostfile torus_4_4.edges_4.txt bin/cg.A.1024 > smpirun13.log &")
for a, s, n in npb_params:
    for b in bases:
        if a not in a_exclude:
            # print(b, a, s, n)
            print("smpirun --cfg=smpi/privatize_global_variables:yes -platform {0}.xml -hostfile {0}.txt bin/{1}.{2}.{3} > {0}_{1}_{2}_{3}.log".format(b, a, s, n))
        # exit(1)
# smpirun --cfg=smpi/privatize_global_variables:yes -platform torus_4_4.edges_4.xml -hostfile torus_4_4.edges_4.txt bin/cg.A.1024 > smpirun13.log &
