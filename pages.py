import csv
import re

from playwright.sync_api import Page
from loguru import logger


class BasePage:
    def __init__(self, page: Page, url: str):
        self.page = page
        self.url = url

    def navigate(self):
        logger.debug(f"Navigating to {self.url}")
        self.page.goto(self.url, wait_until="load")

    @staticmethod
    def handle_request(route, request):
        if request.resource_type == "image":
            route.abort()
        else:
            route.continue_()


class PageList(BasePage):
    def __init__(self, page: Page, url: str):
        super().__init__(page, url)

    def load_full_page_data(self) -> None:
        flag = True
        while flag:
            self.page.wait_for_load_state('load')
            next_button = self.page.locator('text=Показать еще')
            if next_button.is_hidden():
                flag = False
            elif next_button.is_visible():
                next_button.click(timeout=60000)
            else:
                self.page.wait_for_timeout(5000)

    def get_links(self) -> list:
        elements = self.page.query_selector_all('.product__block-link.js-product-link')
        links = [element.get_attribute('href') for element in elements]
        logger.info(f'Scraped {len(links)} links')
        return links


class PageDetail(BasePage):
    def __init__(self, page: Page, url: str):
        super().__init__(page, url)

    def _load_labels(self):
        labels = self.page.query_selector_all(
            "xpath=//div[contains(@class, 'product-card__variation-option-name') and text("
            ")='Исполнение:']/following-sibling::div[1]//label[not(following-sibling::div[contains(@class, "
            "'product-card__variation-option-name') and text()='Степень автоматизации'])]")
        return labels

    def get_all_positions(self):
        self.process_data()
        initial_labels = self._load_labels()
        for label in range(1, len(initial_labels)):
            labels = self._load_labels()
            labels[label].click()
            self.page.wait_for_load_state('load')
            self.process_data()

    def process_data(self):
        title = self.page.query_selector('h1').inner_text()
        url = self.page.url
        image_path = self.page.query_selector('.inline-gallery.js-product-card-gallery').query_selector_all('img')
        images = [i.get_attribute('src') for i in image_path]
        images = [re.sub(r'thumb[^/]*/', 'original/', image) for image in images]
        images = ', '.join(images)

        table = self.page.query_selector_all('.options-table__item')
        specification = []
        for row in table:
            key = row.query_selector('.options-table__item-caption').inner_text().replace('?', '').strip()
            if key == 'Информация о доставке':
                continue
            value = row.query_selector('.options-table__item-value').inner_text()
            specification.append(f'{key} {value}')

        specification = ', '.join(specification)

        with open('data/data.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([title, url, images, specification])
