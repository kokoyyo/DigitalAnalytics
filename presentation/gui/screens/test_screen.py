"""Экран тестирования с множественным выбором"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
from presentation.gui.styles import Colors, Fonts
from data.repositories import CardRepository, StatisticsRepository


class TestScreen(tk.Frame):
    """Экран тестирования"""
    
    def __init__(self, parent, deck_id, deck_name):
        super().__init__(parent, bg=Colors.BG_LIGHT)
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.card_repo = CardRepository()
        self.stats_repo = StatisticsRepository()
        
        self.questions = []
        self.current_question = 0
        self.correct_answers = 0
        self.start_time = time.time()
        self.user_answers = []
        self.selected_answer = None
        self.test_completed = False
        
        self.load_questions()
        self.create_widgets()
        self.update_question_display()
    
    def format_time(self, seconds):
        """Форматирование времени в минуты и секунды"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        if minutes > 0:
            return f"{minutes} мин {secs} сек"
        else:
            return f"{secs} сек"
    
    def load_questions(self):
        """Загрузка вопросов для теста"""
        cards = self.card_repo.get_by_deck(self.deck_id)
        
        if len(cards) < 4:
            messagebox.showwarning(
                "Недостаточно карточек", 
                f"В колоде '{self.deck_name}' недостаточно карточек для тестирования.\n"
                f"Требуется минимум 4 карточки.\n"
                f"Сейчас в колоде: {len(cards)} карточек."
            )
            self.go_back()
            return
        
        for card in cards:
            other_cards = [c for c in cards if c.id != card.id]
            random.shuffle(other_cards)
            
            options = [card.translation]
            for other in other_cards[:3]:
                options.append(other.translation)
            
            while len(options) < 4:
                options.append("???")
            
            random.shuffle(options)
            
            self.questions.append({
                'word': card.word,
                'correct': card.translation,
                'options': options,
                'card_id': card.id
            })
        
        random.shuffle(self.questions)
        self.total_questions = len(self.questions)
    
    def create_widgets(self):
        """Создание виджетов"""
        # Верхняя панель
        header_frame = tk.Frame(self, bg=Colors.BG_WHITE)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text=f"Тест: {self.deck_name}",
            font=Fonts.SUBTITLE,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_DARK
        ).pack(side=tk.LEFT, padx=20)
        
        self.progress_label = tk.Label(
            header_frame,
            text="",
            font=Fonts.BODY,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_GRAY
        )
        self.progress_label.pack(side=tk.LEFT, padx=20)
        
        self.exit_btn = tk.Button(
            header_frame,
            text="✕ Выйти",
            command=self.exit_test,
            bg=Colors.ERROR,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.exit_btn.pack(side=tk.RIGHT, padx=20)
        
        # Основная область
        self.main_frame = tk.Frame(self, bg=Colors.BG_LIGHT)
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)
        
        # Контейнер для вопросов
        self.question_container = tk.Frame(self.main_frame, bg=Colors.BG_LIGHT)
        
        # Слово для перевода
        self.word_label = tk.Label(
            self.question_container,
            text="",
            font=("Segoe UI", 32, "bold"),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT_DARK
        )
        self.word_label.pack(pady=50)
        
        # Варианты ответов
        self.buttons_frame = tk.Frame(self.question_container, bg=Colors.BG_LIGHT)
        self.buttons_frame.pack(pady=30)
        
        for i in range(2):
            self.buttons_frame.grid_columnconfigure(i, weight=1)
        
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
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="ew")
            self.option_buttons.append(btn)
        
        # Кнопка "Далее"
        self.next_btn = tk.Button(
            self.question_container,
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
        
        # Прогресс-бар
        self.progress_bar = ttk.Progressbar(
            self.question_container,
            style="Success.Horizontal.TProgressbar",
            maximum=self.total_questions,
            value=0
        )
        self.progress_bar.pack(fill=tk.X, pady=20)
        
        self.question_container.pack(expand=True, fill=tk.BOTH)
        self.update_progress_display()
    
    def _make_mousewheel_handler(self):
        """Возвращает плавный обработчик скролла колесиком"""
        def handler(event):
            if hasattr(event, 'delta') and event.delta != 0:
                delta = -1 * (event.delta // 30)
            elif event.num == 4:
                delta = -3
            elif event.num == 5:
                delta = 3
            else:
                return
            
            current_pos = self.canvas.yview()[0]
            new_pos = current_pos + (delta / 100)
            new_pos = max(0, min(1, new_pos))
            self.canvas.yview_moveto(new_pos)
            self.canvas.update_idletasks()
        return handler

    def _bind_mousewheel(self, widget):
        """Привязывает скролл к виджету и всем его дочерним элементам"""
        widget.bind("<MouseWheel>", self._mousewheel_handler, add="+")
        widget.bind("<Button-4>", self._mousewheel_handler, add="+")
        widget.bind("<Button-5>", self._mousewheel_handler, add="+")
        for child in widget.winfo_children():
            self._bind_mousewheel(child)


    def update_progress_display(self):
        """Обновление отображения прогресса"""
        if self.current_question > 0:
            percent = int((self.current_question / self.total_questions) * 100)
            self.progress_label.config(
                text=f"Вопрос {self.current_question} из {self.total_questions} ({percent}%)"
            )
            self.progress_bar.config(value=self.current_question)
        else:
            self.progress_label.config(
                text=f"Вопрос 1 из {self.total_questions} (0%)"
            )
            self.progress_bar.config(value=0)
    
    def update_question_display(self):
        """Обновление отображения вопроса"""
        if self.current_question < self.total_questions and not self.test_completed:
            q = self.questions[self.current_question]
            self.word_label.config(text=q['word'])
            
            for i, option in enumerate(q['options']):
                self.option_buttons[i].config(
                    text=option, 
                    bg=Colors.BG_WHITE, 
                    fg=Colors.TEXT_DARK,
                    state=tk.NORMAL
                )
            
            self.selected_answer = None
            self.next_btn.config(state=tk.DISABLED)
            self.update_progress_display()
    
    def check_answer(self, idx):
        """Проверка ответа"""
        if self.selected_answer is not None or self.test_completed:
            return
        
        q = self.questions[self.current_question]
        selected = self.option_buttons[idx].cget("text")
        
        is_correct = (selected == q['correct'])
        self.user_answers.append({
            'question': q['word'],
            'selected': selected,
            'correct': q['correct'],
            'is_correct': is_correct,
            'card_id': q['card_id']
        })
        
        if is_correct:
            self.option_buttons[idx].config(bg=Colors.SUCCESS, fg=Colors.WHITE)
            self.correct_answers += 1
        else:
            self.option_buttons[idx].config(bg=Colors.ERROR, fg=Colors.WHITE)
            for i, btn in enumerate(self.option_buttons):
                if btn.cget("text") == q['correct']:
                    btn.config(bg=Colors.SUCCESS, fg=Colors.WHITE)
        
        self.selected_answer = selected
        self.next_btn.config(state=tk.NORMAL)
        
        for btn in self.option_buttons:
            btn.config(state=tk.DISABLED)
    
    def next_question(self):
        """Следующий вопрос"""
        if self.selected_answer is None:
            return
        
        self.current_question += 1
        
        if self.current_question < self.total_questions:
            self.update_question_display()
        else:
            # Обновляем прогресс до 100% перед показом результатов
            self.progress_label.config(
                text=f"Вопрос {self.total_questions} из {self.total_questions} (100%)"
            )
            self.progress_bar.config(value=self.total_questions)
            self.show_results()
    
    def show_results(self):
        """Показать результаты на основном экране"""
        self.test_completed = True
        
        percent = (self.correct_answers / self.total_questions) * 100
        time_spent_seconds = int(time.time() - self.start_time)
        time_spent_minutes = round(time_spent_seconds / 60, 1)  # сохраняем с десятыми
        
        # Сохраняем результаты в БД (в минутах с десятыми)
        self.stats_repo.add_test_result(
            self.deck_id, 
            self.total_questions, 
            self.correct_answers, 
            time_spent_minutes
        )
        # ... остальной код
        
        # Если тест пройден (>=70%), отмечаем карточки как изученные
        if percent >= 70:
            self.card_repo.mark_deck_cards_as_studied(self.deck_id)
        
        # Меняем кнопку "Выйти" на "Закрыть"
        self.exit_btn.config(text="✓ Закрыть", command=self.go_back, bg=Colors.SUCCESS)
        
        # Очищаем контейнер с вопросами
        self.question_container.destroy()
        
        # Создаем контейнер для результатов
        results_container = tk.Frame(self.main_frame, bg=Colors.BG_LIGHT)
        results_container.pack(expand=True, fill=tk.BOTH)
        
        # Заголовок
        if percent >= 80:
            icon = "🎉"
            message = "Отлично! Вы отлично справились!"
            grade = "5"
            color = Colors.SUCCESS
        elif percent >= 70:
            icon = "👍"
            message = "Хорошо! Тест пройден!"
            grade = "4"
            color = Colors.INFO
        elif percent >= 50:
            icon = "📚"
            message = "Неплохо, но нужно повторить материал."
            grade = "3"
            color = Colors.WARNING
        else:
            icon = "😔"
            message = "Тест не пройден. Попробуйте еще раз!"
            grade = "2"
            color = Colors.ERROR
        
        # Результаты
        tk.Label(results_container, text=icon, font=("Segoe UI", 48), bg=Colors.BG_LIGHT).pack(pady=10)
        tk.Label(results_container, text=message, font=Fonts.SUBTITLE, fg=color, bg=Colors.BG_LIGHT).pack(pady=5)
        tk.Label(results_container, text=f"Оценка: {grade}", font=Fonts.BODY_BOLD, fg=color, bg=Colors.BG_LIGHT).pack(pady=5)
        
        # Статистика
        stats_frame = tk.Frame(results_container, bg=Colors.BG_LIGHT, relief=tk.RIDGE, bd=1)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(stats_frame, text=f"Правильных ответов: {self.correct_answers} из {self.total_questions}", 
                font=Fonts.BODY, bg=Colors.BG_LIGHT).pack(pady=5)
        tk.Label(stats_frame, text=f"Процент: {percent:.0f}%", font=Fonts.BODY_BOLD, fg=color, bg=Colors.BG_LIGHT).pack(pady=5)
        tk.Label(stats_frame, text=f"Время: {self.format_time(time_spent_seconds)}", 
                font=Fonts.BODY, bg=Colors.BG_LIGHT).pack(pady=5)
        
        # Вердикт
        if percent >= 70:
            tk.Label(stats_frame, text="✅ Тест пройден! Все карточки отмечены как изученные!", 
                    font=Fonts.BODY_BOLD, fg=Colors.SUCCESS, bg=Colors.BG_LIGHT).pack(pady=5)
        else:
            needed = 70 - percent
            tk.Label(stats_frame, text=f"❌ Тест не пройден. Нужно набрать минимум 70% для зачета.\n"
                    f"Не хватает {needed:.0f}%", 
                    font=Fonts.BODY_BOLD, fg=Colors.ERROR, bg=Colors.BG_LIGHT).pack(pady=5)
        
        # Вместо старого кода с canvas, вставьте этот:
        # Детали ответов (с прокруткой)
        details_frame = tk.LabelFrame(results_container, text="Детали ответов", 
                                    font=Fonts.BODY_BOLD, bg=Colors.BG_WHITE, fg=Colors.TEXT_DARK)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Canvas для прокрутки деталей
        self.canvas = tk.Canvas(details_frame, bg=Colors.BG_WHITE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=Colors.BG_WHITE)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Универсальный обработчик скролла
        self._mousewheel_handler = self._make_mousewheel_handler()
        self._bind_mousewheel(self.canvas)
        self._bind_mousewheel(self.scrollable_frame)

        # Заполняем детали
        for i, answer in enumerate(self.user_answers):
            color = Colors.SUCCESS if answer['is_correct'] else Colors.ERROR
            status = "✓" if answer['is_correct'] else "✗"
            
            frame = tk.Frame(self.scrollable_frame, bg=Colors.BG_WHITE)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(frame, text=f"{status} {answer['question']} → {answer['correct']}", 
                    font=Fonts.SMALL, bg=Colors.BG_WHITE, fg=color, anchor=tk.W).pack(fill=tk.X)
        
        # Кнопка "Пройти еще раз"
        btn_frame = tk.Frame(results_container, bg=Colors.BG_LIGHT)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="🔄 Пройти еще раз", command=self.restart_test,
                 bg=Colors.SECONDARY, fg=Colors.WHITE, padx=20, pady=5, cursor="hand2").pack(pady=5)
    
    def restart_test(self):
        """Перезапустить тест"""
        # Сбрасываем состояние
        self.current_question = 0
        self.correct_answers = 0
        self.start_time = time.time()
        self.user_answers = []
        self.selected_answer = None
        self.test_completed = False
        random.shuffle(self.questions)
        
        # Меняем кнопку обратно на "Выйти"
        self.exit_btn.config(text="✕ Выйти", command=self.exit_test, bg=Colors.ERROR)
        
        # Очищаем и пересоздаем интерфейс
        self.main_frame.destroy()
        self.main_frame = tk.Frame(self, bg=Colors.BG_LIGHT)
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)
        
        self.question_container = tk.Frame(self.main_frame, bg=Colors.BG_LIGHT)
        
        self.word_label = tk.Label(
            self.question_container,
            text="",
            font=("Segoe UI", 32, "bold"),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT_DARK
        )
        self.word_label.pack(pady=50)
        
        self.buttons_frame = tk.Frame(self.question_container, bg=Colors.BG_LIGHT)
        self.buttons_frame.pack(pady=30)
        
        for i in range(2):
            self.buttons_frame.grid_columnconfigure(i, weight=1)
        
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
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="ew")
            self.option_buttons.append(btn)
        
        self.next_btn = tk.Button(
            self.question_container,
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
        
        self.progress_bar = ttk.Progressbar(
            self.question_container,
            style="Success.Horizontal.TProgressbar",
            maximum=self.total_questions,
            value=0
        )
        self.progress_bar.pack(fill=tk.X, pady=20)
        
        self.question_container.pack(expand=True, fill=tk.BOTH)
        self.update_question_display()
    
    def exit_test(self):
        """Выход из теста без сохранения"""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти из теста?\nПрогресс не будет сохранен."):
            self.go_back()
    
    def go_back(self):
        """Вернуться к колоде"""
        from presentation.gui.screens.deck_detail_screen import DeckDetailScreen
        
        # Находим parent_container
        current = self
        parent_container = None
        while current:
            if hasattr(current, 'content_container'):
                parent_container = current.content_container
                break
            current = current.master
        
        if not parent_container:
            parent_container = self.master
        
        # Очищаем и создаем экран колоды
        for widget in parent_container.winfo_children():
            widget.destroy()
        
        deck_screen = DeckDetailScreen(parent_container, self.deck_id)
        deck_screen.pack(fill=tk.BOTH, expand=True)