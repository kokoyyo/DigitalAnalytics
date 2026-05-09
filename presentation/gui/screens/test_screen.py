"""Экран тестирования"""

import tkinter as tk
from tkinter import ttk, messagebox
from presentation.gui.styles import Colors, Fonts


class TestScreen(tk.Frame):
    """Экран тестирования с множественным выбором"""
    
    def __init__(self, parent, deck_id):
        super().__init__(parent, bg=Colors.BG_LIGHT)
        self.deck_id = deck_id
        
        self.current_question = 0
        self.total_questions = 5
        self.correct_answers = 0
        self.selected_answer = None
        
        # Временные вопросы
        self.questions = [
            {"word": "apple", "correct": "яблоко", "options": ["яблоко", "груша", "апельсин", "банан"]},
            {"word": "car", "correct": "машина", "options": ["дом", "машина", "самолет", "поезд"]},
            {"word": "house", "correct": "дом", "options": ["квартира", "дом", "дача", "здание"]},
            {"word": "happy", "correct": "счастливый", "options": ["грустный", "счастливый", "злой", "уставший"]},
            {"word": "big", "correct": "большой", "options": ["маленький", "огромный", "большой", "средний"]}
        ]
        
        self.create_widgets()
        self.load_question()
    
    def create_widgets(self):
        """Создание виджетов"""
        # Верхняя панель
        header_frame = tk.Frame(self, bg=Colors.BG_WHITE)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Прогресс
        self.progress_label = tk.Label(
            header_frame,
            text=f"Вопрос 1 из {self.total_questions}",
            font=Fonts.BODY,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_GRAY
        )
        self.progress_label.pack(side=tk.LEFT, padx=20)
        
        # Кнопка выхода
        exit_btn = tk.Button(
            header_frame,
            text="✕ Выйти",
            command=self.exit_test,
            bg=Colors.ERROR,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            relief=tk.FLAT,
            cursor="hand2"
        )
        exit_btn.pack(side=tk.RIGHT, padx=20)
        
        # Основная область
        main_frame = tk.Frame(self, bg=Colors.BG_LIGHT)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)
        
        # Слово для перевода
        self.word_label = tk.Label(
            main_frame,
            text="",
            font=("Segoe UI", 32, "bold"),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT_DARK
        )
        self.word_label.pack(pady=50)
        
        # Варианты ответов
        self.buttons_frame = tk.Frame(main_frame, bg=Colors.BG_LIGHT)
        self.buttons_frame.pack(pady=30)
        
        self.option_buttons = []
        for i in range(4):
            btn = tk.Button(
                self.buttons_frame,
                text="",
                font=Fonts.BODY,
                bg=Colors.BG_WHITE,
                fg=Colors.TEXT_DARK,
                width=30,
                height=2,
                relief=tk.RAISED,
                cursor="hand2",
                command=lambda idx=i: self.check_answer(idx)
            )
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
            self.option_buttons.append(btn)
        
        # Кнопка "Далее"
        self.next_btn = tk.Button(
            main_frame,
            text="Далее →",
            command=self.next_question,
            bg=Colors.PRIMARY,
            fg=Colors.WHITE,
            font=("Segoe UI", 12, "bold"),
            padx=30,
            pady=10,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.next_btn.pack(pady=30)
    
    def load_question(self):
        """Загрузка текущего вопроса"""
        if self.current_question < self.total_questions:
            q = self.questions[self.current_question]
            self.word_label.config(text=q["word"])
            
            for i, option in enumerate(q["options"]):
                self.option_buttons[i].config(text=option, bg=Colors.BG_WHITE)
            
            self.selected_answer = None
            self.next_btn.config(state=tk.DISABLED)
            self.progress_label.config(text=f"Вопрос {self.current_question + 1} из {self.total_questions}")
    
    def check_answer(self, idx):
        """Проверка ответа"""
        q = self.questions[self.current_question]
        selected = self.option_buttons[idx].cget("text")
        
        if selected == q["correct"]:
            # Правильный ответ
            self.option_buttons[idx].config(bg=Colors.SUCCESS, fg=Colors.WHITE)
            if not self.selected_answer:
                self.correct_answers += 1
        else:
            # Неправильный ответ
            self.option_buttons[idx].config(bg=Colors.ERROR, fg=Colors.WHITE)
            # Подсвечиваем правильный ответ
            for btn in self.option_buttons:
                if btn.cget("text") == q["correct"]:
                    btn.config(bg=Colors.SUCCESS, fg=Colors.WHITE)
        
        self.selected_answer = selected
        self.next_btn.config(state=tk.NORMAL)
        
        # Блокируем все кнопки
        for btn in self.option_buttons:
            btn.config(state=tk.DISABLED)
    
    def next_question(self):
        """Следующий вопрос"""
        self.current_question += 1
        
        if self.current_question < self.total_questions:
            # Разблокируем кнопки
            for btn in self.option_buttons:
                btn.config(state=tk.NORMAL)
            self.load_question()
        else:
            self.show_results()
    
    def show_results(self):
        """Показать результаты теста"""
        percent = (self.correct_answers / self.total_questions) * 100
        
        result_window = tk.Toplevel(self)
        result_window.title("Результаты теста")
        result_window.geometry("400x300")
        result_window.resizable(False, False)
        result_window.transient(self)
        result_window.grab_set()
        
        # Центрируем
        result_window.update_idletasks()
        x = (result_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (result_window.winfo_screenheight() // 2) - (300 // 2)
        result_window.geometry(f"400x300+{x}+{y}")
        
        # Результаты
        tk.Label(result_window, text="Тест завершен!", font=Fonts.TITLE, fg=Colors.PRIMARY).pack(pady=20)
        
        if percent >= 80:
            icon = "🎉"
            message = "Отлично!"
        elif percent >= 60:
            icon = "👍"
            message = "Хорошо!"
        else:
            icon = "📚"
            message = "Нужно повторить!"
        
        tk.Label(result_window, text=icon, font=("Segoe UI", 48)).pack()
        tk.Label(result_window, text=message, font=Fonts.SUBTITLE).pack(pady=10)
        tk.Label(result_window, text=f"Правильных ответов: {self.correct_answers} из {self.total_questions}", font=Fonts.BODY).pack()
        tk.Label(result_window, text=f"Процент: {percent:.0f}%", font=Fonts.BODY_BOLD, fg=Colors.SUCCESS).pack(pady=10)
        
        def close_and_exit():
            result_window.destroy()
            self.exit_test()
        
        tk.Button(
            result_window,
            text="Закрыть",
            command=close_and_exit,
            bg=Colors.PRIMARY,
            fg=Colors.WHITE,
            padx=20,
            pady=5,
            cursor="hand2"
        ).pack(pady=20)
    
    def exit_test(self):
        """Выход из теста"""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти из теста?"):
            self.destroy()