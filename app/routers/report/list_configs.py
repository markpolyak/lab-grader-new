import os

def list_configs():
    directory = "courses"
    print(os.listdir(directory))

    yml_files = [f[:-5] for f in os.listdir(directory) if f.endswith('.yaml')]

    return {"files": yml_files}
