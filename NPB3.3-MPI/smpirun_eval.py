import os
import glob
import argparse
import subprocess

def smpirun_single(basename, app, app_size):
    workdir = "./simgrid_topo/"
    txt_filepath = os.path.join(workdir, basename + ".txt")
    print(txt_filepath)
    print(os.path.exists(txt_filepath))

    xml_filepath = os.path.join(workdir, basename + ".xml")
    print(xml_filepath)
    print(os.path.exists(xml_filepath))

    num_hosts = int(subprocess.check_output(['wc', '-l', txt_filepath]).decode().split(' ')[0])
    # print(num_hosts)

    app_name = ".".join([app.lower(), app_size.upper(), str(num_hosts)])
    app_filepath = os.path.join("./bin/", app_name)
    print(app_filepath)
    print(os.path.exists(app_filepath))

    exec_str = "smpirun --cfg=smpi/privatize_global_variables:yes -platform {0} -hostfile {1} {2} --log=chaix.threshold:verbose --log=chaix.fmt:%m%n --log=chaix.app:splitfile:1000000000:{3}/{4}_{5}_trace_%.csv".format(xml_filepath, txt_filepath, app_filepath, workdir, basename, app_name)
    print(exec_str)
    print(exec_str.split())
    # subprocess.run(["ls"])
    
    with open("{2}/{0}_{1}.log".format(basename, app_name, workdir), "w") as outf:
        subprocess.call(exec_str.split(), stdout=outf)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("basename")
    parser.add_argument("app")
    parser.add_argument("app_size")

    args = parser.parse_args()
    # print(args)

    smpirun_single(args.basename, args.app, args.app_size)
    

