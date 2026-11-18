import csv
from itertools import islice

import pandas as pd
import requests
import json
import  os


class TotalIssue:


    token = "your_token_here"
    headers = {
        "Authorization": f"{token}",
        "Accept": "application/vnd.github.v3+json"
    }

    @staticmethod
    def get_all_issues(state,repo_name):
        issues_url = f"https://api.github.com/repos/{repo_name}/issues"
        all_issues = []
        page = 1
        while True:
            print(f'page:{page}')
            params = {
                "state": state,
                "per_page": 100,
                "page": page
            }
            response = requests.get(issues_url, headers=TotalIssue.headers, params=params)

            if response.status_code == 200:
                issues = response.json()
                if not issues:
                    break
                all_issues.extend(issues)
                page += 1
            else:
                print(f"Errore {response.status_code}: {response.json()['message']}")
                break

        return all_issues


    @staticmethod
    def get_number_of_open_closed_issues(repo_name,save_flag):
        open_issues = TotalIssue.get_all_issues("open",repo_name)
        closed_issues = TotalIssue.get_all_issues("closed",repo_name)

        all_issues = {
            "open": open_issues,
            "closed": closed_issues
        }

        if save_flag:
            out_file_name=f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/webrepo_issues_analysis/webrepo_issues_analysis/'+repo_name.replace('/','_',1)+"_all_issues.json"
            with open(out_file_name,'w') as json_file:
                json.dump(all_issues, json_file, indent=4)
            #print(f"{len(open_issues)} issue aperte e {len(closed_issues)} issue chiuse salvate in 'all_issues.json'.")
        github_actions_issues = TotalIssue.check_github_actions_issues(open_issues,closed_issues)
        return len(open_issues),len(closed_issues),len(github_actions_issues['open']),len(github_actions_issues['closed'])

    @staticmethod
    def check_github_actions_issues(open_issues, closed_issues):

        github_actions_issues = {
            "open": [],
            "closed": []
        }

        for issue in open_issues:
            if issue is not None and issue.get('user', {}).get('login') == 'github-actions[bot]':
                github_actions_issues['open'].append(issue)

        for issue in closed_issues:
            if issue is not None and issue.get('user', {}).get('login') == 'github-actions[bot]':
                github_actions_issues['closed'].append(issue)

        return github_actions_issues


    @staticmethod
    def calculate_number_of_issue(start,end):
        output_file = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/total_issues_analysis_2.xlsx'
        df_res = pd.read_excel(output_file)
        df = pd.read_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ2/rq2_data.xlsx')
        for index, row in islice(df.iterrows(),start,end):
            repo_name = row.iloc[0]
            num_of_test= row.iloc[11]
            print(f' sto processando {repo_name} con num_of_test:{num_of_test}')
            save_file_issue = num_of_test>0
            open_issues,closed_issues,action_open_issue,action_closed_issues=TotalIssue.get_number_of_open_closed_issues(repo_name,save_file_issue)
            print(f'open-issues:{open_issues} - closed-issues:{closed_issues} act-open: {action_open_issue} act-close :{action_closed_issues}')
            new_row = {
                'repo': repo_name,
                'open' : open_issues,
                'closed': closed_issues,
                'act-open':action_open_issue,
                'act-closed': action_closed_issues
            }
            print(new_row)
            #new_row_df = pd.DataFrame([new_row])
            #df_res = pd.concat([df_res, new_row_df], ignore_index=True)
            #df_res.to_excel(output_file,index=False)


    @staticmethod
    def save_rq2_new_total_issues():
        rq2_data = pd.read_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ2/rq2_data_updated.xlsx')
        total_1 = pd.read_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/total_issues_analysis_1.xlsx')
        total_2 = pd.read_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/total_issues_analysis_2.xlsx')
        flag_found = 0
        for index,row in rq2_data.iterrows():
            repo_name = row.iloc[0]
            total_issue = row.iloc[11]
            total_issue_ga = row.iloc[12]
            if pd.isna(total_issue):
                for index_1,row_1 in total_1.iterrows():
                    repo_name1= row_1.iloc[0]
                    if repo_name1==repo_name:
                        open_issue = row_1.iloc[1]
                        closed_issue= row_1.iloc[2]
                        open_ga = row_1.iloc[3]
                        closed_ga = row_1.iloc[4]
                        #print(f'1 {repo_name} - {open_issue}-  {closed_issue}')
                        if open_issue>0 or closed_issue > 0:
                            flag_found=1
                            rq2_data.at[index,'totalIssue'] = open_issue+closed_issue
                            rq2_data.at[index,'totalIssue_noGA'] = (open_issue+closed_issue)-(open_ga+closed_ga)
                            break
                if flag_found ==0:
                    for index_2,row_2 in total_2.iterrows():
                        repo_name2 = row_2.iloc[0]
                        if repo_name2 == repo_name:
                            open_issue = row_2.iloc[1]
                            closed_issue = row_2.iloc[2]
                            open_ga = row_2.iloc[3]
                            closed_ga = row_2.iloc[4]
                            #print(f'2 {repo_name} - {open_issue}-  {closed_issue}')
                            if open_issue > 0 or closed_issue > 0:
                                rq2_data.at[index, 'totalIssue'] = open_issue + closed_issue
                                rq2_data.at[index, 'totalIssue_noGA'] = (open_issue + closed_issue) - (open_ga + closed_ga)
                                flag_found =1
                                break
                if flag_found == 0:
                    print(f'{repo_name} con indice {index} non trovata!')
                flag_found=0
        # Salva il DataFrame aggiornato
        rq2_data.to_excel('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ2/rq2_data_updated.xlsx',index=False)

    '''
    @staticmethod
    def create_csv_file_res():
        session = Session(bind=engine)
        print("Connection successful!")

        # Query con join tra WebRepositoryDAO e E2ERepository
        records = session.query(WebRepositoryDAO, E2ERepository).join(
            E2ERepository,
            WebRepositoryDAO.name == E2ERepository.repository
        ).filter(
            or_(
                WebRepositoryDAO.is_web_java == True,
                WebRepositoryDAO.is_web_javascript == True,
                WebRepositoryDAO.is_web_typescript == True,
                WebRepositoryDAO.is_web_python == True
            ),
                E2ERepository.number_of_test > 30
        ).all()
        # Esportare i risultati in CSV
        with open('repo_191_query.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)

            # Scrivi l'intestazione
            header = [column.key for column in WebRepositoryDAO.__table__.columns] + \
                     [column.key for column in E2ERepository.__table__.columns]
            writer.writerow(header)

            # Scrivi i dati
            for web_repo, e2e_repo in records:
                row = [getattr(web_repo, column) for column in header[:len(WebRepositoryDAO.__table__.columns)]] + \
                      [getattr(e2e_repo, column) for column in header[len(WebRepositoryDAO.__table__.columns):]]
                writer.writerow(row)
        print("Dati esportati con successo in risultati_query.csv")
        '''

    @staticmethod
    def count_ga_open_issues(open_issues):
        # Scorri le issue aperte e verifica se l'autore è "github-actions[bot]"
        count=0
        for issue in open_issues:
            if issue is not None and issue.get('user', {}).get('login') == 'github-actions[bot]':
                count+=1
        return count

    @staticmethod
    def count_ga_closed_issues(closed_issues):
        inactivity_count = 0
        taken_by_other_count = 0
        e2e_issues_count = 0
        for issue in closed_issues:
            # Verifica che l'issue sia stata chiusa da github-actions[bot]
            if issue is not None and issue.get('user', {}).get('login') == 'github-actions[bot]' and issue.get('state') == 'closed':
                # Recupera il corpo della issue (o il messaggio finale) e verifica che non sia None
                closed_by = issue.get('closed_by',{})
                if closed_by is not None:
                    closed_by_user =closed_by.get('login')
                # Controlla il motivo di chiusura per identificare l'inattività

                if closed_by_user == 'github-actions[bot]':
                    inactivity_count += 1
                else:
                    # Altrimenti conta come presa in carico da qualcun altro
                    taken_by_other_count += 1

                # Controlla se una label contiene "e2e"
                labels = issue.get('labels', [])
                if any('e2e' in label.get('name', '').lower() for label in labels):
                    e2e_issues_count += 1

        return inactivity_count, taken_by_other_count,e2e_issues_count


    @staticmethod
    def load_json_files_from_directory(directory_path):
        df_repos = pd.read_csv(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/filename.csv')
        df_res = pd.read_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/githubactions_issues_analysis.xlsx')
        # Scorre tutti i file nella cartella specificata
        for index,row in df_repos.iterrows():
            name = row.iloc[0]
            #print(name)
            if os.path.exists(directory_path+'/'+name+'_all_issues.json'):
                file_path = os.path.join(directory_path, name+'_all_issues.json')
                # Apre e carica il contenuto del file JSON
                #if name=='woocommerce_woocommerce':
                with open(file_path, 'r', encoding='utf-8') as json_file:
                    try:
                        data = json.load(json_file)
                        open_ga = TotalIssue.count_ga_open_issues(data['open'])
                        close_ga = TotalIssue.count_ga_open_issues(data['closed'])
                        inactivity_count, taken_by_other_count, e2e_issues_count = TotalIssue.count_ga_closed_issues(data['closed'])
                        print(f'repo : {name} open_ga:{open_ga} closed_ga :{close_ga} tot ={open_ga+close_ga} inactivity:{inactivity_count} taken_by: {taken_by_other_count} e2e-label:{e2e_issues_count}')
                    except json.JSONDecodeError as e:
                        print(f"Errore nel parsing del file {name}: {e}")
                    new_row = {
                        'repo': name,
                        'open_GA': open_ga,
                    'closed_GA': close_ga,
                    'closed_for_inactivity':inactivity_count,
                    'closed_resolved':taken_by_other_count,
                    'label - % e2e %':e2e_issues_count
                    }
                    new_row_df = pd.DataFrame([new_row])
                    df_res = pd.concat([df_res,new_row_df],ignore_index=True)
                    df_res.to_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/githubactions_issues_analysis.xlsx',index=False)



    @staticmethod
    def missed_repo(directory_path):
        df_repos = pd.read_csv(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/repo_to_analyze.csv')
        for index,row in df_repos.iterrows():
            name = row.iloc[0]
            if not (os.path.exists(directory_path + '/' + name + '_all_issues.json')):
                print(f'sto analizzando {name}')
                TotalIssue.get_number_of_open_closed_issues(name.replace('_','/',1),1)



    @staticmethod
    def fill_total_issue_perf():
        file_path ='/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ2/rq2_data.xlsx'
        df = pd.read_excel(file_path)
        for index,row in df.iterrows():
            repo_name = row["repoName"]
            if pd.isna(df.at[index,"totalIssue"]):
                open,closed,open_ga,closed_ga=TotalIssue.get_number_of_open_closed_issues(repo_name,False)
                df.at[index,"totalIssue"] = open+closed
                df.at[index,"totalIssue_noGA"] = open_ga+closed_ga
        df.to_excel(file_path, index=False, engine="openpyxl")
        print("Modified!")


if __name__ == "__main__":
    TotalIssue.fill_total_issue_perf()
    #TotalIssue.calculate_number_of_issue(2529,5232)
    #TotalIssue.load_json_files_from_directory(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/webrepo_issues_analysis/webrepo_issues_analysis')
    #TotalIssue.save_rq2_new_total_issues()
    #TotalIssue.create_csv_file_res()
    # #TotalIssue.missed_repo(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/webrepo_issues_analysis/webrepo_issues_analysis')
