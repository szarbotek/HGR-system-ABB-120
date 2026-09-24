import subprocess
import sys


def main():
    module = "src.ui.gui"
    script_path = "./scripts/run.sh"

    try:
        result = subprocess.run([script_path, module], check=True)
    except FileNotFoundError:
        print(f"Cannot find file: {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"Script error: {e.returncode}")


if __name__ == "__main__":
    main()