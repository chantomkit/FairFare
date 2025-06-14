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
    # capture_output=True to suppress direct output of pre-commit
    # and then print it if there's an error.
    # text=True decodes stdout/stderr as text.
    result = subprocess.run(cmd_args, capture_output=True, text=True, check=False)

    # Print stdout and stderr for better debugging, regardless of success.
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print(f"\n!!! Error: Command failed: {' '.join(cmd_args)}")
        # Exit with the command's return code to indicate failure
        sys.exit(result.returncode)


def main():
    """
    Main function to run isort, black, pre-commit fixers, and flake8 sequentially.
    """
    # 1. Run isort to sort imports
    # The '.' argument tells isort to process files in the current directory and subdirectories.
    run_command(["poetry", "run", "isort", "."], "Running isort to fix import order...")

    # 2. Run black to format code
    # The '.' argument tells black to format files in the current directory and subdirectories.
    run_command(["poetry", "run", "black", "."], "Running black to format code...")

    # 3. Run pre-commit hooks for trailing whitespace and end-of-file
    # Changed from --hook-id to passing the hook_id as a positional argument,
    # which is the standard way to run specific pre-commit hooks.
    run_command(
        ["poetry", "run", "pre-commit", "run", "trailing-whitespace", "--all-files"], "Fixing trailing whitespace..."
    )
    run_command(
        ["poetry", "run", "pre-commit", "run", "end-of-file-fixer", "--all-files"],
        "Ensuring consistent end-of-file newlines...",
    )

    # 4. Run flake8 to check for remaining linting issues
    # Note: flake8 primarily reports issues; it does not automatically fix them.
    # If flake8 finds issues, this command will return a non-zero exit code,
    # causing the script to exit and signal a failure.
    run_command(["poetry", "run", "flake8", "."], "Running flake8 to check for remaining issues...")

    print("\n--- All code quality checks and fixes completed successfully! ---")
    print("Code is formatted, imports are sorted, basic file issues fixed, and no major linting problems were found.")


if __name__ == "__main__":
    main()
