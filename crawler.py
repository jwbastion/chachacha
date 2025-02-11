from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

import time, random, re
import pandas as pd

driver = webdriver.Chrome()

sequence = []
page_num = 1

# 사진 등록된 차량들에서 url에 들어가는 sequence 값 추출
while True:
    url = f'https://www.kbchachacha.com/public/search/main.kbc#!?countryOrder=2&page={page_num}&sort=-orderDate&useCode=002006'
    driver.get(url)

    time.sleep(random.uniform(2, 5))
    items = driver.find_elements(By.CSS_SELECTOR, '.area')

    # 사진 등록이 안된 차량 매물이 나오는 시점에서 break
    if not items: break

    # 같은 클래스 이름을 공유하지만 data-car-seq 정보가 없다면 추가 X
    for item in items:
        seq = item.get_attribute('data-car-seq')
        if seq is not None:
            sequence.append(seq)

    page_num += 1

# sequence 값 csv 형식으로 저장
seq_df = pd.DataFrame(sequence, columns=['시퀀스']).reset_index(drop=True)
seq_df.index += 1
seq_df.to_csv('seq_data.csv', encoding='utf-8-sig', index_label='번호')

data = []

# sequence 값으로 각 차량들의 페이지에 접속하여 필요한 정보들을 크롤링
for seq in sequence:
    temp = []
    try:
        url = f'https://www.kbchachacha.com/public/car/detail.kbc?carSeq={seq}'
        driver.get(url)

        time.sleep(random.uniform(2, 5))

        place = driver.find_element(By.CSS_SELECTOR, '.txt-info > span:nth-of-type(4)').text

        name = driver.find_element(By.CSS_SELECTOR, '.car-buy-name').text.replace('\n', ' ')
        name = re.sub(r"^\([^)]*\)", "", name).strip()

        price = driver.find_element(By.CSS_SELECTOR, '.car-buy-price > div > dl > dd > strong').text

        relief = driver.find_element(By.CSS_SELECTOR, '.price-tooltip-wrap > strong > strong').text

        info_list = driver.find_elements(By.CSS_SELECTOR, '.detail-info01 > table > tbody > tr > td')
        info = [data.text for data in info_list]
        info = info[:5] + info[7:9]

        temp.append(name)
        temp.append(place)
        temp.append(price)
        temp.append(relief)
        temp.extend(info)

        # data 리스트에 car_df에 들어갈 행들을 추가
        data.append(temp)

    # TimeoutException 처리
    except TimeoutException:
        print(f"TimeoutException 발생 - {seq} 페이지 로드 실패")
        time.sleep(10)  # 10초 대기 후 재시도
        continue

    # StaleElementReferenceException 처리
    except StaleElementReferenceException:
        print(f"StaleElementReferenceException 발생 - {seq} 페이지 요소 오류")
        time.sleep(5)  # 5초 대기 후 재시도
        continue

    # Exception 처리
    except Exception as e:
        print(f"알 수 없는 오류 발생 - {seq} : {e}")
        continue  # 예외 발생 시 해당 seq 건너뛰고 계속 진행

driver.quit()

# data를 csv 형식으로 저장
columns = ['모델', '지역', '가격', '시세', '차량번호', '연식', '주행거리', '연료', '변속기', '배기량', '색상']
car_df = pd.DataFrame(data, columns=columns).reset_index(drop=True)
car_df.index += 1
car_df.to_csv('car_data.csv', encoding='utf-8-sig', index_label='번호')
