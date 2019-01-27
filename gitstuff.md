##### Add something to staging repository
    - `git add .` OR `git add -A`
        - We can also use file names, folder names, or any other valid command-line navigation method.

##### Check on the status of our changes
    - `git status`

##### Commit all staged changes
    - `git commit -m "commit message here"`

##### Push all commits to remote repostiory
    - `git push <remote> <branch>`
        - Usually this will be `git push origin master`
        - We can use the -u flag to set the default "upstream branch"
        - `git push -u origin master`
        - Each -u is unique each local branch, this also makes it the default for pull/fetch