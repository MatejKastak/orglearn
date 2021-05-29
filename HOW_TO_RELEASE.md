1. Check and update `CHANGELOG.md`
2. Bump the version in `setup.py` 
3. Stage changes `git add CHANGELOG.md setup.py`
4. Commit changes `git commit -m "Release v<NEW_VERSION>"`
5. Create tags `git tag -a v<NEW_VERSION> -m "Release v<NEW_VERSION>"`
6. Trigger the release `git push origin master --tags`
