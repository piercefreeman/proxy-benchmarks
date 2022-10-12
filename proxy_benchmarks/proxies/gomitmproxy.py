from contextlib import contextmanager
from subprocess import Popen
from time import sleep

from proxy_benchmarks.assets import get_asset_path
from proxy_benchmarks.enums import MimicTypeEnum
from proxy_benchmarks.process import terminate_all
from proxy_benchmarks.proxies.base import CertificateAuthority, ProxyBase


class GoMitmProxy(ProxyBase):
    def __init__(self, proxy_type: MimicTypeEnum):
        super().__init__(port=6010)
        self.project_path = "gomitmproxy" if proxy_type == MimicTypeEnum.STANDARD else "gomitmproxy-mimic"

    @contextmanager
    def launch(self):
        #env = {
        #    **environ,
        #    "SSL_CERT_FILE": str(get_asset_path("speed-test/server/cert.crt")),
        #}

        current_extension_path = get_asset_path(f"proxies/{self.project_path}")
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
            public=get_asset_path(f"proxies/{self.project_path}/ca.crt"),
            key=get_asset_path(f"proxies/{self.project_path}/ca.key"),
        )

    @property
    def short_name(self) -> str:
        return self.project_path

    def __repr__(self) -> str:
        return f"GoMitmProxy(port={self.port},version={self.project_path})"
