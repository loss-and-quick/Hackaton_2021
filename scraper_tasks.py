from selenium import webdriver
import os
from PIL import Image
import time
from io import BytesIO
from bs4 import BeautifulSoup

ffprofile = webdriver.FirefoxProfile()
ffprofile.add_extension('uBlock0_1.33.3b0.firefox.signed.xpi')
ffprofile.set_preference("extensions.adblockplus.currentVersion", "1.33.3b0")
browser = webdriver.Firefox(ffprofile,executable_path="C:\\Users\\minicx\\PycharmProjects\\pythonProject\\geckodriver.exe",)
browser.set_window_size(1212,1045)


def watermark_with_transparency(input_image_path,
                                output_image_path,
                                watermark_image_path,
                                ):
    base_image = Image.open(input_image_path)
    watermark = Image.open(watermark_image_path)
    width1,height1=watermark.size
    width, height = base_image.size

    transparent = Image.new('RGBA', (width, height+15), (0, 0, 0, 0))

    transparent.paste(base_image, (0, 0))
    transparent.paste(watermark, ((width - width1), (height - height1)+10), mask=watermark)

    transparent.save(output_image_path)

def full_screenshot(driver, save_path):
    # initiate value
    save_path = save_path + '.png' if save_path[-4::] != '.png' else save_path
    img_li = []  # to store image fragment
    offset = 0  # where to start

    # js to get height
    height = driver.execute_script('return Math.max('
                                   'document.documentElement.clientHeight, window.innerHeight);')

    # js to get the maximum scroll height
    # Ref--> https://stackoverflow.com/questions/17688595/finding-the-maximum-scroll-position-of-a-page
    max_window_height = driver.execute_script('return Math.max('
                                              'document.body.scrollHeight, '
                                              'document.body.offsetHeight, '
                                              'document.documentElement.clientHeight, '
                                              'document.documentElement.scrollHeight, '
                                              'document.documentElement.offsetHeight);')

    # looping from top to bottom, append to img list
    # Ref--> https://gist.github.com/fabtho/13e4a2e7cfbfde671b8fa81bbe9359fb

    while offset < max_window_height:

        # Scroll to height
        driver.execute_script(f'window.scrollTo(0, {offset});')
        img = Image.open(BytesIO((driver.get_screenshot_as_png())))
        img_li.append(img)
        offset += height

    # Stitch image into one
    # Set up the full screen frame
    img_frame_height = sum([img_frag.size[1] for img_frag in img_li])
    img_frame = Image.new('RGB', (img_li[0].size[0], img_frame_height))
    offset = 0
    for img_frag in img_li:
        img_frame.paste(img_frag, (0, offset))
        offset += img_frag.size[1]
    img_frame.save(save_path)

