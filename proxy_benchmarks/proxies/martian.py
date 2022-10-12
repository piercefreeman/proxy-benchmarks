from contextlib import contextmanager
from subprocess import Popen
from time import sleep

from proxy_benchmarks.assets import get_asset_path
from proxy_benchmarks.process import terminate_all
from proxy_benchmarks.proxies.base import ProxyBase, CertificateAuthority


class MartianProxy(ProxyBase):
    def __init__(self):
        super().__init__(port=6012)

    @contextmanager
    def launch(self):
        current_extension_path = get_asset_path("proxies/martian")
        process = Popen(f"go run . --port {self.port}", shell=True, cwd=current_extension_path)

        self.wait_for_launch()
        # Requires a bit more time to load than our other proxies
        sleep(2)

        try:
            yield process
        finally:
            terminate_all(process)

            # Wait for the socket to close
            self.wait_for_close()

    @property
    def certificate_authority(self) -> CertificateAuthority:
        return CertificateAuthority(
            public=get_asset_path("proxies/martian/ca.crt"),
            key=get_asset_path("proxies/martian/ca.key"),
        )

    @property
    def short_name(self) -> str:
        return "martian"

    def __repr__(self) -> str:
        return f"MartianProxy(port={self.port})"
