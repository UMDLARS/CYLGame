# Releasing a Build

Follow these steps to release a build of CYLGame.

1. Version Bump
   1. Change the version number in `CYLGame/version.py` to the version you wish to release. (Note: for bug fixes simply add one to the last number ex. `1.6.22` -> `1.6.23`)
   1. Commit this change using git and the the following message: `Version Bump` (Example command `git commit CYLGame/version.py -m "Version Bump"`)
   1. Create a tag for the version in git. (Example command `git tag v1.6.23`)
   1. Push the commit and tag to github. (Example command `git push origin master --tags`)
1. Check build
   1. **Check [https://travis-ci.org/UMDLARS/CYLGame](https://travis-ci.org/UMDLARS/CYLGame) to make sure the build passes.**
1. Compile and Upload
   1. Run `python setup.py sdist upload` to compile and upload the build to the Python Package Index (aka. the Cheese Shop).