import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from telegram import Bot

driver_path = 'C:\\Users\\asppl\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe'
service = Service(driver_path)


vending_machines_sales = {}
sales_step = 5  #ИЗМЕНИТЬ ШАГ


TELEGRAM_TOKEN = '8135486958:AAEt8a8xwKSxmktXIEqjS1xjrFrqXFy9TzA'
TELEGRAM_CHAT_ID = '-4586465654'

async def send_telegram_message(message):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print(f"Сообщение отправлено: {message}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


def login(driver):
    url = 'https://cabinet.kitvending.ru/Account/Login'
    driver.get(url)
    print(f"Открыта страница {url}")


    driver.find_element(By.ID, 'LoginField').send_keys('xxxxxx')
    driver.find_element(By.ID, 'PasswordField').send_keys('xxxxxx') 


    input("Введите капчу и нажмите Enter, чтобы продолжить")


def open_sales_page(driver):
    url = 'https://cabinet.kitvending.ru/Statistics/SalesByVendingMachines'
    driver.get(url)
    print(f"Открыта страница статистики {url}")


def select_all(driver):
    try:
      
        wait = WebDriverWait(driver, 10)
        select = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'select2-selection')))
        select.click()

     
        all_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[text()='Все']")))
        all_option.click()

        print("Выбрана опция 'Все'.")
    except Exception as e:
        print(f"Ошибка при выборе опции 'Все': {e}")


def clean_sales_string(sales_string):
    clean_string = re.sub(r'\D', '', sales_string)  
    return clean_string

def check_sales(driver):
    print("Начинаем проверку продаж...")

    rows = driver.find_elements(By.XPATH, "//tr") 
    print(f"Найдено строк таблицы: {len(rows)}")  

    for row in rows:
        try:
            columns = row.find_elements(By.TAG_NAME, 'td')
            if len(columns) < 4:
                continue  
            

            name_column = columns[2].text.strip()
            print(f"Обрабатываем строку: {name_column}")

 
            number_match = re.search(r'-\s+"(\d{4,})', name_column)  
            if not number_match:
                print(f"Номер автомата не найден в строке: {name_column}")
                continue  

            vending_number = number_match.group(1)  

            if not vending_number.startswith("36"):
                print(f"Автомат с номером {vending_number} пропущен (не начинается с 36)")
                continue 

            sales_text = columns[3].text.strip() 
            clean_sales_text = clean_sales_string(sales_text)
            sales_count = int(clean_sales_text)

            if name_column not in vending_machines_sales:
                vending_machines_sales[name_column] = sales_count
                print(f"Автомат '{name_column}' добавлен с {sales_count} продажами.")  
            
    
            previous_sales = vending_machines_sales[name_column]
            if sales_count >= previous_sales + sales_step:
                message = f"Продажи автомата '{name_column}' (номер {vending_number}) увеличились до {sales_count} (было {previous_sales})."
                asyncio.run(send_telegram_message(message)) 
                print(message)
                vending_machines_sales[name_column] = sales_count  
        except Exception as e:
            print(f"Ошибка при обработке строки: {e}")


def run_script():

    try:
        driver = webdriver.Chrome(service=service)
        print("Браузер запущен успешно.")
    except Exception as e:
        print(f"Ошибка при запуске браузера: {e}")
        return
    

    login(driver)

    open_sales_page(driver)

  
    while True:
        try:
          
            print("Выбираем опцию 'Все'...")
            select_all(driver)
            print("Проверяем данные о продажах...")
            check_sales(driver)  # Проверка продаж
        except Exception as e:
            print(f"Ошибка при проверке продаж: {e}")
        
        time.sleep(30)
        driver.refresh()

   
    driver.quit()


if __name__ == '__main__':
    run_script()
