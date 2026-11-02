-- ranking_node_repositories.sql
-- Estrae e ordina i repository Node.js (JavaScript/TypeScript) dal database E2EGit.db
-- Criteri: presenza di test GUI E2E (Cypress, Playwright, Puppeteer), ordinati per numero di test e commit.

SELECT 
    g.repository_name,
    r.main_language AS linguaggio,
    CASE 
        WHEN (g.number_files_cypress_js + g.number_files_cypress_ts) > 0 
             AND (g.number_files_playwright_js + g.number_files_playwright_ts) > 0 THEN 'Cypress + Playwright'
        WHEN (g.number_files_cypress_js + g.number_files_cypress_ts) > 0 THEN 'Cypress'
        WHEN (g.number_files_playwright_js + g.number_files_playwright_ts) > 0 THEN 'Playwright'
        WHEN (g.number_files_puppeteer_js + g.number_files_puppeteer_ts) > 0 THEN 'Puppeteer'
        ELSE 'Selenium'
    END AS framework_e2e,
    g.number_of_tests AS num_test_gui,
    g.number_of_files AS num_file_test,
    r.commits AS commit_totali,
    r.stargazers AS stelle_github,
    r.contributors,
    'https://github.com/' || g.repository_name AS github_url
FROM gui_testing_repo_details g
JOIN repository r ON g.repository_name = r.name
WHERE r.main_language IN ('JavaScript', 'TypeScript')
  AND (
      (g.number_files_cypress_js + g.number_files_cypress_ts) > 0 OR
      (g.number_files_playwright_js + g.number_files_playwright_ts) > 0 OR
      (g.number_files_puppeteer_js + g.number_files_puppeteer_ts) > 0
  )
ORDER BY 
    g.number_of_tests DESC, 
    r.commits DESC
LIMIT 20;

