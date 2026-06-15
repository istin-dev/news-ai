from django.db import models

# Since all MCQs are stored directly on the News model,
# we don't need a complex quiz schema. We can log attempts for analytics.
class QuizAttempt(models.Model):
    category = models.CharField(max_length=50, blank=True, null=True)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz Attempt on {self.attempted_at} - Score: {self.correct_answers}/{self.total_questions}"
