import subprocess
import sys


def run_command(cmd_args, message):
    """
    Executes a shell command and prints a message.
    Exits if the command fails (returns a non-zero exit code).
    """
    print(f"\n--- {message} ---")
    # Use subprocess.run to execute the command.
    # We pass cmd_args as a list for robustness (avoids shell injection issues)
    # check=False allows us to handle the return code ourselves.
    result = subprocess.run(cmd_args, check=False)

    if result.returncode != 0:
        print(f"\n!!! Error: Command failed: {' '.join(cmd_args)}")
        # Exit with the command's return code to indicate failure
        sys.exit(result.returncode)


def main():
    """
    Main function to run isort, black, and flake8 sequentially.
    """
    # 1. Run isort to sort imports
    # The '.' argument tells isort to process files in the current directory and subdirectories.
    run_command(["poetry", "run", "isort", "."], "Running isort to fix import order...")

    # 2. Run black to format code
    # The '.' argument tells black to format files in the current directory and subdirectories.
    run_command(["poetry", "run", "black", "."], "Running black to format code...")

    # 3. Run flake8 to check for remaining linting issues
    # Note: flake8 primarily reports issues; it does not automatically fix them.
    # If flake8 finds issues, this command will return a non-zero exit code,
    # causing the script to exit and signal a failure.
    run_command(["poetry", "run", "flake8", "."], "Running flake8 to check for remaining issues...")

    print("\n--- All checks completed successfully! ---")
    print("Code is formatted, imports are sorted, and no major linting issues were found.")


if __name__ == "__main__":
    main()
