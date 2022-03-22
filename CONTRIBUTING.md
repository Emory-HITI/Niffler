# Developer Guidelines

This is a discussion page to help the developers get started soon. 


# Documentation

* Please make sure to document any user-facing changes on the respective module's README. If your change will affect how a user will use any of Niffler's modules, it should be reflected in the respective README.

* In the code, please feel free to use logs. But do not use print() as they make the management of logs difficult. Rather, use the python logging module, and use the relevant log level. For example, if your log is merely a debug log, it should be logging.debug(). If it is a log that you expect to print always, you can use logging.info(), and for warnings and errors logging.warning() and logging.error() appropriately. While logs are helpful, too many logs will overwhelm the users and prevent them from extracting any useful information. As such, debug logs that you introduce to debug your coding, should be marked as logging.debug() rather than logging.info().


# Commit logs

* Please try to write meaningful commit messages.


# Requests for Enhancement (RFE) and bugs

* Please open an issue in the [bug tracker](https://github.com/Emory-HITI/Niffler/issues) if it is not already reported there.


# Commits and pull requests

* Please develop against the [dev](https://github.com/Emory-HITI/Niffler/tree/dev) branch. New contributors are encouraged to submit pull requests, rather than directly committing even when you have committer access. Another developer can then review and merge your pull request.

* The pull request should be minimal. Avoid including irrelevant changes in your pull request -- for example, unused library imports, line break changes, adding/removing new lines that interpret an unchanged code segment as changed. Inclusion of irrelevant changes in your pull request dilutes your actual contribution, and make it hard for the developers to merge and review. Please check with a "git diff" before committing your changes, to avoid such additions. 

* Some important requests for enhancements are tracked in the [bug tracker](https://github.com/Emory-HITI/Niffler/issues).

