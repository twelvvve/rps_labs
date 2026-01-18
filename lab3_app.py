import random
import tkinter as tk
from tkinter import messagebox, ttk

from db_layer import SqliteStorage, User
from sort_alg import quick_sort


class ArraySorterGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Сервис сортировки массивов")
        self.root.geometry("820x640")

        self.storage = SqliteStorage("sorting_app.db")

        self.user: User | None = None
        self.src: list[int] = []
        self.dst: list[int] | None = None

        self.status = tk.StringVar(value="Готово")
        self.input_mode = tk.StringVar(value="manual")  # manual | random

        self._build_login()

    # -------------------- UI builders --------------------

    def _reset_window(self) -> None:
        for w in self.root.winfo_children():
            w.destroy()

    def _build_login(self) -> None:
        self._reset_window()

        frame = ttk.Frame(self.root, padding=24)
        frame.pack(expand=True)

        ttk.Label(frame, text="Вход в систему", font=("Arial", 18, "bold")).pack(pady=(0, 14))

        form = ttk.Frame(frame)
        form.pack(fill="x")

        ttk.Label(form, text="Логин").grid(row=0, column=0, sticky="w", pady=6)
        self.login_entry = ttk.Entry(form, width=34)
        self.login_entry.grid(row=0, column=1, pady=6)

        ttk.Label(form, text="Пароль").grid(row=1, column=0, sticky="w", pady=6)
        self.pass_entry = ttk.Entry(form, width=34, show="*")
        self.pass_entry.grid(row=1, column=1, pady=6)

        btns = ttk.Frame(frame)
        btns.pack(pady=18)

        ttk.Button(btns, text="Войти", command=self._do_login).pack(side="left", padx=6)
        ttk.Button(btns, text="Создать аккаунт", command=self._do_register).pack(side="left", padx=6)

        note = ttk.Label(
            frame,
            text="Подсказка: логин - минимум 3 символа, пароль - минимум 4 символа.",
            foreground="#444",
        )
        note.pack(pady=(8, 0))

    def _build_main(self) -> None:
        self._reset_window()

        # Верхняя панель
        top = ttk.Frame(self.root, padding=(12, 10))
        top.pack(fill="x")

        ttk.Label(top, text=f"Пользователь: {self.user.username}", font=("Arial", 12)).pack(side="left")

        ttk.Button(top, text="Справка", command=self._show_help).pack(side="right", padx=(6, 0))
        ttk.Button(top, text="История", command=self._open_history).pack(side="right", padx=(6, 0))
        ttk.Button(top, text="Выйти", command=self._logout).pack(side="right")

        # Блок ввода
        box_in = ttk.LabelFrame(self.root, text="Данные", padding=12)
        box_in.pack(fill="x", padx=12, pady=(0, 10))

        mode_row = ttk.Frame(box_in)
        mode_row.pack(fill="x")

        ttk.Label(mode_row, text="Способ ввода:").pack(side="left")
        ttk.Radiobutton(
            mode_row,
            text="с клавиатуры",
            variable=self.input_mode,
            value="manual",
            command=self._sync_mode,
        ).pack(side="left", padx=10)
        ttk.Radiobutton(
            mode_row,
            text="случайная генерация",
            variable=self.input_mode,
            value="random",
            command=self._sync_mode,
        ).pack(side="left")

        self.array_entry = ttk.Entry(box_in)
        self.array_entry.pack(fill="x", pady=(10, 6))
        self.array_entry.insert(0, "Например: 5, -2, 13, 0")

        actions = ttk.Frame(box_in)
        actions.pack(fill="x", pady=(4, 0))

        ttk.Button(actions, text="Сгенерировать", command=self._generate).pack(side="left")
        ttk.Button(actions, text="Проверить и разобрать", command=self._parse_from_entry).pack(
            side="left", padx=6
        )
        ttk.Button(actions, text="Отсортировать", command=self._sort).pack(side="left", padx=6)
        ttk.Button(actions, text="Очистить", command=self._clear_arrays).pack(side="right")

        # Блок вывода
        box_out = ttk.LabelFrame(self.root, text="Результаты", padding=12)
        box_out.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        ttk.Label(box_out, text="Исходный массив").pack(anchor="w")
        self.src_text = tk.Text(box_out, height=4)
        self.src_text.pack(fill="x", pady=(4, 10))

        ttk.Label(box_out, text="Отсортированный массив (QuickSort)").pack(anchor="w")
        self.dst_text = tk.Text(box_out, height=4)
        self.dst_text.pack(fill="x", pady=(4, 10))

        save_row = ttk.Frame(box_out)
        save_row.pack(fill="x")

        ttk.Button(save_row, text="Сохранить", command=self._save).pack(side="left")
        ttk.Label(save_row, text="(сохраняется исходный и, если есть, отсортированный)", foreground="#444").pack(
            side="left", padx=10
        )

        # Статус бар
        status = ttk.Label(self.root, textvariable=self.status, relief="sunken", anchor="w")
        status.pack(fill="x", padx=12, pady=(0, 10))

        self._sync_mode()
        self._render_arrays()

    # -------------------- Auth --------------------

    def _do_register(self) -> None:
        u = self.login_entry.get().strip()
        p = self.pass_entry.get().strip()
        if not u or not p:
            messagebox.showwarning("Проверка", "Заполните логин и пароль")
            return
        ok, msg = self.storage.register_user(u, p)
        if ok:
            messagebox.showinfo("Готово", msg)
        else:
            messagebox.showerror("Ошибка", msg)

    def _do_login(self) -> None:
        u = self.login_entry.get().strip()
        p = self.pass_entry.get().strip()
        if not u or not p:
            messagebox.showwarning("Проверка", "Заполните логин и пароль")
            return

        ok, res = self.storage.authenticate_user(u, p)
        if ok:
            self.user = res
            self.status.set(f"Вход выполнен: {self.user.username}")
            self._build_main()
        else:
            messagebox.showerror("Ошибка", str(res))

    def _logout(self) -> None:
        self.user = None
        self.src = []
        self.dst = None
        self.status.set("Вы вышли из аккаунта")
        self._build_login()

    # -------------------- Array logic --------------------

    def _sync_mode(self) -> None:
        mode = self.input_mode.get()
        if mode == "manual":
            self.array_entry.state(["!disabled"])
        else:
            self.array_entry.state(["disabled"])

    def _generate(self) -> None:
        if self.input_mode.get() != "random":
            messagebox.showinfo("Подсказка", "Переключите способ ввода на 'случайная генерация'.")
            return

        n = random.randint(8, 20)
        self.src = [random.randint(-100, 100) for _ in range(n)]
        self.dst = None
        self.status.set(f"Сгенерирован массив из {n} элементов")
        self._render_arrays()

    def _parse_from_entry(self) -> bool:
        if self.input_mode.get() != "manual":
            messagebox.showinfo("Подсказка", "Переключите способ ввода на 'с клавиатуры'.")
            return False

        raw = self.array_entry.get().strip()
        if not raw:
            messagebox.showwarning("Проверка", "Введите числа через запятую")
            return False

        try:
            parts = [p.strip() for p in raw.split(",") if p.strip()]
            self.src = [int(x) for x in parts]
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат. Пример: 1, -2, 3")
            return False

        if not self.src:
            messagebox.showwarning("Проверка", "Массив пустой")
            return False

        self.dst = None
        self.status.set("Массив принят")
        self._render_arrays()
        return True

    def _sort(self) -> None:
        if not self.src:
            # если режим ручной, пробуем распарсить
            if self.input_mode.get() == "manual":
                if not self._parse_from_entry():
                    return
            else:
                messagebox.showwarning("Проверка", "Сначала сгенерируйте массив")
                return

        self.dst = quick_sort(self.src)
        self.status.set("Сортировка завершена")
        self._render_arrays()

    def _clear_arrays(self) -> None:
        self.src = []
        self.dst = None
        self.status.set("Данные очищены")
        self._render_arrays()

    def _render_arrays(self) -> None:
        self.src_text.delete("1.0", tk.END)
        self.dst_text.delete("1.0", tk.END)

        if self.src:
            self.src_text.insert(tk.END, str(self.src))
        if self.dst is not None:
            self.dst_text.insert(tk.END, str(self.dst))

    # -------------------- DB actions --------------------

    def _save(self) -> None:
        if not self.user:
            messagebox.showwarning("Доступ", "Сначала выполните вход")
            return
        if not self.src:
            messagebox.showwarning("Проверка", "Нет массива для сохранения")
            return

        ok, msg = self.storage.save_arrays(self.user.id, self.src, self.dst)
        if ok:
            self.status.set("Сохранено")
            messagebox.showinfo("Готово", msg)
        else:
            messagebox.showerror("Ошибка", msg)

    def _open_history(self) -> None:
        if not self.user:
            return

        ok, res = self.storage.list_user_arrays(self.user.id)
        if not ok:
            messagebox.showerror("Ошибка", str(res))
            return

        win = tk.Toplevel(self.root)
        win.title("История сохранений")
        win.geometry("900x420")

        tree = ttk.Treeview(win, columns=("id", "len", "created", "orig", "sorted"), show="headings")
        tree.heading("id", text="ID")
        tree.heading("len", text="Размер")
        tree.heading("created", text="Дата")
        tree.heading("orig", text="Исходный")
        tree.heading("sorted", text="Отсортированный")

        tree.column("id", width=60, anchor="center")
        tree.column("len", width=70, anchor="center")
        tree.column("created", width=150)
        tree.column("orig", width=280)
        tree.column("sorted", width=280)

        for item in res:
            tree.insert(
                "",
                "end",
                values=(
                    item["id"],
                    item["length"],
                    item["created_at"],
                    str(item["original"]),
                    str(item["sorted"]) if item["sorted"] is not None else "-",
                ),
            )

        tree.pack(fill="both", expand=True, padx=10, pady=10)

    # -------------------- Help --------------------

    def _show_help(self) -> None:
        txt = (
            "Как работать с программой:\n\n"
            "1) Создайте аккаунт или войдите.\n"
            "2) Выберите способ ввода массива: ручной или генерация.\n"
            "3) Для ручного ввода: числа через запятую (например: 3, -1, 0).\n"
            "4) Нажмите 'Отсортировать' - используется QuickSort (лаб. 2).\n"
            "5) Кнопка 'Сохранить' записывает массивы в БД, а 'История' показывает сохранения.\n\n"
            "Если ввод некорректен - программа подсветит проблему через сообщение об ошибке."
        )
        messagebox.showinfo("Справка", txt)


def main() -> None:
    root = tk.Tk()
    ArraySorterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
