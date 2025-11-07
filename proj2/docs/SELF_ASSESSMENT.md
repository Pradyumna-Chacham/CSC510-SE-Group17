# 📊 Software Sustainability Evaluation - Self Assessment

### Software Sustainability Evaluation self-assessment table (project2 only):

| Category                         | Question                                                                                                                                                                                                                                                                                                                      | Yes | No | Evidence |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- | -- | -------- |
| *Q1 - Software Overview*       |  |  |   |   |
|Question 1.1| Does your website and documentation provide a clear, high-level overview of your software?| ✅   | ❌  | See [README.md](../README.md) "Project Overview" section |
|Question 1.2| Does your website and documentation clearly describe the type of user who should use your software?| ✅   | ❌  | See [README.md](../README.md) "Intended Users"  section|
|Question 1.3| Do you publish case studies to show how your software has been used by yourself and others?| ✅   | ❌  | See [README.md](../README.md) "Use Case Examples" section |
| *Q2 - Identity*                | |  |   |   |
|Question 2.1| Is the name of your project/software unique?| ✅   | ❌  | "ReqEngine" is a unique name |
|Question 2.2| Is your project/software name free from trademark violations?| ✅   | ❌  | Preliminary searches show no trademark violations |
| *Q3 - Availability*            | |  |   |   |
|Question 3.1| Is your software available as a package that can be deployed without building it?| ❌   | ✅  | Currently requires building from source - could add Docker deployment |
|Question 3.2| Is your software available for free?| ✅   | ❌  | Software is freely available on GitHub |
|Question 3.3| Is your source code publicly available to download, either as a downloadable bundle or via access to a source code repository?| ✅   | ❌  | Source code is available in GitHub repository |
| Question 3.4 | Is your software hosted in an established, third-party repository like [GitHub](https://github.com), [BitBucket](https://bitbucket.org), [LaunchPad](https://launchpad.net), or [SourceForge](https://sourceforge.net)? | ✅ | ❌ | Software is hosted by GitHub |
| *Q4 - Documentation*           | |  |   |   |
|Question 4.1| Is your documentation clearly available on your website or within your software?| ✅   | ❌  | See [README.md](../README.md) "Documentation" section |
|Question 4.2| Does your documentation include a "quick start" guide, that provides a short overview of how to use your software with some basic examples of use?| ✅   | ❌  | See [docs/SETUP.md](SETUP.md) section |
|Question 4.3| If you provide more extensive documentation, does this provide clear, step-by-step instructions on how to deploy and use your software?| ✅   | ❌  | See [README.md](../README.md) "Installation and Setup" section |
|Question 4.4| Do you provide a comprehensive guide to all your software's commands, functions and options?| ✅   | ❌  | See [docs/INSTALL.md](INSTALL.md) section |
|Question 4.5| Do you provide troubleshooting information that describes the symptoms and step-by-step solutions for problems and error messages?| ✅   | ❌  | See [README.md](../README.md) "Throubleshooting" section ,[docs/INSTALL.md](INSTALL.md) "Running Tests" and [docs/CONTRIBUTING.md](CONTRIBUTING.md) "Troubleshooting" sections |
|Question 4.6| If your software can be used as a library, package or service by other software, do you provide comprehensive API documentation?| ✅   | ❌  | See [docs/API.md](API.md) and [README.md](../README.md) "API Integration" section |
|Question 4.7| Do you store your documentation under revision control with your source code?| ✅   | ❌  | All documents are stored in docs/ folder and are in revision control with the source code |
|Question 4.8| Do you publish your release history e.g. release data, version numbers, key features of each release etc. on your web site or in your documentation?| ✅   | ❌  | See [README.md](../README.md) and [docs/CHANGELOG.md](CHANGELOG.md) |
| *Q5 - Support*                 | |  |   |   |
|Question 5.1| Does your software describe how a user can get help with using your software?| ✅   | ❌  | See [docs/CONTRIBUTING.md](CONTRIBUTING.md) and [README.md](../README.md) "Contributing" section |
|Question 5.2| Does your website and documentation describe what support, if any, you provide to users and developers?| ✅   | ❌  | See [docs/CONTRIBUTING.md](CONTRIBUTING.md) "Contributing to ReqEngine" section |
|Question 5.3| Does your project have an e-mail address or forum that is solely for supporting users?| ✅   | ❌  | See [README.md](../README.md) "Support" section |
|Question 5.4| Are e-mails to your support e-mail address received by more than one person?| ✅   | ❌  | GitHub Issues are visible to all project maintainers |
|Question 5.5| Does your project have a ticketing system to manage bug reports and feature requests?| ✅   | ❌  | See [Git Issues](https://github.com/Pradyumna-Chacham/CSC510-SE-Group17/issues) |
|Question 5.6| Is your project's ticketing system publicly visible to your users, so they can view bug reports and feature requests?| ✅   | ❌  | See [Git Issues](https://github.com/Pradyumna-Chacham/CSC510-SE-Group17/issues) |
| *Q6 - Maintainability*         | |  |   |   |
|Question 6.1| Is your software's architecture and design modular?| ✅   | ❌  | See [README.md](../README.md) "Project Structure" - modular FastAPI backend and React frontend |
|Question 6.2| Does your software use an accepted coding standard or convention?| ✅   | ❌  | Python PEP8, ESLint for JavaScript, see [docs/CONTRIBUTING.md](CONTRIBUTING.md) |
| *Q7 - Open Standards*          | |  |   |   |
|Question 7.1| Does your software allow data to be imported and exported using open data formats?| ✅   | ❌  | See [README.md](../README.md) "Key Features" section. Supports PDF, DOCX, TXT, Markdown input; exports to DOCX, Markdown |
|Question 7.2| Does your software allow communications using open communications protocols?| ✅   | ❌  | See [README.md](../README.md). Uses HTTP/REST API, standard JSON format |
| *Q8 - Portability*             | |  |   |   |
|Question 8.1| Is your software cross-platform compatible?| ✅   | ❌  |See [docs/SETUP.md](SETUP.md)  Python and Node.js are cross-platform (Windows, macOS, Linux) |
| *Q9 - Accessibility*           | |  |   |   |
|Question 9.1| Does your software adhere to appropriate accessibility conventions or standards?| ✅   | ❌  | See [frontend/README.md](../frontend/README.md) .Frontend with TailwindCSS and React follows the standards. |
|Question 9.2| Does your documentation adhere to appropriate accessibility conventions or standards?| ✅   | ❌  | Markdown documentation is screen-reader friendly |
| *Q10 - Source Code Management* | |  |   |   |
|Question 10.1| Is your source code stored in a repository under revision control?| ✅   | ❌  | GitHub repository with full Git version control |
|Question 10.2| Is each source code release a snapshot of the repository?| ✅   | ❌  | Git commits provide snapshots of each release |
|Question 10.3| Are releases tagged in the repository?| ✅   | ❌  | Git tags are present for version releases |
|Question 10.4| Is there a branch of the repository that is always stable? (i.e. tests always pass, code always builds successfully)| ✅   | ❌  | Main branch maintained as stable with testing |
|Question 10.5| Do you back-up your repository?| ✅   | ❌  | GitHub provides automatic backup and redundancy |
| *Q11 - Building & Installing*  | |  |   |   |
|Question 11.1| Do you provide publicly-available instructions for building your software from the source code?| ✅   | ❌  | See [docs/INSTALL.md](INSTALL.md) and [README.md](../README.md) "Installation and Setup" |
|Question 11.2| Can you build, or package, your software using an automated tool?| ✅   | ❌  | npm build for frontend, pip install for backend |
|Question 11.3| Do you provide publicly-available instructions for deploying your software?| ✅   | ❌  | See [docs/INSTALL.md](INSTALL.md) "Running the Application" section |
|Question 11.4| Does your documentation list all third-party dependencies?| ✅   | ❌  | See requirements.txt (backend) and package.json (frontend) |
|Question 11.5| Does your documentation list the version number for all third-party dependencies?| ✅   | ❌  | Version numbers specified in requirements.txt and package.json |
|Question 11.6| Does your software list the web address, and licences for all third-party dependencies and say whether the dependencies are mandatory or optional?| ❌   | ✅  | Dependencies listed but not with individual licenses and web addresses |
|Question 11.7| Can you download dependencies using a dependency management tool or package manager?| ✅   | ❌  | pip for Python dependencies, npm for Node.js dependencies |
|Question 11.8| Do you have tests that can be run after your software has been built or deployed to show whether the build or deployment has been successful?| ✅   | ❌  | See [docs/INSTALL.md](INSTALL.md) "Running Tests" section |
| *Q12 - Testing*                | |  |   |   |
|Question 12.1| Do you have an automated test suite for your software?| ✅   | ❌  | See backend/tests/ and frontend/src/pages/_tests_ See [README.md](../README.md) "Testing" section - 90+ backend tests, 100+ frontend tests |
|Question 12.2| Do you have a framework to periodically (e.g. nightly) run your tests on the latest version of the source code?| ❌   | ✅  | Manual testing currently - could implement CI/CD for automated runs |
|Question 12.3| Do you use continuous integration, automatically running tests whenever changes are made to your source code?| ❌   | ✅  | Tests available but CI/CD pipeline not yet implemented |
|Question 12.4| Are your test results publicly visible?| ✅   | ❌  | Test coverage badges in [README.md](../README.md) show 85% backend, 82% frontend coverage |
|Question 12.5| Are all manually-run tests documented?| ✅   | ❌  | See [docs/INSTALL.md](INSTALL.md) "Running Tests" and [docs/CONTRIBUTING.md](CONTRIBUTING.md) "Testing Guidelines" |
| *Q13 - Community Engagement*   |  |  |   |   |                                                                                                                                                                                           
|Question 13.1| Does your project have resources (e.g. blog, Twitter, RSS feed, Facebook page, wiki, mailing list) that are regularly updated with information about your software?| ❌   | ✅  | Currently no social media presence - GitHub repository serves as main resource |
|Question 13.2| Does your website state how many projects and users are associated with your project?| ❌   | ✅  | See [docs/CHANGELOG.md](CHANGELOG.md) "Contributors" section |
|Question 13.3| Do you provide success stories on your website?| ✅   | ❌  | See [README.md](../README.md) "Use Case Examples" section demonstrates usage |
|Question 13.4| Do you list your important partners and collaborators on your website?| ❌   | ✅  | Project contributors listed in GitHub, See [docs/CHANGELOG.md](CHANGELOG.md) "Contributors" section |
|Question 13.5| Do you list your project's publications on your website or link to a resource where these are available? | ❌   | ✅  | N/A |
|Question 13.6| Do you list third-party publications that refer to your software on your website or link to a resource where these are available?| ❌   | ✅  | No third-party publications yet |
|Question 13.7| Can users subscribe to notifications to changes to your source code repository?| ✅   | ❌  | GitHub watch/star feature allows users to subscribe to repository updates |
|Question 13.8| If your software is developed as an open source project (and, not just a project developing open source software), do you have a governance model?| ✅   | ❌  | See [docs/CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines and project governance |
| *Q14 - Contributions*          ||  |   |   |
|Question 14.1| Do you accept contributions (e.g. bug fixes, enhancements, documentation updates, tutorials) from people who are not part of your project?| ✅   | ❌  | See [docs/CONTRIBUTING.md](CONTRIBUTING.md) "Contributing to ReqEngine" section |
|Question 14.2| Do you have a contributions policy?| ✅   | ❌  | See [docs/CONTRIBUTING.md](CONTRIBUTING.md) with detailed contribution guidelines |
|Question 14.3| Is your contributions' policy publicly available?| ✅   | ❌  | [docs/CONTRIBUTING.md](CONTRIBUTING.md) is publicly available in repository |
|Question 14.4| Do contributors keep the copyright/IP of their contributions?| ✅   | ❌  |See [LICENSE.md](../LICENSE.md) MIT License allows contributors to retain rights while contributing to project |
| *Q15 - Licensing*              |  |  |   |   |                                                                                                                                                                                                                                 
|Question 15.1| Does your website and documentation clearly state the copyright owners of your software and documentation?| ✅   | ❌  | See [LICENSE.md](../LICENSE.md) with ReqEngine copyright statement |
|Question 15.2| Does each of your source code files include a copyright statement?| ❌   | ✅  | Source files lack individual copyright headers |
|Question 15.3| Does your website and documentation clearly state the licence of your software?| ✅   | ❌  | See [README.md](../README.md) "License" section and [LICENSE.md](../LICENSE.md) |
|Question 15.4| Is your software released under an open source licence?| ✅   | ❌  |See [LICENSE.md](../LICENSE.md) MIT License is an open source license |
|Question 15.5| Is your software released under an OSI-approved open-source licence?| ✅   | ❌  | See [LICENSE.md](../LICENSE.md) MIT License is OSI-approved |
|Question 15.6| Does each of your source code files include a licence header?| ❌   | ✅  | Source files lack individual license headers |
|Question 15.7| Do you have a recommended citation for your software?| ✅   | ❌  | See [README.md](../README.md) "Citation" section |
| *Q16 - Future Plans*           |  |  |   |   |
|Question 16.1| Does your website or documentation include a project roadmap (a list of project and development milestones for the next 3, 6 and 12 months)?| ❌   | ✅  | See [docs/CHANGELOG.md](CHANGELOG.md) |
|Question 16.2| Does your website or documentation describe how your project is funded, and the period over which funding is guaranteed?| ❌   | ✅  | N/A |
|Question 16.3| Do you make timely announcements of the deprecation of components, APIs, etc.?| ✅   | ❌  | Changes documented in [docs/CHANGELOG.md](CHANGELOG.md) when applicable |