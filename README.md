To save storage regularly clear the history... 

```bash 
git checkout --orphan newBranch
git add -A  
git commit
git branch -D main
git branch -m main
git push -f origin main
git gc --aggressive --prune=all  
```

