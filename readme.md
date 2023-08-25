DORA Metrics

DORA metrics refer to the metrics developed by the DevOps Research and Assessment (DORA) organization.
These metrics help assess an organization's DevOps maturity level, identify areas for improvement, and track progress over time and provide valuable insights into the performance and health of software delivery processes.

We have four main metrics which constitute DORA metrics.

A) Deployment Frequency: The frequency of successful software releases to production - how often a team deploys code for a particular application
B) Lead time for changes: Time that passes for committed code to reach production
C) Mean time to Recover: Time it takes for a service to bounce back from failure
D) Change failover rate: The percentage of changes that were made to a code that resulted in incidents, rollback or any type of production failure

How to use this app

This is a simple flask application (run app.py) where we provide our Bitbucket (can be changed to use GitHub/GitLab) and JIRA's credentials to use their APIs to fetch certain details of code commits and ticket can calculate the four metrics based upon that.
