from time import sleep
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import os

from selenium.webdriver.support.wait import WebDriverWait


class DsScrapingFromBizreach():

    def __init__(self):

        # 開始メッセージ
        print("#" * 40)
        print("# 開始")
        print("#" * 40)

        # スクレイピング用のブラウザの起動
        options = Options()
        options.binary_location = (
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        )
        # options.add_argument("--headless")
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.implicitly_wait(2)
        self.vars = {}

        # 環境変数からメールとパスワードを取得する
        self.account_mailaddress = os.environ.get('ACCOUNT_MAILADDRESS')
        self.account_password = os.environ.get('ACCOUNT_PASSWORD')

        # データフレームを事前に準備する
        c = ['ID', '年齢', '性別', '都道府県', '年収(下限)', '年収(上限)', '学歴', '大学', '学部', '卒業', '英語',
             'DS経験年数', 'コアスキル']
        self.df = pd.DataFrame(data=None, index=[], columns=c)

    def save(self):

        # データフレームの内容をファイルに保存する
        self.df.to_csv("./output/data.csv", index=True, header=True)

    def end(self):

        # ブラウザを終了する
        sleep(5)
        self.driver.quit()

        # 終了メッセージ
        print("#" * 40)
        print("# 終了")
        print("#" * 40)

    def run(self):

        # BIZREACHのサイトを開く
        self.driver.get("https://cr-support.jp/")
        self.driver.set_window_size(1024, 600)

        # メールとパスワードを指定してログインする
        self.driver.find_element(By.NAME, "mailAddress").send_keys(self.account_mailaddress)
        self.driver.find_element(By.NAME, "password").send_keys(self.account_password)
        self.driver.find_element(By.ID, "jsi-login-submit").click()

        # 検索条件を入力する
        self.driver.find_element(By.CSS_SELECTOR, ".bw").click()
        self.driver.find_element(By.ID, "jsi-gnav-search").click()
        self.driver.find_element(By.NAME, "pstNm").click()
        self.driver.find_element(By.NAME, "pstNm").send_keys("データサイエンティスト")

        # 一番最初の候補者の詳細をクリックする
        self.driver.find_element(By.CSS_SELECTOR, ".bdMidlT:nth-child(1) .jsc-resume-search-button").click()

        # 次の100件（101件から200件）
        next1 = self.driver.find_element(By.XPATH, ".//a[contains(text(), '次の100件')]")
        next1.click()

        # 次の100件（201件から300件）
        next1 = self.driver.find_element(By.XPATH, ".//a[contains(text(), '次の100件')]")
        next1.click()

        # 次の100件（301件から400件）
        next1 = self.driver.find_element(By.XPATH, ".//a[contains(text(), '次の100件')]")
        next1.click()

        # 次の100件（400件から484件）
        next1 = self.driver.find_element(By.XPATH, ".//a[contains(text(), '次の100件')]")
        next1.click()

        ul = self.driver.find_element(By.XPATH, ".//ul[@id='jsi_resume_block']")
        ul.find_elements(By.XPATH, "li")[0].click()

        df_index = 0

        while (1):

            print("*" * 40)
            print(f"* {df_index + 1}件目")
            print("*" * 40)

            try:
                section = self.driver.find_element(By.XPATH, ".//section[@id='jsi_resume_detail']")
                self.driver.save_screenshot(f'./output/output_image_{df_index + 1}.png')

                id = section.find_element(By.XPATH, "..//h2[@class='fl mr10']").text
                self.df.loc[df_index, 'ID'] = id

                h_age = section.find_element(By.XPATH, "..//td[@class='pl5']")
                h_age_text = int(h_age.text.split("歳")[0].strip())

                h_gender = h_age.find_element(By.XPATH, "following-sibling::td")
                h_gender_text = h_gender.text.replace("/", "").strip()

                h_prefectures = h_gender.find_element(By.XPATH, "following-sibling::td")
                h_prefectures_text = h_prefectures.text.replace("/", "").strip()

                h_income = h_prefectures.find_element(By.XPATH, "following-sibling::td")
                h_income_text = h_income.text.replace("/", "").strip()

                income_lbound = 0
                income_ubound = 0
                if h_income_text == "500万円未満":
                    income_lbound = 500
                    income_ubound = 500
                else:
                    income_lbound = int(h_income_text.replace("万円", "").replace(",", "").split("-")[0])
                    income_ubound = int(h_income_text.replace("万円", "").replace(",", "").split("-")[1])

                print(
                    f'年齢:{h_age_text}, 性別:{h_gender_text}, 都道府県:{h_prefectures_text}, 年収(下限):{income_lbound}, 年収(上限):{income_ubound}')
                self.df.loc[df_index, '年齢'] = h_age_text
                self.df.loc[df_index, '性別'] = h_gender_text
                self.df.loc[df_index, '都道府県'] = h_prefectures_text
                self.df.loc[df_index, '年収(下限)'] = income_lbound
                self.df.loc[df_index, '年収(上限)'] = income_ubound

                p = section.find_element(By.XPATH, "..//th[text()='学歴']")
                h_background = p.find_element(By.XPATH, "..").find_elements(By.XPATH, ".//li")[0].text.split("/")[
                    0].strip()
                h_academic_text = p.find_element(By.XPATH, "..").find_elements(By.XPATH, ".//li")[0].text.split("/")[
                    1].strip()

                h_academic_school = ""
                h_academic_faculty = ""
                h_academic_year = ""
                hx = h_academic_text.split("（20")
                if (len(hx) > 1):
                    h_academic_year = "20" + hx[1].replace("）", "").strip(" ")
                else:
                    hx = h_academic_text.split("（19")
                    if (len(hx) > 1):
                        h_academic_year = "19" + hx[1].replace("）", "").strip(" ")

                hs = hx[0].split("\u3000")
                if (len(hs) > 1):
                    h_academic_faculty = hs[1].strip()
                if len(hs[0].split(' ')) > 1:
                    h_academic_school = hs[0].split(' ')[0].strip()
                    h_academic_faculty = hs[0].split(' ')[1].strip() + ' ' + h_academic_faculty
                else:
                    h_academic_school = hs[0].strip()

                self.df.loc[df_index, '学歴'] = h_background
                self.df.loc[df_index, '大学'] = h_academic_school
                self.df.loc[df_index, '学部'] = h_academic_faculty
                self.df.loc[df_index, '卒業'] = h_academic_year

                e = section.find_element(By.XPATH, "..//th[text()='言語']")
                e_level = \
                    e.find_element(By.XPATH, "..").find_elements(By.XPATH, ".//li[contains(text(), '英語')]")[
                        0].text.split(
                        "/")[1].strip()

                self.df.loc[df_index, '英語'] = e_level

                s_year_number = 0
                s = section.find_element(By.XPATH, "..//th[text()='経験職種']")
                s_ds = s.find_element(By.XPATH, "..").find_elements(By.XPATH, ".//span[text()='データサイエンティスト']")
                if len(s_ds) > 0:
                    s_year = s_ds[0].find_element(By.XPATH, "../..").find_elements(By.XPATH, ".//td")
                    if len(s_year) > 1:
                        s_year_number = int(s_year[1].text.replace("年", ""))

                self.df.loc[df_index, 'DS経験年数'] = s_year_number

                print(
                    f'学歴:{h_background}, 大学:{h_academic_school}, 学部:{h_academic_faculty}, 卒業:{h_academic_year}, 英語:{e_level}, DS経験年数:{s_year_number}')

                y = section.find_elements(By.XPATH, ".//dt[contains(text(), '活かせる経験・知識・能力')]")
                if len(y) > 0:
                    z = y[0].find_element(By.XPATH, "..").find_elements(By.XPATH, ".//li[@class='jsc_kwHighlight']")

                    skills = []
                    for e in z:
                        try:
                            skills.append(e.text)
                        except Exception as e:
                            print("例外発生")
                            print(e)

                    print(f'コアスキル:{"#".join(skills)}')
                    self.df.loc[df_index, 'コアスキル'] = "#".join(skills)
                else:
                    self.df.loc[df_index, 'コアスキル'] = ""

            except Exception as e:
                print("例外発生2")
                print(e)

            sleep(0.1)

            df_index += 1

            #if df_index >= 100:
            if df_index >= 84:
                    return

            btns = self.driver.find_elements(By.LINK_TEXT, "次へ »")
            btns[0].click()

if __name__ == '__main__':
    t = DsScrapingFromBizreach()

    try:
        t.run()
    except Exception as e:
        print('例外発生です')
        print(e)
    t.save()
    t.end()
