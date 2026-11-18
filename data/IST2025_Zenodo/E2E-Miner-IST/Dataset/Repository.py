from sqlalchemy import ForeignKey, String, Integer, Boolean, Column, ForeignKeyConstraint
from sqlalchemy.exc import SQLAlchemyError

from Dataset.DBconnector import Base, Session, engine

class Repository(Base):
    __tablename__ = "repository"
    ID = Column(Integer(),primary_key=True)
    name = Column(String())
    is_fork = Column(Boolean())
    commits = Column(Integer())
    branches = Column(Integer())
    releases = Column(Integer())
    forks = Column(Integer())
    main_language = Column(String())
    default_branch = Column(String())
    licences = Column(String())
    homepage = Column(String())
    watchers = Column(Integer())
    stargazers = Column(Integer())
    contributors = Column(Integer())
    size = Column(Integer())
    created_at = Column(String())
    pushed_at = Column(String())
    updated_at = Column(String())
    total_issues = Column(Integer())
    open_issues = Column(Integer())
    total_pull_requests = Column(Integer())
    open_pull_requests = Column(Integer())
    blank_lines = Column(Integer())
    code_lines = Column(Integer())
    comment_lines = Column(Integer())
    metrics = Column(String())
    last_commit = Column(String())
    last_commit_sha = Column(String())
    has_wiki = Column(Boolean())
    is_archived = Column(Boolean())
    is_disabled = Column(Boolean())
    is_locked = Column(Boolean())
    languages = Column(String())
    labels = Column(String())
    topics = Column(String())
    is_processed = Column(Boolean())

    def __init__(self,id, name, is_fork, commits, branches, releases, forks,
                 main_language, default_branch, licenses, homepage, watchers,
                 stargazers, contributors, size, created_at, pushed_at, updated_at,
                 total_issues, open_issues, total_pull_requests, open_pull_requests,
                 blank_lines, code_lines, comment_lines, metrics, last_commit,
                 last_commit_sha, has_wiki, is_archived, is_disabled, is_locked, languages, labels, topics,is_processed):
        self.ID = id
        self.name = name
        self.is_fork = is_fork
        self.commits = commits
        self.branches = branches
        self.releases = releases
        self.forks = forks
        self.main_language = main_language
        self.default_branch = default_branch
        self.licences = licenses
        self.homepage = homepage
        self.watchers = watchers
        self.stargazers = stargazers
        self.contributors = contributors
        self.size = size
        self.created_at = created_at
        self.pushed_at = pushed_at
        self.updated_at = updated_at
        self.total_issues = total_issues
        self.open_issues = open_issues
        self.total_pull_requests = total_pull_requests
        self.open_pull_requests = open_pull_requests
        self.blank_lines = blank_lines
        self.code_lines = code_lines
        self.comment_lines = comment_lines
        self.metrics = metrics
        self.last_commit = last_commit
        self.last_commit_sha = last_commit_sha
        self.has_wiki = has_wiki
        self.is_archived = is_archived
        self.is_disabled = is_disabled
        self.is_locked = is_locked
        self.languages = languages
        self.labels = labels
        self.topics = topics
        self.is_processed = is_processed
        Base.metadata.create_all(engine)

    def connect_to_db(self):
        local_session = Session(bind=engine)
        return local_session

    def add_repository_to_db(self):
        local_session = Session(bind=engine)
        self.languages = self.convert_list_in_string(self.languages)
        self.labels = self.convert_list_in_string(self.labels)
        self.topics = self.convert_list_in_string(self.topics)
        self.metrics = self.convert_metrics_in_string(self.metrics)
        local_session.add(self)
        local_session.commit()

    def convert_metrics_in_string(self, metric):
        import json
        data = json.loads(metric)


        metrics_strings = []


        for item in data:

            metrics_str = f"language:{item['language']}, commentLines:{item['commentLines']}, codeLines:{item['codeLines']}, blankLines:{item['blankLines']}"

            metrics_strings.append(metrics_str)


        output_string = "; ".join(metrics_strings)
        return output_string

    def convert_list_in_string(self, general_list):
        string = ""
        for element in general_list:
            string = string + element + "; "
        return string

    def convert_string_language_in_list(self):

        elements = self.languages.rstrip("; ").split("; ")
        self.languages = elements

    def update_processed_repository(self):
        local_session = Session(bind=engine)

        repository_to_update = local_session.query(Repository).filter(Repository.ID == self.ID).first()
        repository_to_update.is_processed = True
        local_session.commit()



