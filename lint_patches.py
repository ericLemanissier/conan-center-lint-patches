import sys
import copy
import os
from yaml import safe_load


def main(path: str) -> int:
    with open(path, encoding="utf-8") as file:
        content = file.read()

    parsed = safe_load(content)

    patches_path = os.path.join(os.path.dirname(path), "patches")
    actual_patches: list[str] = []
    if os.path.isdir(patches_path):
        actual_patches.extend(
            os.path.join(root[len(patches_path) + 1:], f)
            for root, _, files in os.walk(patches_path) for f in files)
    unused_patches = copy.copy(actual_patches)
    for version in parsed.get("patches", []):
        patches = parsed["patches"][version]
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
                print(f"patches should be located in [patches](https://github.com/conan-io/conan-center-index/tree/master/recipes/{patches_path}) subfolder, not in {patch_file_name}")
            else:
                patch_file_name = patch_file_name[8:]
                if patch_file_name in unused_patches:
                    unused_patches.remove(patch_file_name)
                if patch_file_name not in actual_patches:
                    print(f"The file `{patch_file_name}` does not exist in the [`patches` folder](https://github.com/conan-io/conan-center-index/tree/master/recipes/{patches_path})")

    if unused_patches:
        print(f"Following patch files are not referenced in [{path}](https://github.com/conan-io/conan-center-index/tree/master/recipes/{path})")
        for patch in unused_patches:
            print(f"- [{patch}](https://github.com/conan-io/conan-center-index/tree/master/recipes/{patches_path}/{patch})")
        print("\n")
    return 0


if __name__ == "__main__":
    main(sys.argv[1])