def get_option_math_pro(option_number)-> list:
    browser.get('https://ege.sdamgia.ru/')
    # здесь можно доработать
    time.sleep(2.5)
    while (str(browser.current_url)!='https://ege.sdamgia.ru/'):
        continue
    ###########
    #    html.Html body.Page div.Root div.App div.PageLayout.StartPage div.PageLayout-Grid div.PageLayout-Content main.PageLayout-Main section.Section.OurVariants div.OurVariants-Grid a.Link.VariantLink.OurVariants-Link
    browser.find_elements_by_css_selector("html.Html body.Page div.Root div.App div.PageLayout.StartPage div.PageLayout-Grid div.PageLayout-Content main.PageLayout-Main section.Section.OurVariants div.OurVariants-Grid a.Link.VariantLink.OurVariants-Link")[option_number-1].click()

    time.sleep(1)

    tasks_urls=[]#получаем ссылки на задания
    tasks=[]#сами задания
    #
    # /html/body/div[1]/div[5]/div[6]/div[2]/div/div[1]/div[1]/span/a
    # /html/body/div[1]/div[5]/div[6]/div[4]/div/div[1]/div[1]/span/a
    for i in range(2,((19+1)*2),2):
        print(i/2,browser.find_element_by_xpath('/html/body/div[1]/div[5]/div[6]/div['+str(i)+']/div/div[1]/div[1]/span/a').get_attribute('href'))
        tasks_urls.append(str(browser.find_element_by_xpath('/html/body/div[1]/div[5]/div[6]/div['+str(i)+']/div/div[1]/div[1]/span/a').get_attribute('href')))

    #обрабатываем задания
    for i in range(len(tasks_urls)):

        browser.get(tasks_urls[i])
        time.sleep(0.5)

        #общая высота и общий скриншот
        # Я шатал верстальщиков sdamgia
        multi=35#множитель
        try:
            browser.find_element_by_xpath("//*[contains(text(), 'Источник')]")
            multi+=browser.find_element_by_xpath("//*[contains(text(), 'Источник')]").size["height"]
        except:
            pass
        try:
            browser.find_element_by_xpath("//*[contains(text(), 'Классификатор стереометрии: ')]")
            multi += browser.find_element_by_xpath("//*[contains(text(), 'Классификатор стереометрии: ')]").size["height"]
        except:
            pass
        try:
            browser.find_element_by_xpath("//*[contains(text(), 'Раздел кодификатор')]")
            multi += browser.find_element_by_xpath("//*[contains(text(), 'Раздел кодификатор')]").size["height"]
        except:
            pass
        try:
            #Классификатор базовой части
            browser.find_element_by_xpath("//*[contains(text(), 'Классификатор базовой части')]")
            multi+=browser.find_element_by_xpath("//*[contains(text(), 'Классификатор базовой части')]").size["height"]
        except:
            pass

        size = browser.find_element_by_class_name('prob_maindiv').size
        total_height = (size['height']-browser.find_element_by_class_name('minor').size["height"]-multi)
        full_screenshot(browser, 'tasks\\full_' + str(i + 1) + '.png')
        #

        # скриншот ответа  и сам ответ
        location = browser.find_element_by_xpath(
            '//*[@id="sol' + str(tasks_urls[i])[str(tasks_urls[i]).find('id=') + 3:] + '"]').location
        size = browser.find_element_by_xpath(
            '//*[@id="sol' + str(tasks_urls[i])[str(tasks_urls[i]).find('id=') + 3:] + '"]').size
        x = location['x'];
        y = location['y'];
        width = location['x'] + size['width'];
        heightanswer = size['height']
        height = location['y'] + size['height'];
        #
        # редактирование
        im = Image.open('tasks\\full_' + str(i + 1) + '.png')
        im = im.crop((int(x), int(y), int(width), int(height)))
        im.save('tasks\\full_answer_' + str(i+1) + '.png')
        watermark_with_transparency('tasks\\full_answer_' + str(i+1) + '.png', 'tasks\\full_answer_' + str(i+1) + '.png',
                                    'watermark.png')
        #
        #получение ответа
        content = content = BeautifulSoup(browser.page_source).get_text().replace("\n", "").strip()
        answer = ""
        for y in content[content.rfind("Ответ:") + 6:content.rfind('.', content.rfind("Ответ:"))]:
            if not y.isupper():
                answer += y
            else:
                break
        answer=answer.strip()
        if len(answer)==2 and answer.find(')')!=-1 or answer=="а)  б)":
            answer = "Ответ в решении"
        elif answer=='' or answer ==  ' ':
            answer = "Ответ в решении"
        #
        # скриншот задания
        location = browser.find_element_by_class_name('pbody').location
        size = browser.find_element_by_class_name('pbody').size
        x = location['x'];
        y = location['y'];
        width = location['x'] + size['width'];
        height = y + (total_height - heightanswer);
        #
        #редактирование

        im = Image.open('tasks\\full_' + str(i + 1) + '.png')
        im = im.crop((int(x), int(y), int(width), int(height)))
        im.save('tasks\\task_' + str(i+1) + '.png')
        watermark_with_transparency('tasks\\task_' + str(i+1) + '.png', 'tasks\\task_' + str(i+1) + '.png','watermark.png')
        #
        #добавление путей картинок и ответа в массив,а а также удаление общего скриншота
        tasks.append([answer, os.path.join('tasks','task_' + str(i+1) + '.png'), os.path.join('tasks','full_answer_' + str(i+1) + '.png')])
        os.remove(os.path.join("tasks",'full_' + str(i + 1) + '.png'))

    return tasks

