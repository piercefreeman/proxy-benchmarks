from click import command, option, pass_obj

from proxy_benchmarks.enums import MimicTypeEnum
from proxy_benchmarks.load_test import run_load_server
from proxy_benchmarks.networking import SyntheticHostDefinition, SyntheticHosts
from proxy_benchmarks.proxies.base import ProxyBase
from proxy_benchmarks.proxies.gomitmproxy import GoMitmProxy
from proxy_benchmarks.proxies.goproxy import GoProxy
from proxy_benchmarks.proxies.martian import MartianProxy
from proxy_benchmarks.proxies.mitmproxy import MitmProxy
from proxy_benchmarks.proxies.node_http_proxy import NodeHttpProxy
from proxy_benchmarks.requests import ChromeRequest


@command()
@option("--inspect-commands", is_flag=True)
@pass_obj
def basic_ssl_test(obj, inspect_browser: bool, default=False):
    """
    Walk through the different proxy servers and test their SSL validity separately.
    
    :param inspect-browser: If true, upon issuing each command will wait for the user to press
    enter to continue. This allows you to fully inspect to certificate in the Chrome inspector
    and debugging console.

    """
    console = obj["console"]
    divider = obj["divider"]

    proxies: list[ProxyBase] = [
        GoProxy(MimicTypeEnum.STANDARD),
        GoProxy(MimicTypeEnum.MIMIC),
        MitmProxy(),
        NodeHttpProxy(),
        GoMitmProxy(MimicTypeEnum.STANDARD),
        GoMitmProxy(MimicTypeEnum.MIMIC),
        MartianProxy(),
    ]

    request = ChromeRequest(headless=False, keep_open=inspect_browser)

    with run_load_server() as load_server_definition:
        synthetic_ip_addresses = SyntheticHosts(
            [
                SyntheticHostDefinition(
                    name="load-server",
                    http_port=load_server_definition["http"],
                    https_port=load_server_definition["https"],
                )
            ]
        ).configure()
        synthetic_ip_address = next(iter(synthetic_ip_addresses.values()))
        print("\nSynthetic IP", synthetic_ip_address)

        if inspect_browser:
            print("Waiting for manual client access...")
            if input(" > Press enter when ready...") != "":
                return

        for proxy in proxies:
                with proxy.launch():
                    console.print(f"{divider}\nTesting {request} with proxy {proxy})\n{divider}", style="bold blue")
                    request.handle_request(
                        f"https://{synthetic_ip_address}/handle",
                        proxy=f"http://localhost:{proxy.port}",
                    )
