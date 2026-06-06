import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import subprocess
import os
import re
import threading

class PrimixIDE:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Primix IDE v0.2")
        self.window.geometry("1000x700")
        self.window.configure(bg='#1a1a2e')
        self.current_file = None
        self.build_ui()

    def build_ui(self):
        # Меню
        menubar = tk.Menu(self.window)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label="Run Server", command=self.run_file, accelerator="F5")
        run_menu.add_command(label="Run Ghost Mode", command=self.run_ghost)
        menubar.add_cascade(label="Run", menu=run_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Primix Docs", command=self.show_help)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.window.config(menu=menubar)

        # Toolbar
        toolbar = tk.Frame(self.window, bg='#16213e', height=40)
        toolbar.pack(fill=tk.X)

        for text, cmd, color in [
            ("New", self.new_file, '#0f3460'),
            ("Open", self.open_file, '#0f3460'),
            ("Save", self.save_file, '#0f3460')
        ]:
            btn = tk.Button(toolbar, text=text, bg=color, fg='white',
                            command=cmd, relief=tk.FLAT, padx=12, font=('Arial', 9))
            btn.pack(side=tk.LEFT, padx=3, pady=5)

        self.file_label = tk.Label(toolbar, text="Untitled.pmx", bg='#16213e', fg='#aaaaaa')
        self.file_label.pack(side=tk.LEFT, padx=15)

        btn_run = tk.Button(toolbar, text="▶ Run", bg='#e94560', fg='white',
                            command=self.run_file, relief=tk.FLAT, padx=18,
                            font=('Arial', 10, 'bold'))
        btn_run.pack(side=tk.RIGHT, padx=10, pady=5)

        btn_ghost = tk.Button(toolbar, text="👻 Ghost", bg='#533483', fg='white',
                              command=self.run_ghost, relief=tk.FLAT, padx=12)
        btn_ghost.pack(side=tk.RIGHT, padx=5, pady=5)

        # Editor
        editor_frame = tk.Frame(self.window, bg='#1a1a2e')
        editor_frame.pack(fill=tk.BOTH, expand=True)

        self.editor = tk.Text(editor_frame, bg='#1a1a2e', fg='#e0e0e0',
                              insertbackground='#e94560', font=('Consolas', 13),
                              relief=tk.FLAT, undo=True, wrap=tk.NONE,
                              padx=10, pady=10)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(editor_frame, command=self.editor.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=scrollbar.set)

        self.editor.bind('<KeyRelease>', self.highlight)
        self.editor.bind('<Control-n>', lambda e: self.new_file())
        self.editor.bind('<Control-o>', lambda e: self.open_file())
        self.editor.bind('<Control-s>', lambda e: self.save_file())
        self.editor.bind('<F5>', lambda e: self.run_file())

        # Output
        output_label = tk.Label(self.window, text="Output:", bg='#1a1a2e', fg='#aaaaaa',
                                anchor='w', font=('Arial', 9, 'bold'))
        output_label.pack(fill=tk.X, padx=12, pady=(5, 0))

        self.output = scrolledtext.ScrolledText(self.window, height=10,
                                                bg='#0d0d0d', fg='#00ff88',
                                                font=('Consolas', 10))
        self.output.pack(fill=tk.BOTH, padx=12, pady=(0, 10))

    def highlight(self, event=None):
        code = self.editor.get('1.0', tk.END)
        for tag in ['keyword', 'string', 'number', 'comment', 'command', 'route']:
            self.editor.tag_remove(tag, '1.0', tk.END)

        keywords = [
            'start', 'run/server', 'with', 'key', 'go', 'request', 'fields',
            'then', 'respond', 'connect', 'call/', 'send', 'to/', 'store',
            'on/', 'get', 'print', 'true', 'false', 'if', 'else', 'repeat',
            'times', 'every', 'do', 'delete', 'list', 'vars', 'save', 'state',
            'load', 'clear', 'cache', 'ping', 'bind', 'unbind', 'env',
            'timeout', 'version', 'help', 'throw', 'file', 'read', 'write',
            'lock', 'down', 'key', 'rotate', 'expires', 'intruder', 'alert',
            'blackhole', 'burn', 'server', 'reload', 'block', 'whitelist',
            'physical', 'only', 'ghost', 'balance', 'queue', 'db', 'query',
            'json', 'msgpack', 'status', 'log', 'debug', 'mixed', 'jp', 'en', 'rnd'
        ]

        for kw in set(keywords):
            for match in re.finditer(re.escape(kw), code):
                s, e = f'1.0+{match.start()}c', f'1.0+{match.end()}c'
                self.editor.tag_add('keyword', s, e)

        commands = ['/add', 'sos', 'mod!', 'view', 'in', 'its', 'entirety']
        for cmd in set(commands):
            for match in re.finditer(re.escape(cmd), code):
                s, e = f'1.0+{match.start()}c', f'1.0+{match.end()}c'
                self.editor.tag_add('command', s, e)

        for match in re.finditer(r'"[^"]*"', code):
            s, e = f'1.0+{match.start()}c', f'1.0+{match.end()}c'
            self.editor.tag_add('string', s, e)

        for match in re.finditer(r'\b\d+\b', code):
            s, e = f'1.0+{match.start()}c', f'1.0+{match.end()}c'
            self.editor.tag_add('number', s, e)

        for match in re.finditer(r'#.*$', code, re.MULTILINE):
            s, e = f'1.0+{match.start()}c', f'1.0+{match.end()}c'
            self.editor.tag_add('comment', s, e)

        for match in re.finditer(r'go (request|fields) /\S+', code):
            s, e = f'1.0+{match.start()}c', f'1.0+{match.end()}c'
            self.editor.tag_add('route', s, e)

        self.editor.tag_config('keyword', foreground='#569cd6', font=('Consolas', 13, 'bold'))
        self.editor.tag_config('command', foreground='#e94560', font=('Consolas', 13, 'bold'))
        self.editor.tag_config('string', foreground='#ce9178')
        self.editor.tag_config('number', foreground='#b5cea8')
        self.editor.tag_config('comment', foreground='#6a9955', font=('Consolas', 13, 'italic'))
        self.editor.tag_config('route', foreground='#4ec9b0')

    def new_file(self):
        self.editor.delete('1.0', tk.END)
        self.current_file = None
        self.file_label.config(text="Untitled.pmx")

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Primix files", "*.pmx"), ("All files", "*.*")])
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', f.read())
            self.current_file = path
            self.file_label.config(text=os.path.basename(path))
            self.highlight()

    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.get('1.0', 'end-1c'))
        else:
            path = filedialog.asksaveasfilename(defaultextension=".pmx",
                                                filetypes=[("Primix files", "*.pmx")])
            if path:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.editor.get('1.0', 'end-1c'))
                self.current_file = path
                self.file_label.config(text=os.path.basename(path))

    def run_file(self):
        self._execute(ghost=False)

    def run_ghost(self):
        self._execute(ghost=True)

    def _execute(self, ghost=False):
        self.output.delete('1.0', tk.END)
        if not self.current_file:
            self.save_file()
        if not self.current_file:
            return

        self.output.insert(tk.END, f"Starting Primix server...\n")
        self.output.insert(tk.END, f"File: {self.current_file}\n")
        if ghost:
            self.output.insert(tk.END, f"Mode: GHOST\n")
        self.output.insert(tk.END, f"{'-'*50}\n")
        self.output.see(tk.END)

        def run():
            try:
                args = ['python', 'primix.py', self.current_file]
                if ghost:
                    args.append('ghost')
                proc = subprocess.Popen(args,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                for line in iter(proc.stdout.readline, ''):
                    self.output.insert(tk.END, line)
                    self.output.see(tk.END)
                proc.stdout.close()
                proc.wait()
            except Exception as e:
                self.output.insert(tk.END, f"Error: {e}\n")

        threading.Thread(target=run, daemon=True).start()

    def show_help(self):
        help_text = """Primix v0.2 — Документация

Команды:
  start run/server       — Запуск сервера
  go request /path then  — GET маршрут
  go fields /path then   — POST маршрут
  respond "text"         — Ответ текстом
  respond json {...}     — JSON ответ
  respond msgpack {...}  — MessagePack ответ
  store on/ key          — Сохранить данные
  get to/ key            — Получить данные
  throw to/key data      — Отправить данные другому серверу
  print var              — Вывод в консоль
  if cond then ... else  — Условие
  repeat N times         — Цикл
  every X min do         — Периодическая задача
  status                 — Статус сервера
  log on/off             — Логирование
  debug on               — Отладка
  env key = val          — Переменная окружения
  ping key               — Проверка сервера
  timeout sec            — Таймаут запроса
  list servers           — Список серверов
  key rotate             — Смена ключа
  save state             — Сохранить состояние
  load state             — Загрузить состояние
  cache on               — Включить кеш
  clear cache            — Очистить кеш
  balance on             — Балансировка
  queue on               — Очередь задач
  db query "..."         — SQL запрос
  file read/write        — Работа с файлами
  /add t8t MODE          — Режим шифрования
  /add sos mod! key      — SOS резерв
  /view in its entirety  — Отчёты на комп
  burn server            — Самоуничтожение
  reload server          — Перезагрузка кода
  block key              — Заблокировать ключ
  whitelist key          — Белый список
  lock down              — Полная блокировка
  key expires            — Срок действия ключа
  intruder alert         — Оповещение о вторжении
  blackhole              — Режим тишины
  physical only          — Только физический доступ
"""
        messagebox.showinfo("Primix Documentation", help_text)

    def start(self):
        self.window.mainloop()


if __name__ == '__main__':
    ide = PrimixIDE()
    ide.start()