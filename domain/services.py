class StudyService:
    def update_card_status_after_test(self, card_id: int, was_correct: bool) -> CardStatus:
        # Логика: если тест пройден → studied
        # Если ошибка → for_review
        pass

class TestService:
    def generate_multiple_choice(self, deck_id: int, num_questions: int = 4) -> list:
        # Возвращает список вопросов с 4 вариантами ответа
        pass