from ruamel.yaml import YAML  # type: ignore
from pathlib import Path
from typing import Dict, Union
import requests
from multiprocessing.dummy import Pool as ThreadPool


class Monitor:
    def __init__(self) -> None:
        self.config = self.load_config()
        self.status: Dict[str, Union[int, str]] = {}

    def load_config(self) -> Dict:
        path = Path("config.yaml")
        yaml = YAML(typ="safe")
        data = yaml.load(path)
        return data

    def get_config(self) -> Dict:
        return self.config

    def update_status(self, name: str, status_code: Union[int, str]) -> None:
        self.status.update({name: status_code})

    def get_status(self) -> Dict:
        return self.status

    def get_website_status(self, url: str) -> Union[int, str]:
        return self.status[url]

    def check_basic_website(self, website: Dict) -> None:
        status_code: Union[int, str]
        if "certs" in website.keys():
            try:
                status_code = requests.get(
                    website["url"],
                    cert=(website["certs"]["cert"], website["certs"]["key"]),
                    verify=website["certs"]["key"],
                    timeout=15,
                ).status_code
            except requests.ConnectionError:
                status_code = "UNREACHABLE"
            except requests.exceptions.SSLError:
                status_code = "SSL ERROR"
            self.update_status(website["url"], status_code)
        else:
            try:
                status_code = requests.get(website["url"], timeout=15).status_code
            except requests.ConnectionError:
                status_code = "UNREACHABLE"
            self.update_status(website["url"], status_code)

    def load_urls(self) -> None:
        config = self.config
        for group, websites in config.items():
            with ThreadPool() as pool:
                pool.map(self.check_basic_website, websites)


def main():
    websites: Monitor = Monitor()
    websites.load_urls()


if __name__ == "__main__":
    main()
