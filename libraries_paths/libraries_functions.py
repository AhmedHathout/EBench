from libraries_paths.libraries_paths import *

job = lambda job_id: "Job" + str(job_id) + "/"
prover_path = lambda prover_id: "E" + str(prover_id)
prover_bin = lambda prover_id: prover_path(prover_id) + "/bin/"
removed_problems = "removed_problems.txt"
failed_problems = "failed_problems.tsv"
report = lambda job_id: "Job" + str(job_id) + ".tsv"

def get_server_job_report_path_by_id(job_id):
    return server_jobs_reports_library + job(job_id)

def get_server_removed_problems_from_job(job_id):
    return get_server_job_report_path_by_id(job_id) + removed_problems

def get_server_failed_problems_from_job(job_id):
    return get_server_job_report_path_by_id(job_id) + failed_problems

def get_job_report(job_id):
    return get_server_job_report_path_by_id(job_id) + report(job_id)

def get_server_job_results_path_by_id(job_id):
    return server_jobs_results_library + job(job_id)

def get_client_job_report_path_by_id(job_id):
    return client_jobs_reports_library + job(job_id)

def get_client_job_results_path_by_id(job_id):
    return client_jobs_results_library + job(job_id)

def get_prover_path(prover_id):
    return provers_library + prover_path(prover_id)

def get_prover_bin(prover_id):
    return provers_library + prover_bin(prover_id)