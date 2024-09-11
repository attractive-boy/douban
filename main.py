from datetime import datetime
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import os
import random
from tkinter import ttk
import requests
import asyncio
import aiohttp
from multiprocessing import Process
import webbrowser

import moonyun


class FileHandle(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("文件名精灵v1.0")
        self.geometry("800x600")
        self.files = []

        # 创建按钮
        self.create_buttons()

        # 创建表格
        self.create_table()

    def create_buttons(self):
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.buttons = [
            ("添加文件", self.add_file),
            ("数字编号", self.number_files),
            ("疯狂乱序", self.shuffle_files),
            ("执行修改", self.modify_files),
            ("清空列表", self.clear_list),
            ("恢复原名", self.restore_names),
            ("下载图片", self.download_images),
            ("月球云系统", self.moon_cloud_system)
        ]

        for text, command in self.buttons:
            button = ttk.Button(button_frame, text=text, command=command)
            button.pack(side=tk.LEFT, padx=5)

    def create_table(self):
        self.table_frame = tk.Frame(self)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        # 创建表头
        self.headers = ["名称", "预览", "状态"]
        self.tree = ttk.Treeview(self.table_frame, columns=self.headers, show="headings")

        for header in self.headers:
            self.tree.heading(header, text=header)
            self.tree.column(header, width=200)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建滚动条
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')

    def add_file(self):
        folder_path = filedialog.askdirectory(title="选择文件夹")

        if folder_path:
            # 列出文件夹中的所有文件
            file_paths = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            if file_paths:
                for path in file_paths:
                    file_name = os.path.basename(path)
                    new_file_name = file_name
                    state = ''
                    self.files.append([path, file_name, new_file_name, state])
                self.update_table()

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.files:
            self.tree.insert('', 'end', values=row[1:])

    def clear_list(self):
        self.files = []
        self.update_table()

    def number_files(self):
        self.show_modify_popup()

    def show_modify_popup(self):
        def on_apply():
            selected_style = style_var.get()
            custom_pattern = self.input_box_arr[int(selected_style)].get() if self.input_box_arr[int(selected_style)] != None else ""
            try:
                start_number = int(self.start_number_entry.get() or "1")
                number_length = int(self.number_length_entry.get() or "1")
                increment = int(self.increment_entry.get() or "1")
                padding_char = self.padding_char_entry.get() or "0"
            except ValueError as e:
                messagebox.showerror("错误", f"转换值为整数时出错: {e}")
                return

            for i, file_data in enumerate(self.files):
                original_name, extension = os.path.splitext(file_data[1])
                number = str(start_number + i * increment)
                #如果长度不够 用padding_char填充
                if len(number) < number_length:
                    number = padding_char * (number_length - len(number)) + number

                if selected_style == 1:
                    new_name = f"{custom_pattern}{number}"
                elif selected_style == 2:
                    new_name = f"{number}{custom_pattern}"
                elif selected_style == 3:
                    new_name = f"{original_name}{number}"
                elif selected_style == 4:
                    new_name = f"{number}{original_name}"
                elif selected_style == 5 and custom_pattern:
                    new_name = custom_pattern.replace("<self>", original_name).replace("<#>", number)
                else:
                    new_name = original_name

                file_data[2] = new_name + extension
                file_data[3] = ""

            self.update_table()
            popup.destroy()

        popup = tk.Toplevel(self)
        popup.title("数字编号")

        style_var = tk.IntVar(value=1)

        # 修改方式标签
        tk.Label(popup, text='修改方式').pack(pady=5,anchor='w', expand=True)

        styles = [
            ("样式一", "+ 数字"),
            ("样式二", "数字 +"),
            ("样式三", "文件名 + 数字"),
            ("样式四", "数字 + 文件名"),
            ("自定义", "注:<self>代表原文件名,<#>代表编号")
        ]
        self.input_box_arr = [None] * 6

        for idx, (label_text, suffix_text) in enumerate(styles, start=1):
            frame = tk.Frame(popup)
            frame.pack(pady=2,anchor='w', expand=True)

            checkbox = tk.Checkbutton(frame, variable=style_var, onvalue=idx, offvalue=0)
            checkbox.pack(side=tk.LEFT)

            tk.Label(frame, text=label_text).pack(side=tk.LEFT)


            if idx < 5:
                if idx == 1:             
                    input_box = tk.Entry(frame, width=40)
                    input_box.pack(side=tk.LEFT, padx=5)
                    suffix_label = tk.Label(frame, text=suffix_text)
                    suffix_label.pack(side=tk.LEFT)
                    self.input_box_arr[1] = input_box
                elif idx == 2:
                    suffix_label = tk.Label(frame, text=suffix_text)
                    suffix_label.pack(side=tk.LEFT)
                    input_box = tk.Entry(frame, width=40)
                    input_box.pack(side=tk.LEFT, padx=5)
                    self.input_box_arr[2] = input_box
                else:
                    suffix_label = tk.Label(frame, text=suffix_text)
                    suffix_label.pack(side=tk.LEFT)
            else:
                input_box = tk.Entry(frame, width=40)
                input_box.pack(side=tk.LEFT, padx=5)
                self.input_box_arr[5] = input_box
                frame = tk.Frame(popup)
                frame.pack(pady=2)
                tk.Label(frame, text=suffix_text).pack(side=tk.LEFT)

        # 设置标签和输入框
        tk.Label(popup, text='设置').pack(pady=5,anchor='w', expand=True)

        settings_frame = tk.Frame(popup)
        settings_frame.pack(pady=5, anchor='w', expand=True)

        labels = ['起始编号', '编号位数', '编号增量', '补齐字符']
        entries = []

        for i, label_text in enumerate(labels):
            row = i // 2
            col = (i % 2) * 2

            tk.Label(settings_frame, text=label_text).grid(row=row, column=col, padx=5, pady=5, sticky='e')
            entry = tk.Entry(settings_frame, width=20)
            entry.grid(row=row, column=col + 1, padx=5, pady=5, sticky='w')
            entries.append(entry)

        self.start_number_entry, self.number_length_entry, self.increment_entry, self.padding_char_entry = entries

        # 确定和取消按钮
        btn_box = tk.Frame(popup)
        btn_box.pack(pady=5)

        apply_button = ttk.Button(btn_box, text='确定', command=on_apply)
        apply_button.pack(side=tk.LEFT, padx=5)
        close_button = ttk.Button(btn_box, text='取消', command=popup.destroy)
        close_button.pack(side=tk.RIGHT, padx=5)

        popup.mainloop()

    def shuffle_files(self):
        random.shuffle(self.files)
        self.update_table()

    def modify_files(self):
        for row in self.files:
            new_file_name = row[2]
            new_path = os.path.join(os.path.dirname(row[0]), new_file_name)
            os.rename(row[0], new_path)
            row[1] = new_file_name
            row[3] = '成功'
        self.update_table()

    def restore_names(self):
        for row in self.files:
            row[2] = row[1]
        self.update_table()
    def download_images(self):
        folder_path = filedialog.askdirectory(title="选择文件夹")

        if folder_path:
            # 列出文件夹中的所有文件
            file_path = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            if file_path:
                # 创建加载中的弹窗并设置进度条
                self.loading_window = tk.Toplevel(self)
                self.loading_window.title("下载中...")
                self.loading_window.geometry("300x100")
                self.loading_window.transient(self)
                self.loading_window.grab_set()

                # 进度条
                self.progress_bar = ttk.Progressbar(self.loading_window, orient='horizontal', length=250, mode='determinate')
                self.progress_bar.pack(pady=20)

                # 获取文件行数作为进度条的总数
                total_lines = sum(1 for line in open(file_path))
                self.progress_bar['maximum'] = total_lines
                self.progress_bar['value'] = 0
                self.error_url = []
                # 启动后台线程执行下载任务
                asyncio.run(self._download_images(file_path))

            
    async def _download_images(self, file_path):
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            save_dir = os.path.join(os.path.expanduser("~"), "Desktop", "download_images")
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            total_lines = len(lines)
            self.progress_bar['maximum'] = total_lines

            tasks = []
            for i, line in enumerate(lines):
                url = line.strip()
                tasks.append(self._download_single_image(session, url, save_dir, i + 1))

            for task in asyncio.as_completed(tasks):
                await task

            if len(self.error_url):
                # 保存到当前save_dir文件夹下的error.txt 若存在则覆盖
                with open(os.path.join(save_dir, 'error.txt'), 'w') as f:
                    for url in self.error_url:
                        f.write(url + '\n')
                # 清空
                self.error_url = []
                
            # 关闭加载中的弹窗
            self.loading_window.destroy()

    async def _download_single_image(self, session, url, save_dir, index):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    file_name = os.path.join(save_dir, os.path.basename(url))
                    with open(file_name, 'wb') as img_file:
                        img_file.write(await response.read())
                else:
                    self.error_url.append(url)

            # 更新进度条
            self.progress_bar.step(1)
            self.loading_window.update()

        except Exception as e:
            print(f"Error downloading {url}: {e}")
    def moon_cloud_system(self):   
        webbrowser.open('http://localhost:8079')

def run_server():
        moonyun.run(host='0.0.0.0', port=8079)

if __name__ == "__main__":
    p = Process(target=run_server)
    p.start()
    app = FileHandle()
    app.mainloop()
