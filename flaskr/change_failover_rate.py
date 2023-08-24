"""
Author: Jasjit Rudra
Date: 14 May 2023
Description: The percentage of changes that were made into a code that resulted in incidents, rollbacks or any type
of production failures
"""


def change_failure(failed_changes, total_changes):
    change_fail = failed_changes / total_changes
    return change_fail