class NonTrivialRepo(Base):
    __tablename__ = "nonTrivialRepository"
    IDweb = Column(Integer(),primary_key=True)
    IDrepository = Column(Integer())
    name = Column(String())
    is_web_java = Column(Boolean())
    is_web_python = Column(Boolean())
    is_web_javascript = Column(Boolean())
    is_web_typescript = Column(Boolean())
    web_dependencies = Column(String())

    __table_args__ = (
        ForeignKeyConstraint(['IDrepository'], ['repository.ID']),
    )

    def __init__(self, idweb,idrepo, name,is_web_java, is_web_py,_is_web_js, is_web_ty,web_deps):
        self.IDweb = idweb
        self.IDrepository = idrepo
        self.name = name
        self.is_web_java = is_web_java
        self.is_web_python = is_web_py
        self.is_web_javascript = _is_web_js
        self.is_web_typescript = NonTrivialRepo.is_web_typescript
        self.web_dependencies = self.convert_list_in_string(web_deps)
        Base.metadata.create_all(engine)

    def add_web_repository_to_db(self):
        local_session = Session(bind=engine)
        local_session.add(self)
        local_session.commit()

    def convert_list_in_string(self, general_list):
        string = ""
        for element in general_list:
            string = string + element + "; "
        return string

    def fetch_allwebrepo(self):
        local_session = Session(bind=engine)
        return local_session

        records = session.query(WebRepositoryDAO).all()


        for record in records:
            print(record.id, record.name, record.value)



class WebGUIRepository(Base):
    __tablename__ = 'WebGUIRepository'

    repository_name = Column(String, ForeignKey('nonTrivialRepository.name'), primary_key=True)
    selenium_java = Column(Integer)
    selenium_js = Column(Integer)
    selenium_ts = Column(Integer)
    selenium_py = Column(Integer)
    playwright_java = Column(Integer)
    playwright_js = Column(Integer)
    playwright_ts = Column(Integer)
    playwright_py = Column(Integer)
    puppeteer_js = Column(Integer)
    puppeteer_ts = Column(Integer)
    puppeteer_py = Column(Integer)
    cypress_js = Column(Integer)
    cypress_ts = Column(Integer)
    with_junit = Column(Integer)
    with_testng = Column(Integer)
    with_jest = Column(Integer)
    with_mocha = Column(Integer)
    with_jasmine = Column(Integer)
    with_pytest = Column(Integer)
    with_unittest = Column(Integer)
    number_of_test = Column(Integer)
    number_of_file = Column(Integer)

    def __init__(self, repo_name):
        self.repository_name=repo_name
        self.selenium_java = 0
        self.selenium_js = 0
        self.selenium_ts = 0
        self.selenium_py = 0
        self.playwright_java = 0
        self.playwright_js = 0
        self.playwright_ts = 0
        self.playwright_py = 0
        self.puppeteer_js = 0
        self.puppeteer_ts = 0
        self.puppeteer_py = 0
        self.cypress_js = 0
        self.cypress_ts = 0
        self.with_junit = 0
        self.with_testng = 0
        self.with_jest = 0
        self.with_mocha = 0
        self.with_jasmine = 0
        self.with_pytest = 0
        self.with_unittest = 0
        self.number_of_test = 0
        self.number_of_file = 0

    def add_e2erepository_to_db(self):
        with Session(bind=engine) as local_session:
            local_session.add(self)
            local_session.commit()
