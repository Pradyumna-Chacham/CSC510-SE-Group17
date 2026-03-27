
[fork]: https://github.com/Shorse321/CSC510Group24/fork
[pr]: https://github.com/Shorse321/CSC510Group24/compare
[code-of-conduct]: CODE_OF_CONDUCT.md
[install-guide]: INSTALL.md
[pep8]: https://peps.python.org/pep-0008/

# 🍔 Contributing to StackShack

Hi there! We're thrilled that you'd like to contribute to this project. Your help is essential for keeping it great.

Please note that this project is released with a [Contributor Code of Conduct][code-of-conduct]. By participating in this project you agree to abide by its terms.

## Issues and PRs

If you have suggestions for how this project could be improved, or want to report a bug, open an issue! We'd love all and any contributions. If you have questions, too, we'd love to hear them @ https://discord.gg/R9bttnvf

We'd also love PRs. If you're thinking of a large pull request (PR), we advise opening up an issue first to talk about it, though!

## Submitting a Pull Request

1.  **[Fork][fork] and clone the repository.**
2.  **Follow the [Installation Guide][install-guide]** to set up your virtual environment, install dependencies, and configure your local database.
3.  **Make sure the tests pass on your machine.** From the `proj2/stackshack/` directory, run:
    ```bash
    # On macOS/Linux
    PYTHONPATH=. pytest tests/
    
    # On Windows (PowerShell)
    $env:PYTHONPATH="."; pytest tests/
    ```
4.  **Create a new branch:** `git checkout -b my-branch-name`.
5.  **Make your change, add tests,** and make sure the tests still pass with your changes.
6.  **Push to your fork** and [submit a pull request][pr].
7.  Pat yourself on the back and wait for your pull request to be reviewed and merged!

Here are a few things you can do that will increase the likelihood of your pull request being accepted:

* **Follow Python style conventions.** We follow [PEP 8][pep8] for all Python code.
* **Write and update tests.** We have a robust test suite. Any new features must be accompanied by new tests, and bug fixes should include a test that proves the fix.
* **Keep your changes focused.** If there are multiple changes you would like to make that are not dependent upon each other, please submit them as separate pull requests.
* **Write good commit messages.**

Work-in-progress pull requests are also welcome to get feedback early on, or if you are blocked on something.

## Resources

* [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
* [Using Pull Requests](https://help.github.com/articles/about-pull-requests/)
* [GitHub Help](https://help.github.com)
