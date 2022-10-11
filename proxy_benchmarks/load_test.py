from dataclasses import dataclass
from os import environ
from subprocess import Popen

from configargparse import DefaultConfigFileParser
from contextlib import contextmanager

from proxy_benchmarks.assets import get_asset_path
from proxy_benchmarks.process import terminate_all
from proxy_benchmarks.proxies.base import ProxyBase
from proxy_benchmarks.networking import is_socket_bound
from time import sleep


@dataclass
class LoadTestResults:
    stats: str
    exceptions: str
    failures: str
    stats_history: str


def load_config(path: str) -> str:
    config = DefaultConfigFileParser()
    with open(path) as file:
        return config.parse(file)


@contextmanager
def run_load_server(port=3010, tls_port=3011):
    """
    :port 3010: host a standard http server
    """
    server_path = get_asset_path("speed-test/server")
    server_process = Popen(f"go run . --port {port} --tls-port {tls_port}", shell=True, cwd=server_path)

    # Wait for the server to spin up
    sleep(2)

    try:
        yield dict(http=port, https=tls_port)
    finally:
        terminate_all(server_process)


def run_load_test(
    url: str,
    config_path: str,
    run_time_seconds: int = 60,
    spawn_processes: int = 5,
    proxy: ProxyBase | None = None
) -> LoadTestResults:
    locust_project_path = get_asset_path("speed-test/locust")
    locust_config = load_config(locust_project_path / config_path)

    env = environ.copy()

    if proxy:
        assert proxy.certificate_authority.public.exists()
        assert proxy.certificate_authority.key.exists()

        env["PROXY_PORT"] = str(proxy.port)
        env["PROXY_CERTIFICATE"] = str(proxy.certificate_authority.public)
        env["PROXY_CERTIFICATE_KEY"] = str(proxy.certificate_authority.key)

    try:
        # Launch the coordination server
        # This will wait to launch until N processes have connected
        main_process = Popen(
            f"poetry run locust --run-time {run_time_seconds}s --master --expect-workers {spawn_processes} --config={config_path} --host={url}",
            shell=True,
            cwd=locust_project_path,
            env=env
        )

        worker_processes = [
            Popen(
                f"poetry run locust --worker --config={config_path} --host={url}",
                shell=True,
                cwd=locust_project_path,
                env=env
            )
            for _ in range(spawn_processes)
        ]

        main_process.wait()

    finally:
        terminate_all(main_process)
        for process in worker_processes:
            terminate_all(process)

    # Path prefix to the csv files, relative to the locust project
    csv_prefix = locust_config["csv"]

    return LoadTestResults(
        stats=locust_project_path / f"{csv_prefix}_stats.csv",
        stats_history=locust_project_path / f"{csv_prefix}_stats_history.csv",
        exceptions=locust_project_path / f"{csv_prefix}_exceptions.csv",
        failures=locust_project_path / f"{csv_prefix}_failures.csv",
    )