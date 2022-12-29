import os
import shutil
import sys


def main(*args: str):
    if len(args) != 2 or not args[1].isdigit():
        print("Provide a day number pl0x, preferably two digits")
        sys.exit(1)

    day_name = args[1]
    dir = os.path.dirname(__file__)
    solution_package = f"{dir}/day{day_name}"
    if os.path.exists(solution_package):
        print(f"Directory already exists at {solution_package}")
        sys.exit(2)
    os.mkdir(solution_package)

    init_filepath = f"{solution_package}/__init__.py"
    with open(init_filepath, "w") as init_file:
        init_file.write("from .solution import alpha")

    solution_filepath = f"{solution_package}/solution.py"
    shutil.copyfile(f"{dir}/base.py", solution_filepath)

    test_filepath = f"{solution_package}/tests.py"
    with open(f"{dir}/base_test.py") as btf:
        test_file_contents = btf.read().replace("DAYNO", day_name)
    with open(test_filepath, "w") as tf:
        tf.write(test_file_contents)

    main_fp = f"{dir}/__main__.py"
    with open(main_fp) as m:
        main_contents = m.readlines()

    im_ix = next(
        index
        for index, line in enumerate(main_contents)
        if line.startswith("from solutions import")
    )
    if main_contents[im_ix].strip().endswith("("):
        im_end_ix = next(
            index
            for index, line in enumerate(main_contents[im_ix:], start=im_ix)
            if line.startswith(")")
        )
        solution_imports = main_contents[im_ix + 1 : im_end_ix]
        solution_imports.append(f"    day{day_name},\n")
        solution_imports.sort()
        main_contents[im_ix + 1 : im_end_ix] = solution_imports
    else:
        main_contents[im_ix] = main_contents[im_ix][:-1] + f", day{day_name}\n"

    sf_ix = next(
        index
        for index, line in enumerate(main_contents)
        if line.startswith("solution_functions: ")
    )
    sf_end_ix = next(
        index
        for index, line in enumerate(main_contents[sf_ix:], start=sf_ix)
        if line.startswith("}")
    )
    main_contents[
        sf_end_ix:sf_end_ix
    ] = f"    {int(day_name)}: [day{day_name}.alpha],\n"
    with open(main_fp, "w") as m:
        m.writelines(main_contents)

    print("Run solution:")
    print(f"    python -m solutions {day_name} <input_file>")
    print(
        f"Place example input in inputs/test{day_name}.txt and set the value "
        f"of EXAMPLE_SOLUTIONS in solutions/day{day_name}/tests.py"
    )
    print("Test solution on example input:")
    print(f"    python -m pytest solutions/day{day_name}")


if __name__ == "__main__":
    main(*sys.argv)
