import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import numpy as np
from pyzbar.pyzbar import decode
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Qrcodeextract:
    def __init__(self, master):
        self.master = master
        self.create_window()
        self.data = []  # Store extracted data for each QR code URL

    def create_window(self):
        # 创建子窗口
        self.window = tk.Toplevel(self.master)
        self.window.title("批量提取二维码")
        self.window.geometry("800x400")

        # 选择文件夹按钮
        self.select_folder_button = tk.Button(self.window, text="选择文件夹", command=self.select_folder)
        self.select_folder_button.pack(pady=20)

        # 显示当前选择的文件夹标签
        self.folder_label = tk.Label(self.window, text="未选择文件夹")
        self.folder_label.pack(pady=20)

        # 进度条
        self.progress = ttk.Progressbar(self.window, length=400, mode='determinate')
        self.progress.pack(pady=20)

        # 显示解析结果
        self.result_label = tk.Label(self.window, text="", wraplength=700)
        self.result_label.pack(pady=20)

    def select_folder(self):
        # 弹出文件夹选择对话框
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            # 更新标签显示当前选择的文件夹路径
            self.folder_label.config(text=f"当前选择的文件夹: {folder_selected}")

            # 解析文件夹中的二维码
            self.decode_qrcodes_in_folder(folder_selected)

    def decode_qrcodes_in_folder(self, folder_path):
        # 启动浏览器
        self.driver = webdriver.Chrome()
        self.driver.get("https://accounts.douban.com/passport/login")
        self.folder_path = folder_path
        # messagebox.showinfo("提示", "请在打开的浏览器中完成登录，然后点击确定继续")
        self.after_login = tk.Button(self.window, text="请登录完成后点击此按钮继续...", command=self.continue_after_login)
        self.after_login.pack(pady=20)    

    def continue_after_login(self):
        self.after_login.destroy()
        # 获取文件夹中的所有图像文件
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
        image_files = [os.path.join(self.folder_path, f) for f in os.listdir(self.folder_path) 
                       if os.path.splitext(f)[1].lower() in image_extensions]

        if not image_files:
            self.result_label.config(text="没有找到任何图像文件。")
            return

        total_files = len(image_files)
        self.progress['value'] = 0
        self.window.update_idletasks()

        # 遍历每个图像文件并解析二维码
        for idx, image_file in enumerate(image_files):
            detector = cv2.wechat_qrcode.WeChatQRCode()
            image = cv2.imdecode(np.fromfile(image_file,dtype=np.uint8),-1)
            qr_codes, _ = detector.detectAndDecode(image)

            for qr_code in qr_codes:
                url = qr_code
                self.result_label.config(text=f"正在处理: {url}")
                self.window.update_idletasks()

                self.driver.get(url)

                # 获取页面的相关数据 (示例)
                try:

                    # 等待按钮可以点击
                    element = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[1]/a'))  # 根据实际情况更改定位方式和值
                    )
                    url = element.get_attribute("href")
                    element.click()

                    name = self.driver.find_element(By.XPATH, '//*[@id="db-usr-profile"]/div[2]/h1').text.strip()  # 假设这是页面的用户名称
                    nickname = self.driver.find_element(By.XPATH, '//*[@id="profile"]/div/div[2]/div[1]/div/div').text.strip()  # 假设这是用户昵称
                    ip_location = self.driver.find_element(By.XPATH, '//*[@id="profile"]/div/div[2]/div[1]/div/a').text.strip()  # 假设IP地址位置
                    create_time = self.driver.find_element(By.XPATH, '//*[@id="profile"]/div/div[2]/div[1]/div/div/br[1]').text.split("加入")[0].strip()   # 假设创建时间 
                    # visited = self.driver.find_element(By.XPATH, '//*[@id="movie"]/h2/span/a[2]').text.split("部看过")[0].strip()  # 当前访问时间 
                    a_tags = self.driver.find_elements(By.XPATH, '//*[@id="movie"]/h2/span/a')
                    # 遍历所有 a 标签
                    for a_tag in a_tags:
                        text = a_tag.text
                        if text.endswith("部看过"):
                            # 获取“部看过”之前的部分
                            visited = text.split("部看过")[0].strip()
                            break  # 找到第一个符合条件的标签后可以退出循环
                    
                    # 将数据保存到列表
                    self.data.append({
                        "FileName": os.path.basename(image_file),
                        "Name": name,
                        "Url": url,
                        "NickName": nickname,
                        "IPLocation": ip_location,
                        "CreateTime": create_time,
                        "Visited": visited
                    })
                except Exception as e:
                    print(f"Error while processing {url}: {e}")

            # 更新进度条
            self.progress['value'] = (idx + 1) / total_files * 100
            self.window.update_idletasks()
        self.driver.quit()
        # 保存数据到Excel
        self.save_to_excel()
    def save_to_excel(self):
        if self.data:
            df = pd.DataFrame(self.data)
            save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                                     filetypes=[("Excel files", "*.xlsx")])
            if save_path:
                df.to_excel(save_path, index=False)
                messagebox.showinfo("提示", f"数据已保存到 {save_path}")
        else:
            messagebox.showinfo("提示", "没有数据可保存。")

# 主程序
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    app = Qrcodeextract(root)
    root.mainloop()
