from smpirun_eval import *

if __name__ == "__main__":
    basename = "crossbar_64"
    apps = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]
    app_size = "W"

    for app in apps:
        smpirun_single(basename, app, app_size)
