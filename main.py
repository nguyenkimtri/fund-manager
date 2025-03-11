import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import json
import os

DATA_FILE = "fund.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"total": 0, "week": 1, "members": {}}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


class FundManagerApp(toga.App):
    def startup(self):
        self.data = load_data()

        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # Tổng quỹ
        self.total_label = toga.Label(f"Tổng quỹ: {self.data['total']:,} VND", style=Pack(padding=5))
        main_box.add(self.total_label)

        # Chọn tuần
        self.week_selection = toga.Selection(
            items=[f"Tuần {i}" for i in range(1, self.data["week"] + 1)],
            style=Pack(padding=5),
            on_change=self.update_ui
        )
        main_box.add(self.week_selection)

        # Danh sách thành viên
        self.members_list = toga.Box(style=Pack(direction=COLUMN, padding=5))
        main_box.add(self.members_list)

        self.update_ui()

        # Thêm tuần
        self.add_week_button = toga.Button("Thêm tuần", on_press=self.add_week, style=Pack(padding=5))
        main_box.add(self.add_week_button)

        # Nhập tên thành viên
        self.member_input = toga.TextInput(placeholder="Nhập tên thành viên", style=Pack(padding=5))
        main_box.add(self.member_input)

        # Nút thêm/xóa thành viên
        btn_box = toga.Box(style=Pack(direction=ROW, padding=5))
        add_member_btn = toga.Button("Thêm", on_press=self.add_member, style=Pack(padding=5))
        remove_member_btn = toga.Button("Xóa", on_press=self.remove_member, style=Pack(padding=5))
        reset_btn = toga.Button("Reset", on_press=self.reset_all, style=Pack(padding=5))
        btn_box.add(add_member_btn)
        btn_box.add(remove_member_btn)
        btn_box.add(reset_btn)
        main_box.add(btn_box)

        # Nút tổng kết
        self.summary_button = toga.Button("Tổng kết", on_press=self.toggle_summary, style=Pack(padding=5))
        main_box.add(self.summary_button)

        self.summary_label = toga.Label("", style=Pack(padding=5))
        main_box.add(self.summary_label)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def update_ui(self, widget=None):
        self.members_list.clear()
        selected_week = int(self.week_selection.value.split()[1]) if self.week_selection.value else 1

        for member in self.data.get("members", {}):
            status = "✔ Đã đóng" if self.data["members"][member].get(selected_week, False) else "✘ Chưa đóng"
            btn = toga.Button(f"{member} - {status}",
                              on_press=lambda w, name=member: self.toggle_payment(name, selected_week),
                              style=Pack(padding=5))
            self.members_list.add(btn)

    def toggle_payment(self, name, week):
        self.data["members"][name][week] = not self.data["members"][name].get(week, False)
        self.data["total"] += 30000 if self.data["members"][name][week] else -30000
        save_data(self.data)
        self.total_label.text = f"Tổng quỹ: {self.data['total']:,} VND"
        self.update_ui()

    def add_member(self, widget):
        name = self.member_input.value.strip()
        if name and name not in self.data["members"]:
            self.data["members"][name] = {week: False for week in range(1, self.data["week"] + 1)}
            save_data(self.data)
            self.update_ui()
        self.member_input.value = ""

    def remove_member(self, widget):
        name = self.member_input.value.strip()
        if name in self.data["members"]:
            del self.data["members"][name]
            save_data(self.data)
            self.update_ui()
        self.member_input.value = ""

    def add_week(self, widget):
        self.data["week"] += 1
        for member in self.data["members"]:
            self.data["members"][member][self.data["week"]] = False
        save_data(self.data)
        self.week_selection.items = [f"Tuần {i}" for i in range(1, self.data["week"] + 1)]
        self.week_selection.value = f"Tuần {self.data['week']}"
        self.update_ui()

    def reset_all(self, widget):
        self.data = {"total": 0, "week": 1, "members": {}}
        save_data(self.data)

        # Cập nhật lại giao diện
        self.week_selection.items = ["Tuần 1"]
        self.week_selection.value = "Tuần 1"
        self.total_label.text = "Tổng quỹ: 0 VND"
        self.summary_label.text = ""

        # Xóa hết các thành viên hiển thị
        self.members_list.children.clear()

        self.update_ui()  # Đảm bảo giao diện được cập nhật lại

    def toggle_summary(self, widget):
        summary_text = ""
        for member in self.data["members"]:
            unpaid_weeks = [str(week) for week in self.data["members"][member] if
                            not self.data["members"][member][week]]
            if unpaid_weeks:
                summary_text += f"{member}: {', '.join(unpaid_weeks)}\n"
        self.summary_label.text = summary_text if summary_text else "Tất cả thành viên đã đóng đầy đủ"


if __name__ == "__main__":
    FundManagerApp("Quỹ Nhóm", "com.kimtri.fundmanager").main_loop()
