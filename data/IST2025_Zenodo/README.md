# IST25-WebGUITesting

The replication package provides  information on GitHub repositories analyzed for the study titled Investigating the Adoption and Maintenance of Web GUI Testing:  
Insights from GitHub Repositories". The dataset includes an SQLite database and three folders with data organized according to the research questions (RQs).

## Dataset Structure

1. **SQLite Database (`ist-webgui.db`)**: contains primary information on all analyzed repositories, with specific details on those with Web GUI tests.
2. **Data folders**: each folder is dedicated to addressing one of the research questions (RQs).

---

## SQLite Database: `ist25-webgui.db`

The SQLite database consists of the following tables:

### 1. `repository`

This table includes basic information on over 1 million repositories retrieved from SEART. Each field in this table is self-explanatory, detailing relevant attributes for each repository.

### 2. `nonTrivialRepository`

This table contains the 5,623 repositories identified as "non-toy". For each repository, it provides detailed information on:

- **Type of web repository**: for example, the `is_web_java` field is set to 1 if the repository includes dependencies with one of the analyzed Java web frameworks.
- **Dependencies**: the `web_dependencies` field lists web dependencies identified for each repository.
- **File paths**: the `test_path` field includes paths to files that have dependencies on any of the browser automation frameworks, allowing for the identification of Web GUI test files.

### 3. `WebGUIRepository`

This table includes the 472 repositories that contain at least one Web GUI test. For each repository, it provides:

- **Browser automation frameworks**: information on the browser automation frameworks used (e.g., `selenium_java` indicates the use of Selenium in Java).
- **Test engines**: the test runner used for the automation framework, such as `with_junit` indicating JUnit as the test engine.
- **Number of tests**: the `number_of_test` field represents the total number of tests identified within the repository. For example, `selenium_java=3`, `with_junit=3`, and `number_of_test=10` indicate that 3 Java files using Selenium as the framework and JUnit as the test engine were found, containing a total of 10 tests.

---
**`ist-number-of-tests`**: this file reports information on the number of web GUI testing in each project.

---
## Research Question 1: To what extent are web GUI tests adopted in open-source web applications?

Data used to answer this research question are extracted from `ist25-webgui.db`, with further information available in the following folders/file:

### 1. `adoption_migration_commit`

This folder contains information on the analysis performed on commit messages to understand the reasons behind the adoption on web GUI testing and the migration from a framework to another one. The folder contains info on the keyword used to extract relevant commit messages. 

### 2. `migration_analysis`

This file contains information to track browser automation framework migrations over time. 

### 3. `results_coadoption`

This file contains information the projects that show a co-adoption of the frameworks analyzed.

### 4. `creation-adoption-gui`

This file contains information on when the projects have adopted a browser automation framework to perform a web GUI testing 

---

## Research Question 2: What are the main characteristics of projects adopting web GUI testing??

This folder provides the data required for statistical analysis, focusing on the characteristics of projects that adopt Web GUI testing. It contains the following:

### 1. `rq2_data`

This file includes data for each of the 5,623 web repositories analyzed, with each column representing an attribute considered in the study. The columns are self-explanatory and provide insight into repository characteristics relevant to Web GUI testing.

### 2. `other_test_analysis`

The `nOtherTest` field in `rq2_data` is calculated based on an analysis of additional test types (beyond Web GUI tests). This folder includes, for each repository, a file listing other test files detected and the number of tests they contain.

### 3. `issues_analysis` and `issues_analysis.xlsx`

The `issues_analysis` folder contains JSON files with details on open and closed issues for the 472 repositories studied. The `githubactions_issues_analysis` file provides information on automated issues, noting whether they were closed due to inactivity or resolved by a developer.

---
## Research Question 3: Do web GUI tests co-evolve with the web application, and how are these tests maintained as the application evolves?

The data and files necessary for answering this research question are organized as follows:

### 1. Co-evolution and Maintenance Metrics

- **`ass_rule-metrics`, `coevolution-metrics`, `tests_maintenance_metrics`**: These files contain results related to association rule metrics and co-evolution analysis used to assess the relationship between Web GUI tests and application evolution. The files use the same nomenclature as in the paper; for more details, refer to the publication. We considered differents commit-window sizes from 0 to 10.
- **`ass_rule-metrics_15_20`**: Contains information on the association rule computed for the 15- and 20-commit-window size

### 2. `commits_analysis` Folder

This folder provides the necessary data for co-evolution adn maintenance analysis, organized as follows:

- **`commits_analysis_reponame_only_app`**: A matrix where each row represents an application file, each column represents a commit (in ascending order), and cells indicate the file’s status:
   - `A`: File was added.
   - `D`: File was deleted.
   - `R(new_name)`: File was renamed; `new_name` is the new file name.
   - `M(n)`: File was modified by `n%`.
   - Example: Row 3, Column 5 shows `A`, meaning the file in Row 3 was added in the 5th commit.

- **`commits_analysis_reponame_only_gui`**: Similar to the `only_app` file but for Web GUI test files.

- **`commits_analysis_reponame_app_span_analysis`**: Contains span data for application commits, with details on each span and associated commit information (e.g., dates).

- **`commits_analysis_reponame_gui_span_analysis`**: Similar to the `app_span_analysis` file but for Web GUI test spans.

- **`commits_analysis_reponame_tests_lifecycle_analysis`**: Contains metrics for each Web GUI test file, tracking maintenance over its lifecycle according to the criteria detailed in the paper.


### 3. selenium_changes and developers analysis

- **`selenium_changes_aggregation_results`** This file contains all information on the analysis performed on the By.<selector> to analyze the maintenance activities in Selenium
- **`dev-analysis`** This file contains the analysis perfomed with Pydriller on the maitenance activities from developers' perspective.



