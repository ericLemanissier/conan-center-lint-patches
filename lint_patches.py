# /// script
# dependencies = [
#   "pyyaml==6.0.3",
# ]
# ///

import ast
import sys
import copy
import os
from yaml import safe_load


def check_if_patches_are_exported_and_applied(path: str):
    conandata_path = os.path.join(path, "conandata.yml")
    conanfile_path = os.path.join(path, "conanfile.py")
    with open(conanfile_path, encoding='utf-8') as file:
        recipe_lines = file.readlines()
    source = "".join(recipe_lines)

    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "apply_conandata_patches":
                break
            if isinstance(func, ast.Attribute):
                if func.attr == "apply_conandata_patches":
                    break
                if isinstance(func.value, ast.Name) and func.value.id == "tools" and func.attr == "patch":
                    break
    else:
        patches_are_exported = any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "export_conandata_patches" for node in ast.walk(tree))
        if not patches_are_exported:
            print(f"Patches are listed in [{conandata_path}](https://github.com/ericLemanissier/cocorepo/tree/HEAD/recipes/{conandata_path})"
                  f" but not exported in [{conanfile_path}](https://github.com/ericLemanissier/cocorepo/tree/HEAD/recipes/{conanfile_path})\n")

        print(f"Patches are listed in [{conandata_path}](https://github.com/ericLemanissier/cocorepo/tree/HEAD/recipes/{conandata_path})"
              f" but not applied in [{conanfile_path}](https://github.com/ericLemanissier/cocorepo/tree/HEAD/recipes/{conanfile_path})\n")


def main(path: str) -> int:  # noqa: MC0001  pylint: disable=too-many-branches
    conandata_path = os.path.join(path, "conandata.yml")
    if os.path.isfile(conandata_path):
        with open(conandata_path, encoding="utf-8") as file:
            parsed = safe_load(file.read())
    else:
        parsed = {}

    patches_path = os.path.join(path, "patches")
    actual_patches: list[str] = []
    if os.path.isdir(patches_path):
        actual_patches.extend(
            os.path.join(root[len(patches_path) + 1:], f)
            for root, _, files in os.walk(patches_path) for f in files)
    actual_patches.sort()
    unused_patches = copy.copy(actual_patches)
    for version, patches in parsed.get("patches", {}).items():
        if version not in parsed["sources"]:
            print(
                f"Patch(es) are listed for version `{version}`,"
                f" but there is source for this version."
                f" You should either remove `{version}` from the `patches` section,"
                f" or add it to the `sources` section"
            )
        for _, patch in enumerate(patches):
            patch_file_name = str(patch["patch_file"])
            if not patch_file_name.startswith("patches/"):
                print(f"patches should be located in [patches](https://github.com/ericLemanissier/cocorepo/tree/HEAD/recipes/{patches_path}) subfolder, not in {patch_file_name}")
            else:
                patch_file_name = os.path.relpath(patch_file_name)  # fixes the path (double slashes for example)
                patch_file_name = patch_file_name[8:]
                if patch_file_name in unused_patches:
                    unused_patches.remove(patch_file_name)
                if patch_file_name not in actual_patches:
                    print(f"The file `{patch_file_name}` does not exist in the [`patches` folder](https://github.com/ericLemanissier/cocorepo/tree/HEAD/recipes/{patches_path})")

    if any(parsed.get("patches", {})):
        check_if_patches_are_exported_and_applied(path)

    if unused_patches:
        print(f"Following patch files are not referenced in [{conandata_path}](https://github.com/ericLemanissier/cocorepo/tree/HEAD/recipes/{conandata_path})")
        for patch in unused_patches:
            print(f"- [{patch}](https://github.com/ericLemanissier/cocorepo/tree/HEAD/recipes/{patches_path}/{patch})")
        print("\n")
    return 0


if __name__ == "__main__":
    main(sys.argv[1])
