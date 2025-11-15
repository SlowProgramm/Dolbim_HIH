import json
import re
import requests
import time
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from tqdm import tqdm

BASE_CATALOG_URL = "https://www.rustore.ru/catalog/games/all"
MAX_PAGES = 4
TARGET_CATEGORIES = [
    "Шутеры",
    "Аркады",
    "Гоночные",
    "Игры с AR",
    "Головоломки",
    "Словесные",
    "Викторины",
    "Приключения",
    "Ролевые",
    "Инди",
    "Стратегии",
    "Настольные игры",
    "Карточные",
    "Детские",
    "Семейные",
]
TARGET_CATEGORIES_LOWER = [cat.lower() for cat in TARGET_CATEGORIES]
OUTPUT_FILE = "filtered_apps.json"
REQUEST_DELAY = 0.8

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def is_target_category(categories):
    for cat in categories:
        if cat.lower() in TARGET_CATEGORIES_LOWER:
            return True
    return False

def parse_rustore_app(url, app_id):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.rustore.ru/",
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")

        script_tag = soup.find("script", type="application/ld+json")
        if not script_tag:
            return None

        try:
            data = json.loads(script_tag.string)
        except json.JSONDecodeError:
            return None

        app_data = None
        for item in data.get("@graph", []):
            if item.get("@type") == "SoftwareApplication":
                app_data = item
                break

        if not app_data:
            return None

        short_desc = clean_text(app_data.get("description", ""))
        full_desc = extract_full_description(soup)
        icon_url = app_data.get("image", "")
        developer = extract_developer_info(app_data)
        age_rating = app_data.get("typicalAgeRange", "Не указан")

        result = {
            "app_id": app_id,
            "name": clean_text(app_data.get("name", "")),
            "short_description": short_desc,
            "full_description": full_desc,
            "rating": parse_rating(app_data),
            "rating_count": parse_rating_count(app_data),
            "categories": parse_categories(app_data),
            "icon_url": icon_url,
            "screenshots": app_data.get("screenshot", []),
            "developer": developer,
            "age_rating": age_rating,
        }

        return result

    except Exception as e:
        return None

def extract_developer_info(app_data):
    author = app_data.get("author", {})
    if isinstance(author, dict):
        return {
            "name": clean_text(author.get("name", "Не указан")),
            "url": author.get("url", ""),
        }
    elif isinstance(author, str):
        return {"name": clean_text(author), "url": ""}
    else:
        return {"name": "Не указан", "url": ""}

def extract_full_description(soup):
    description_blocks = soup.find_all("div", {"data-testid": "description"})
    if not description_blocks:
        return "Подробное описание не найдено на странице"

    all_paragraphs = []
    for block in description_blocks:
        paragraphs = block.find_all("p", class_=re.compile(r"Pg0h2jm"))
        for p in paragraphs:
            paragraph_text = process_paragraph_content(p)
            if paragraph_text.strip():
                all_paragraphs.append(paragraph_text)

    return "\n\n".join(all_paragraphs)

def process_paragraph_content(element):
    text_parts = []
    for child in element.children:
        if isinstance(child, NavigableString):
            text = str(child)
            text = text.replace("\xa0", " ")
            text = re.sub(r"\s+", " ", text)
            text_parts.append(text)
        elif isinstance(child, Tag):
            if child.name == "br":
                text_parts.append("\n")
            else:
                text_parts.append(process_paragraph_content(child))

    return clean_text(" ".join(text_parts))

def parse_rating(app_data):
    try:
        rating = app_data.get("aggregateRating", {}).get("ratingValue")
        if rating is None:
            return 0.0
        return float(rating)
    except (TypeError, ValueError):
        return 0.0

def parse_rating_count(app_data):
    try:
        count = app_data.get("aggregateRating", {}).get("ratingCount")
        if count is None:
            return 0
        return int(count)
    except (TypeError, ValueError):
        return 0

def parse_categories(app_data):
    categories = app_data.get("applicationSubCategory", [])
    if isinstance(categories, str):
        return [clean_text(categories)]
    return [clean_text(cat) for cat in categories if cat.strip()]

def get_app_ids_from_catalog_page(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        response = requests.get(url, headers=headers, timeout=8)
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")
        app_cards = soup.find_all("a", {"data-testid": "app-card"})

        app_ids = []
        for card in app_cards:
            href = card.get("href", "")
            if href.startswith("/catalog/app/"):
                app_id = href.replace("/catalog/app/", "")
                app_ids.append(app_id)

        return app_ids

    except Exception as e:
        print(f"⚠️ Ошибка при обработке страницы {url}: {str(e)}")
        return []

def main():
    print(f"🚀 Начинаем сбор данных с {MAX_PAGES} страниц каталога RuStore")

    all_app_ids = []
    for page_num in range(1, MAX_PAGES + 1):
        if page_num == 1:
            catalog_url = BASE_CATALOG_URL
        else:
            catalog_url = f"{BASE_CATALOG_URL}/page-{page_num}"

        print(f"🔄 Обработка страницы каталога: {catalog_url}")
        app_ids = get_app_ids_from_catalog_page(catalog_url)

        print(f"🔍 Найдено {len(app_ids)} приложений на странице {page_num}")
        all_app_ids.extend(app_ids)

        time.sleep(REQUEST_DELAY)

    print(f"\n✅ Всего найдено {len(all_app_ids)} приложений для проверки")

    filtered_apps = []
    print("\n🔍 Начинаем проверку приложений по категориям...")

    for app_id in tqdm(all_app_ids, desc="Проверка приложений"):
        app_url = f"https://www.rustore.ru/catalog/app/{app_id}"
        app_data = parse_rustore_app(app_url, app_id)

        if app_data and is_target_category(app_data["categories"]):
            filtered_apps.append(app_data)

        time.sleep(REQUEST_DELAY)

    print(f"\n🎯 Найдено {len(filtered_apps)} приложений, соответствующих критериям")

    if filtered_apps:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(filtered_apps, f, ensure_ascii=False, indent=2)

        category_stats = {}
        for app in filtered_apps:
            for cat in app["categories"]:
                if cat in TARGET_CATEGORIES:
                    category_stats[cat] = category_stats.get(cat, 0) + 1

        print("\n📊 Статистика по категориям:")
        for cat, count in category_stats.items():
            print(f"- {cat}: {count} приложений")

        print(f"\n💾 Результаты сохранены в файл: {OUTPUT_FILE}")

        print("\n📌 Примеры найденных приложений:")
        for i, app in enumerate(filtered_apps[:3], 1):
            print(f"{i}. {app['name']} (ID: {app['app_id']})")
            print(f"   Категории: {', '.join(app['categories'])}")
            print(f"   Рейтинг: {app['rating']} ({app['rating_count']} оценок)")
            print(f"   Возрастной рейтинг: {app['age_rating']}")
            print(f"   Разработчик: {app['developer']['name']}")
            if app["developer"]["url"]:
                print(f"   Страница разработчика: {app['developer']['url']}")
            print(f"   Иконка: {app['icon_url']}")
            print(f"   Краткое описание: {app['short_description'][:100]}{'...' if len(app['short_description']) > 100 else ''}")
    else:
        print("❌ Не найдено ни одного приложения, соответствующего критериям")

if __name__ == "__main__":
    main()