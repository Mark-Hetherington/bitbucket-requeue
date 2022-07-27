# bitbucket-requeue
Requeues bitbucket pipelines builds that get paused.

See https://jira.atlassian.com/browse/BCLOUD-16304

Automatically restart a pipeline for the latest commit in a branch if the latest commit is paused. I couldn't find a way to resume the paused pipeline, so this currently creates a new pipeline. Hopefully it is useful to others.

We deploy this as a cloud function, and call it periodically to keep builds moving.
