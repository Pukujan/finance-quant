from finance_quant.orchestration.authority import CapabilityClass, worker_environment


def test_research_worker_env_does_not_include_mlflow_uri():
    env = worker_environment(CapabilityClass.RESEARCH_WORKER, {
        "PATH": "x", "MLFLOW_TRACKING_URI": "http://evil", "FQ_CAPABILITY": "ignored",
    })
    assert "MLFLOW_TRACKING_URI" not in env
    assert env["FQ_CAPABILITY"] == "research_worker"