def get_options_math_pro(numbers_tasks)-> list:
    browser.get('https://ege.sdamgia.ru/')
    # здесь можно доработать
    time.sleep(2.5)
    while (str(browser.current_url)!='https://ege.sdamgia.ru/'):
        continue
    ###########
    if numbers_tasks<=12:
        for i in range(1,numbers_tasks+1):#первые 12 заданий
            button= browser.find_element_by_css_selector("div.ConstructorForm-Row:nth-child("+str(i+1)+") > div:nth-child(1) > button:nth-child(3)")
            button.click()
    else:
        for i in range(1,numbers_tasks+1):#первые 12 заданий
            if i==13:
                break
            button= browser.find_element_by_css_selector("div.ConstructorForm-Row:nth-child("+str(i+1)+") > div:nth-child(1) > button:nth-child(3)")
            button.click()

        for i in range(13,numbers_tasks+1):# развернутые вопросы с 13 по 19
            button = browser.find_element_by_css_selector(
                "div.ConstructorForm-Row:nth-child(" + str(i + 2) + ") > div:nth-child(1) > button:nth-child(3)")
            button.click()

    time.sleep(1)
    button=browser.find_element_by_css_selector('.ConstructorForm-SubmitButton')
    button.click()#получаем вариант
    browser.get(str(browser.current_url).replace('True',"False"))
    tasks_urls=[]#получаем ссылки на задания
    tasks=[]#сами задания

    for i in range(2,((numbers_tasks+1)*2),2):
        print(i/2,browser.find_element_by_xpath('/html/body/div[1]/div[5]/div[3]/div['+str(i)+']/div/div[1]/div[1]/span/a').get_attribute('href'))
        tasks_urls.append(str(browser.find_element_by_xpath('/html/body/div[1]/div[5]/div[3]/div['+str(i)+']/div/div[1]/div[1]/span/a').get_attribute('href')))

    #обрабатываем задания
    for i in range(len(tasks_urls)):

        browser.get(tasks_urls[i])
        time.sleep(0.5)

        #общая высота и общий скриншот
        # Я шатал верстальщиков sdamgia
        multi=35#множитель
        try:
            browser.find_element_by_xpath("//*[contains(text(), 'Источник')]")
            multi+=browser.find_element_by_xpath("//*[contains(text(), 'Источник')]").size["height"]
        except:
            pass
        try:
            browser.find_element_by_xpath("//*[contains(text(), 'Классификатор стереометрии: ')]")
            multi += browser.find_element_by_xpath("//*[contains(text(), 'Классификатор стереометрии: ')]").size["height"]
        except:
            pass
        try:
            browser.find_element_by_xpath("//*[contains(text(), 'Раздел кодификатор')]")
            multi += browser.find_element_by_xpath("//*[contains(text(), 'Раздел кодификатор')]").size["height"]
        except:
            pass
        try:
            #Классификатор базовой части
            browser.find_element_by_xpath("//*[contains(text(), 'Классификатор базовой части')]")
            multi+=browser.find_element_by_xpath("//*[contains(text(), 'Классификатор базовой части')]").size["height"]
        except:
            pass

        size = browser.find_element_by_class_name('prob_maindiv').size
        total_height = (size['height']-browser.find_element_by_class_name('minor').size["height"]-multi)
        full_screenshot(browser, 'tasks\\full_' + str(i + 1) + '.png')
        #

        # скриншот ответа  и сам ответ
        location = browser.find_element_by_xpath(
            '//*[@id="sol' + str(tasks_urls[i])[str(tasks_urls[i]).find('id=') + 3:] + '"]').location
        size = browser.find_element_by_xpath(
            '//*[@id="sol' + str(tasks_urls[i])[str(tasks_urls[i]).find('id=') + 3:] + '"]').size
        x = location['x'];
        y = location['y'];
        width = location['x'] + size['width'];
        heightanswer = size['height']
        height = location['y'] + size['height'];
        #
        # редактирование
        im = Image.open('tasks\\full_' + str(i + 1) + '.png')
        im = im.crop((int(x), int(y), int(width), int(height)))
        im.save('tasks\\full_answer_' + str(i+1) + '.png')
        watermark_with_transparency('tasks\\full_answer_' + str(i+1) + '.png', 'tasks\\full_answer_' + str(i+1) + '.png',
                                    'watermark.png')
        #
        #получение ответа
        content = content = BeautifulSoup(browser.page_source).get_text().replace("\n", "").strip()
        answer = ""
        for y in content[content.rfind("Ответ:") + 6:content.rfind('.', content.rfind("Ответ:"))]:
            if not y.isupper():
                answer += y
            else:
                break
        answer=answer.strip()
        if len(answer)==2 and answer.find(')')!=-1 or answer=="а)  б)":
            answer = "Ответ в решении"
        elif answer=='' or answer ==  ' ':
            answer = "Ответ в решении"
        #
        # скриншот задания
        location = browser.find_element_by_class_name('pbody').location
        size = browser.find_element_by_class_name('pbody').size
        x = location['x'];
        y = location['y'];
        width = location['x'] + size['width'];
        height = y + (total_height - heightanswer);
        #
        #редактирование

        im = Image.open('tasks\\full_' + str(i + 1) + '.png')
        im = im.crop((int(x), int(y), int(width), int(height)))
        im.save('tasks\\task_' + str(i+1) + '.png')
        watermark_with_transparency('tasks\\task_' + str(i+1) + '.png', 'tasks\\task_' + str(i+1) + '.png','watermark.png')
        #
        #добавление путей картинок и ответа в массив,а а также удаление общего скриншота
        tasks.append([answer, os.path.join('tasks','task_' + str(i+1) + '.png'), os.path.join('tasks','full_answer_' + str(i+1) + '.png')])
        os.remove(os.path.join("tasks",'full_' + str(i + 1) + '.png'))

    return tasks


