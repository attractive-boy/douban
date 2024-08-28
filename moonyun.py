import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Tk, Toplevel, simpledialog, messagebox
import pandas as pd
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from tkinter import Scrollbar, VERTICAL, HORIZONTAL, YES, BOTH
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from moondetail import ChildTableWindow

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

class OrderTableWindow:
    def __init__(self, master=None):
        self.master = master
        self.create_window()
        self.load_data()
        self.update_view()

    def create_window(self):
        self.window = ttk.Toplevel(self.master)
        self.window.title("月球云系统v1.0")
        self.window.geometry("1000x600")

        # 创建 Treeview 表格
        columns = ("订单编号", "任务类型", "执行时间", "目标链接", "任务数量", "执行进度", "任务状态", "订单操作")
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings', bootstyle="primary")

        # 设置表头和列宽
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=CENTER, width=120, stretch=NO)

        # 创建垂直滚动条
        # self.v_scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.tree.yview)
        # self.tree.configure(yscrollcommand=self.v_scrollbar.set)

        # 创建水平滚动条
        self.h_scrollbar = ttk.Scrollbar(self.window, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.h_scrollbar.set)

        # 创建新增行按钮
        self.add_button = ttk.Button(self.window, text="新增订单", command=self.open_add_window)

        # 创建分页器按钮
        self.prev_button = ttk.Button(self.window, text="上一页", command=self.prev_page)
        self.next_button = ttk.Button(self.window, text="下一页", command=self.next_page)

        # 创建分页信息显示标签
        self.page_info = ttk.Label(self.window, text="")

        # 创建自定义行数输入框
        ttk.Label(self.window, text="每页行数:").grid(row=2, column=4, padx=5)
        self.rows_per_page_entry = ttk.Entry(self.window, width=5)
        self.rows_per_page_entry.grid(row=2, column=5, padx=5)
        self.rows_per_page_entry.insert(0, "10")  # 默认值

        # 创建跳转页数输入框
        ttk.Label(self.window, text="跳转到页:").grid(row=2, column=6, padx=5)
        self.page_jump_entry = ttk.Entry(self.window, width=5)
        self.page_jump_entry.grid(row=2, column=7, padx=5)

        # 创建跳转按钮
        self.jump_button = ttk.Button(self.window, text="跳转", command=self.jump_to_page)

        # 使用 grid 布局管理器
        self.tree.grid(row=0, column=0, columnspan=8, sticky="nsew")
        # self.v_scrollbar.grid(row=0, column=8, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, columnspan=8, sticky="ew")
        self.add_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.prev_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.next_button.grid(row=2, column=2, padx=10, pady=10, sticky="w")
        self.page_info.grid(row=2, column=3, padx=10, pady=10, sticky="e")
        self.jump_button.grid(row=2, column=8, padx=5)

        # 设置列和行的权重，以使表格和按钮能够扩展
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # 初始化分页参数
        self.current_page = 1

        # 绑定双击事件
        self.tree.bind("<Double-1>", self.open_edit_window)
        self.tree.bind("<Button-1>", self.on_tree_click)

        # 隐藏滚动条但保持功能
        # self.v_scrollbar.place(relwidth=0.01)  # 调整为非常小的宽度，使其不可见

    def load_data(self):
        # 从数据库加载数据
        self.data = session.query(Order).all()
        self.update_view()

    def open_add_window(self):
        # 创建一个新的弹出窗口用于录入新订单信息
        self.add_window = Toplevel(self.master)
        self.add_window.title("新增订单")
        self.add_window.geometry("400x400")

        # 创建表单字段
        labels = ["订单编号", "任务类型", "执行时间", "目标链接", "任务数量", "执行进度", "任务状态"]
        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(self.add_window, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = ttk.Entry(self.add_window)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[label] = entry

        # 创建保存按钮
        ttk.Button(self.add_window, text="保存", command=self.save_new_order).grid(row=len(labels), column=0, columnspan=2, pady=20)

    def save_new_order(self):
        # 获取表单数据并保存到数据库
        new_order = Order(
            order_id=self.entries["订单编号"].get(),
            task_type=self.entries["任务类型"].get(),
            execution_time=self.entries["执行时间"].get(),
            target_link=self.entries["目标链接"].get(),
            task_quantity=int(self.entries["任务数量"].get()),
            execution_progress=self.entries["执行进度"].get(),
            task_status=self.entries["任务状态"].get(),
            order_action="查看详情" 
        )
        session.add(new_order)
        session.commit()

        # 关闭新增窗口，刷新数据
        self.add_window.destroy()
        self.load_data()
        self.update_view()

    def open_edit_window(self, event):
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item, "values")

        # 创建一个编辑窗口
        self.edit_window = Toplevel(self.master)
        self.edit_window.title("编辑订单")
        self.edit_window.geometry("400x400")

        # 创建表单字段
        labels = ["订单编号", "任务类型", "执行时间", "目标链接", "任务数量", "执行进度", "任务状态"]
        self.entries = {}

        for i, (label, value) in enumerate(zip(labels, values)):
            ttk.Label(self.edit_window, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = ttk.Entry(self.edit_window)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, value)
            self.entries[label] = entry

        # 创建保存按钮
        ttk.Button(self.edit_window, text="保存", command=lambda: self.save_edit_order(selected_item)).grid(row=len(labels), column=0, columnspan=2, pady=20)

    def save_edit_order(self, item_id):
        # 更新选中订单的数据
        order = session.query(Order).filter(Order.order_id == self.entries["订单编号"].get()).first()
        order.task_type = self.entries["任务类型"].get()
        order.execution_time = self.entries["执行时间"].get()
        order.target_link = self.entries["目标链接"].get()
        order.task_quantity = int(self.entries["任务数量"].get())
        order.execution_progress = self.entries["执行进度"].get()
        order.task_status = self.entries["任务状态"].get()
        session.commit()

        # 关闭编辑窗口，刷新数据
        self.edit_window.destroy()
        self.load_data()
        self.update_view()

    def update_view(self):
        # 更新表格数据
        for row in self.tree.get_children():
            self.tree.delete(row)

        # 计算分页范围
        rows_per_page = int(self.rows_per_page_entry.get())
        start_index = (self.current_page - 1) * rows_per_page
        end_index = start_index + rows_per_page

        # 添加数据到表格
        for item in self.data[start_index:end_index]:
            self.tree.insert('', 'end', values=(
                item.order_id,
                item.task_type,
                item.execution_time,
                item.target_link,
                item.task_quantity,
                item.execution_progress,
                item.task_status,
                item.order_action
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

    def on_tree_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            if self.tree.identify_column(event.x) == "#8":  # 操作列
                selected_order_id = self.tree.item(item, "values")[0]
                ChildTableWindow(self.master,selected_order_id)

    