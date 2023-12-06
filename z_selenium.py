import time
from selenium.webdriver import Chrome, ChromeOptions

opt = ChromeOptions()
opt.add_argument('--no-sandbox')  # 解决DevToolsActivePort文件不存在的报错
opt.add_argument('window-size=1920x3000')  # 设置浏览器分辨率
opt.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
opt.add_argument('--hide-scrollbars')  # 隐藏滚动条，应对一些特殊页面
opt.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片，提升运行速度
opt.add_argument('--headless')  # 无界面模式
driver = Chrome(options=opt)
driver.get('https://www.baidu.com')
# driver.switch_to.frame('')  # 如果存在多个frame 嵌套页面则用这个语句定位
text_input = driver.find_element('id', 'kw')
text_input.send_keys('人民币')
time.sleep(2)
driver.find_element('id', 'su').click()
time.sleep(3)
# JS滑动操作
driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
time.sleep(3)

# 获取当前页面源码数据
print(driver.page_source)

# time.sleep(10)

driver.quit()