# broken
# def get_options_rus(numbers_tasks)-> list:
#     browser.get('https://rus-ege.sdamgia.ru/')
#     # здесь можно доработать
#
#     while (str(browser.current_url)!='https://rus-ege.sdamgia.ru/'):
#         continue
#     ###########
#     time.sleep(3)
#     if numbers_tasks<=26:
#         #
#         #div.ConstructorForm-Row:nth-child(2) > div:nth-child(1) > button:nth-child(3)
#         #div.ConstructorForm-Row:nth-child(3) > div:nth-child(1) > button:nth-child(3)
#         for i in range(2,numbers_tasks+2):#первые 26 заданий
#             button= browser.find_element_by_css_selector("div.ConstructorForm-Row:nth-child("+str(i)+") > div:nth-child(1) > button:nth-child(3)")
#             button.click()
#     else:
#         for i in range(2,numbers_tasks+1):#первые 26 заданий
#             button= browser.find_element_by_css_selector("div.ConstructorForm-Row:nth-child("+str(i)+") > div:nth-child(1) > button:nth-child(3)")
#             button.click()
#         button= browser.find_element_by_css_selector("div.ConstructorForm-Row:nth-child(29) > div:nth-child(1) > button:nth-child(3)")
#         button.click()
#
#
#
#     time.sleep(2)
#     button=browser.find_element_by_css_selector('.ConstructorForm-SubmitButton')
#     button.click()#получаем вариант
#     browser.get(str(browser.current_url).replace('True',"False"))
#     tasks_urls=[]#получаем ссылки на задания
#     tasks=[]#сами задания
#
#     for i in range(2,((numbers_tasks+1)*2),2):
#         print(i/2,browser.find_element_by_xpath('/html/body/div[1]/div[5]/div[3]/div['+str(i)+']/div/div[1]/div[1]/span/a').get_attribute('href'))
#         tasks_urls.append(str(browser.find_element_by_xpath('/html/body/div[1]/div[5]/div[3]/div['+str(i)+']/div/div[1]/div[1]/span/a').get_attribute('href')))
#
#     #обрабатываем задания
#     for i in range(len(tasks_urls)):
#
#         browser.get(tasks_urls[i])
#         time.sleep(0.5)
#
#         #общая высота и общий скриншот
#         # Я шатал верстальщиков sdamgia
#         multi=35#множитель
#         try:
#             browser.find_element_by_xpath("//*[contains(text(), 'Актуальность')]")
#             multi+=browser.find_element_by_xpath("//*[contains(text(), 'Актуальность')]").size["height"]
#         except:
#             pass
#         try:
#             browser.find_element_by_xpath("//*[contains(text(), 'Сложность: ')]")
#             multi += browser.find_element_by_xpath("//*[contains(text(), 'Сложность: ')]").size["height"]
#         except:
#             pass
#         try:
#             browser.find_element_by_xpath("//*[contains(text(), 'Раздел кодификатора')]")
#             multi += browser.find_element_by_xpath("//*[contains(text(), 'Раздел кодификатора')]").size["height"]
#         except:
#             pass
#         #fixed need
#         try:
#             #Классификатор базовой части
#             browser.find_element_by_xpath("//*[contains(text(), 'Раздел кодификатора ФИПИ: ')]")
#             multi+=browser.find_element_by_xpath("//*[contains(text(), 'Раздел кодификатора ФИПИ: ')]").size["height"]
#         except:
#             pass
#         try:
#             #Классификатор базовой части
#             browser.find_element_by_xpath("//*[contains(text(), 'Правило:')]")
#             multi+=browser.find_element_by_xpath("//*[contains(text(), 'Правило:')]").size["height"]
#         except:
#             pass
#         try:
#             #Классификатор базовой части
#             browser.find_element_by_xpath("//*[contains(text(), 'Источник:')]")
#             multi+=browser.find_element_by_xpath("//*[contains(text(), 'Источник:')]").size["height"]
#         except:
#             pass
#
#         size = browser.find_element_by_class_name('prob_maindiv').size
#         total_height = (size['height']-browser.find_element_by_class_name('minor').size["height"]-multi)
#         full_screenshot(browser, 'tasks\\full_' + str(i + 1) + '.png')
#         #
#
#         # скриншот ответа  и сам ответ
#         location = browser.find_element_by_xpath(
#             '//*[@id="sol' + str(tasks_urls[i])[str(tasks_urls[i]).find('id=') + 3:] + '"]').location
#         size = browser.find_element_by_xpath(
#             '//*[@id="sol' + str(tasks_urls[i])[str(tasks_urls[i]).find('id=') + 3:] + '"]').size
#         x = location['x'];
#         y = location['y'];
#         width = location['x'] + size['width'];
#         heightanswer = size['height']
#         height = location['y'] + size['height'];
#         #
#         # редактирование
#         im = Image.open('tasks\\full_' + str(i + 1) + '.png')
#         im = im.crop((int(x), int(y), int(width), int(height)))
#         im.save('tasks\\full_answer_' + str(i+1) + '.png')
#         watermark_with_transparency('tasks\\full_answer_' + str(i+1) + '.png', 'tasks\\full_answer_' + str(i+1) + '.png',
#                                     'watermark.png')
#         #
#         #получение ответа
#         try:
#             content = BeautifulSoup(browser.page_source.replace(
#                 '<div class="answer" style="display:none"><span style="letter-spacing: 2px;">Ответ:', "")).get_text()
#         except:
#             content = BeautifulSoup(browser.page_source).get_text().split()
#         answer = ""
#         if content.rfind("Ответ:")!=-1 and i!=27:
#             for y in content[content.rfind("Ответ:") + 6:content.rfind('.', content.rfind("Ответ:"))]:
#                 if not y.isupper():
#                     answer += y
#                 else:
#                     break
#         else:
#             answer = "Ответ в решении"
#         answer=answer.strip()
#
#         #
#         # скриншот задания
#         location = browser.find_element_by_class_name('pbody').location
#         size = browser.find_element_by_class_name('pbody').size
#         x = location['x'];
#         y = location['y'];
#         width = location['x'] + size['width'];
#         #
#         #редактирование
#         height = y + (total_height - heightanswer );
#         im = Image.open('tasks\\full_' + str(i + 1) + '.png')
#         im = im.crop((int(x), int(y), int(width), int(height)))
#         im.save('tasks\\task_' + str(i+1) + '.png')
#         watermark_with_transparency('tasks\\task_' + str(i+1) + '.png', 'tasks\\task_' + str(i+1) + '.png','watermark.png')
#         #
#         #добавление путей картинок и ответа в массив,а а также удаление общего скриншота
#         tasks.append([answer, os.path.join('tasks','task_' + str(i+1) + '.png'), os.path.join('tasks','full_answer_' + str(i+1) + '.png')])
#         os.remove(os.path.join("tasks",'full_' + str(i + 1) + '.png'))
#
#     return tasks
#


# for i in get_option_math_pro(15):
#      print(i[2],i[0])
# time.sleep(100000)
# browser.close()