import pandas as pd
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Tk, Toplevel, filedialog, messagebox
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base

# 数据库配置
DATABASE_URL = "sqlite:///orders.db"

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)

# 创建会话
Session = sessionmaker(bind=engine)
session = Session()

# 基础类
Base = declarative_base()

# 定义订单模型
class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(String, primary_key=True)
    task_type = Column(String)
    execution_time = Column(String)
    target_link = Column(String)
    task_quantity = Column(Integer)
    execution_progress = Column(String)
    task_status = Column(String)
    order_action = Column(String)



class OrderDetail(Base):
    __tablename__ = 'order_details'
    id = Column(Integer, primary_key=True)
    order_id = Column(String, ForeignKey('orders.order_id'))
    account = Column(String)
    ip_address = Column(String)
    target_link = Column(String)
    run_status = Column(String)

    # 关联主表
    order = relationship("Order", back_populates="details")

# 更新主表模型
Order.details = relationship("OrderDetail", order_by=OrderDetail.id, back_populates="order")

# 创建表格
Base.metadata.create_all(engine)

# 子表窗口类
class ChildTableWindow:
    def __init__(self, master, order_id):
        self.master = master
        self.order_id = order_id
        self.create_window()
        self.load_data()
        self.update_view()

    def create_window(self):
        self.window = Toplevel(self.master)
        self.window.title(self.order_id)
        self.window.geometry("800x400")

        # 创建 Treeview 子表格
        columns = ("账号", "IP地址", "目标链接", "运行状态")
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings', bootstyle="primary")

        # 设置表头和列宽
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=CENTER, width=120, stretch=NO)

        # 创建水平滚动条
        self.h_scrollbar = ttk.Scrollbar(self.window, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.h_scrollbar.set)

        # 创建新增子表行按钮
        self.add_button = ttk.Button(self.window, text="新增子表项", command=self.open_add_window)

        # 创建分页器按钮
        self.prev_button = ttk.Button(self.window, text="上一页", command=self.prev_page)
        self.next_button = ttk.Button(self.window, text="下一页", command=self.next_page)

        # 创建分页信息显示标签
        self.page_info = ttk.Label(self.window, text="")

        # 创建自定义行数输入框和跳转页数输入框
        ttk.Label(self.window, text="每页行数:").grid(row=2, column=4, padx=5)
        self.rows_per_page_entry = ttk.Entry(self.window, width=5)
        self.rows_per_page_entry.grid(row=2, column=5, padx=5)
        self.rows_per_page_entry.insert(0, "10")  # 默认值

        ttk.Label(self.window, text="跳转到页:").grid(row=2, column=6, padx=5)
        self.page_jump_entry = ttk.Entry(self.window, width=5)
        self.page_jump_entry.grid(row=2, column=7, padx=5)

        # 创建跳转按钮
        self.jump_button = ttk.Button(self.window, text="跳转", command=self.jump_to_page)

        # 创建导入 Excel 按钮
        self.import_button = ttk.Button(self.window, text="导入 Excel", command=self.import_excel)
        self.import_button.grid(row=2, column=9, padx=10, pady=10, sticky="w")

        # 使用 grid 布局管理器
        self.tree.grid(row=0, column=0, columnspan=10, sticky="nsew")
        self.h_scrollbar.grid(row=1, column=0, columnspan=10, sticky="ew")
        self.add_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.prev_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.next_button.grid(row=2, column=2, padx=10, pady=10, sticky="w")
        self.page_info.grid(row=2, column=3, padx=10, pady=10, sticky="e")
        self.jump_button.grid(row=2, column=8, padx=5)

        # 设置列和行的权重
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # 初始化分页参数
        self.current_page = 1

        # 设置双击事件处理
        self.tree.bind('<Double-1>', self.on_item_double_click)

    def load_data(self):
        # 在数据库中通过外键查询
        self.data = session.query(OrderDetail).filter(OrderDetail.order_id == self.order_id).all()
        self.update_view()

    def open_add_window(self):
        # 创建一个新的弹出窗口用于录入子表新数据
        self.add_window = Toplevel(self.window)
        self.add_window.title("新增")
        self.add_window.geometry("400x300")

        # 创建表单字段
        labels = ["账号", "IP地址", "目标链接", "运行状态"]
        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(self.add_window, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = ttk.Entry(self.add_window)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[label] = entry

        # 创建保存按钮
        ttk.Button(self.add_window, text="保存", command=self.save_new_item).grid(row=len(labels), column=0, columnspan=2, pady=20)

    def save_new_item(self):
        # 获取表单数据并保存到数据库
        new_detail = OrderDetail(
            order_id=self.order_id,
            account=self.entries["账号"].get(),
            ip_address=self.entries["IP地址"].get(),
            target_link=self.entries["目标链接"].get(),
            run_status=self.entries["运行状态"].get()
        )
        session.add(new_detail)
        session.commit()

        # 关闭新增窗口并刷新数据
        self.add_window.destroy()
        self.load_data()

    def update_view(self):
        # 更新子表格数据
        for row in self.tree.get_children():
            self.tree.delete(row)

        # 计算分页范围
        rows_per_page = int(self.rows_per_page_entry.get())
        start_index = (self.current_page - 1) * rows_per_page
        end_index = start_index + rows_per_page

        # 添加数据到子表格
        for item in self.data[start_index:end_index]:
            self.tree.insert('', 'end', iid=item.id, values=(
                item.account,
                item.ip_address,
                item.target_link,
                item.run_status
            ))

        # 更新分页信息
        self.update_page_info()

    def update_page_info(self):
        rows_per_page = int(self.rows_per_page_entry.get())
        total_rows = len(self.data)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page
        self.page_info.config(text=f"第 {self.current_page} 页 / 共 {total_pages} 页")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_view()

    def next_page(self):
        rows_per_page = int(self.rows_per_page_entry.get())
        total_rows = len(self.data)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page

        if self.current_page < total_pages:
            self.current_page += 1
            self.update_view()

    def jump_to_page(self):
        try:
            page_number = int(self.page_jump_entry.get())
            if 1 <= page_number <= (len(self.data) + int(self.rows_per_page_entry.get()) - 1) // int(self.rows_per_page_entry.get()):
                self.current_page = page_number
                self.update_view()
        except ValueError:
            pass

    def on_item_double_click(self, event):
        item_id = self.tree.selection()[0]  # 获取选中的项
        item_values = self.tree.item(item_id, 'values')  # 获取当前行的值

        # 创建一个新的弹出窗口用于编辑数据
        self.edit_window = Toplevel(self.window)
        self.edit_window.title("编辑")
        self.edit_window.geometry("400x300")

        # 创建表单字段
        labels = ["账号", "IP地址", "目标链接", "运行状态"]
        self.edit_entries = {}

        for i, label in enumerate(labels):
            ttk.Label(self.edit_window, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = ttk.Entry(self.edit_window)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, item_values[i])  # 显示当前值
            self.edit_entries[label] = entry

        # 创建保存按钮
        ttk.Button(self.edit_window, text="保存", command=lambda: self.save_edit(item_id)).grid(row=len(labels), column=0, columnspan=2, pady=20)
        # ttk.Button(self.edit_window, text="取消", command=self.edit_window.destroy).grid(row=len(labels)+1, column=0, columnspan=2, pady=5)

    def save_edit(self, item_id):
        # 获取编辑框中的内容
        account = self.edit_entries["账号"].get()
        ip_address = self.edit_entries["IP地址"].get()
        target_link = self.edit_entries["目标链接"].get()
        run_status = self.edit_entries["运行状态"].get()

        # 更新数据库中的数据
        detail = session.query(OrderDetail).filter(OrderDetail.id == item_id).first()
        detail.account = account
        detail.ip_address = ip_address
        detail.target_link = target_link
        detail.run_status = run_status

        session.commit()  # 提交更改
        self.edit_window.destroy()  # 关闭编辑窗口
        self.load_data()  # 重新加载数据

    def import_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if not file_path:
            return

        try:
            # 读取 Excel 文件
            df = pd.read_excel(file_path)

            # 将数据插入数据库
            for _, row in df.iterrows():
                detail = OrderDetail(
                    order_id=self.order_id,
                    account=row.get('账号', ''),
                    ip_address=row.get('IP地址', ''),
                    target_link=row.get('目标链接', ''),
                    run_status=row.get('运行状态', '')
                )
                session.add(detail)

            session.commit()
            self.load_data()
            messagebox.showinfo("导入成功", "Excel 数据导入成功！")
        except Exception as e:
            session.rollback()
            messagebox.showerror("导入失败", f"导入 Excel 数据时出错: {e}")
