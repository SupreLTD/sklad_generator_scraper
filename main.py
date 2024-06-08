from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from tqdm import tqdm

from pages import BasePage, PageList, PageDetail

CATALOG = [
    "https://www.sklad-generator.ru/elektrostancii/dizelnye/agg/",
    "https://www.sklad-generator.ru/elektrostancii/dizelnye/arken/",
    "https://www.sklad-generator.ru/elektrostancii/dizelnye/enegorpom/",
    "https://www.sklad-generator.ru/elektrostancii/dizelnye/emsa/",
    "https://www.sklad-generator.ru/elektrostancii/dizelnye/eco-power/",
    "https://www.sklad-generator.ru/elektrostancii/dizelnye/magnus/",
    "https://www.sklad-generator.ru/elektrostancii/dizelnye/mge/",
    "https://www.sklad-generator.ru/elektrostancii/dizelnye/ortea/",
    "https://www.sklad-generator.ru/elektrostancii/dizelnye/rensol/",
    "https://www.sklad-generator.ru/elektrostancii/dizelnye/wattstream/",
    "https://www.sklad-generator.ru/elektrostancii/dizelnye/weifang/",
    "https://www.sklad-generator.ru/elektrostancii/dizelnye/zammer/",
    "https://www.sklad-generator.ru/elektrostancii/gazovye/jenbacher/",
    "https://www.sklad-generator.ru/elektrostancii/gazovye/poweron/",
    "https://www.sklad-generator.ru/elektrostancii/gazovye/fregat/",
    "https://www.sklad-generator.ru/elektrostancii/benzinovye/ctg/",
]


def parse():
    for url in tqdm(CATALOG):
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True, timeout=60000)  # headless=False откроет физический браузер
            context = browser.new_context(
                ignore_https_errors=True,
            )
            context.route("**/*", BasePage.handle_request)
            page = context.new_page()
            stealth_sync(page)

            gen_page = PageList(page, url)
            gen_page.navigate()
            gen_page.load_full_page_data()
            links = gen_page.get_links()
            for link in links:
                page_detail = PageDetail(page, link)
                page_detail.navigate()
                page_detail.get_all_positions()

            page.close()
            context.close()


if __name__ == '__main__':
    parse()
