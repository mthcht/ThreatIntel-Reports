#!/usr/bin/env python

import subprocess
import logging
import os

def setup_logging():
    logging.basicConfig(
        filename='main.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

def log(message):
    logging.info(message)
    print(message)

def run_script(command, description, max_wait_time):
    log(f"Executing {description}...")
    try:
        # Start the process
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

        # Capture and log the output line by line
        for line in process.stdout:
            log(line.strip())
        for line in process.stderr:
            log(line.strip())

        # Wait for the process to complete with a timeout
        process.wait(timeout=max_wait_time)

        # Check for errors based on exit code
        if process.returncode != 0:
            log(f"{description} encountered an error with exit code {process.returncode}.")
            return False

        log(f"{description} completed successfully.")
        return True

    except subprocess.TimeoutExpired:
        log(f"{description} exceeded the maximum allowed execution time.")
        process.kill()
        return False

def main():
    setup_logging()
    log("Starting script sequence...")

    # Define a maximum wait time (timeout) for each script (e.g., 2 hours)
    max_wait_time = 2 * 60 * 60  # 2 hours in seconds

    # Execute each script and check for successful completion
    if not run_script(['python', 'fetch_report_links.py'], "fetch_report_links.py", max_wait_time):
        log("Script sequence terminated due to an error.")
        return

    if not run_script(['python', 'download_reports.py'], "download_reports.py", max_wait_time):
        log("Script sequence terminated due to an error.")
        return

    # Go back to the previous directory
    log("Changing to the previous directory...")
    os.chdir('..')

    if not run_script(['python', 'search_keyword_ripgrep_fast.py', '--update'], "search_keyword_ripgrep_fast.py with --update flag", max_wait_time):
        log("Script sequence terminated due to an error.")
        return

    log("Script sequence completed successfully.")

if __name__ == '__main__':
    main()
