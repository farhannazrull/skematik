import random

class Game:
    def __init__(self):
        self.players = []
        self.emails = {}
        self.scores = {}
        self.drawer_index = 0
        self.current_word = ""
        self.word_pool = ["cat", "tree", "car", "house", "pizza"]
        self.rounds = 3
        self.current_round = 0

    def add_player(self, username, email):
        if username not in self.players:
            self.players.append(username)
            self.emails[username] = email
            self.scores[username] = 0

    def remove_player(self, username):
        if username in self.players:
            self.players.remove(username)
            self.emails.pop(username, None)
            self.scores.pop(username, None)

    def start_game(self):
        self.current_round = 1
        self.drawer_index = 0
        self.select_word()

    def select_word(self):
        self.current_word = random.choice(self.word_pool)

    def get_drawer(self):
        if not self.players:
            return None
        return self.players[self.drawer_index]

    def check_guess(self, guess):
        return guess.strip().lower() == self.current_word.lower()

    def next_round(self):
        self.drawer_index = (self.drawer_index + 1) % len(self.players)
        if self.drawer_index == 0:
            self.current_round += 1
        self.select_word()

    def get_scores(self):
        return self.scores

    def get_winner(self):
        if not self.scores:
            return None
        return max(self.scores, key=self.scores.get)

    def get_email(self, username):
        return self.emails.get(username, None)

    def get_word_hint(self):
        return self.current_word[0] + "_" * (len(self.current_word) - 1)