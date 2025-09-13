import os
import sys
import random
import json

def sample_apps(folder_path, num_apps_list, num_iter):
    apps = [f[:-7] for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    
    result = {}
    for num_app in num_apps_list:
        if len(apps) < num_app:
            raise ValueError(f"Not Enough Apps!")
        result[num_app] = {}
        for i in range(num_iter):
            chosen = random.sample(apps, num_app)
            result[num_app][i] = chosen
    return result


# 示例调用
if __name__ == "__main__":
    folder = "/InteractionShield/artifact/Intermediate/apps/"
    bundle_file = "/InteractionShield/artifact/Intermediate/config/app_bundles.json"

    if len(sys.argv) < 3:
        print("Usage: python your_script_name.py <num_apps> <num_iter>")
        sys.exit(1)

    try:
        max_num_apps = int(sys.argv[1])
        num_iter = int(sys.argv[2])
    except ValueError:
        print("Error: Need Integers!")
        sys.exit(1)

    num_apps_list = list(range(5, max_num_apps + 1, 5))
    output = sample_apps(folder, num_apps_list, num_iter)

    json_s = json.dumps(output, indent=4)
    with open(bundle_file, "w", encoding="ISO-8859-1") as fpw_fp:
        fpw_fp.write(json_s)
