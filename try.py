import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import difflib  # for fuzzy matching

class Flashcard:
    def __init__(self, german, english=None, examples=None):
        self.german = german
        self.english = english if english else ["", "", ""]
        self.examples = examples if examples else ["", "", ""]

    def to_dict(self):
        return {
            "german": self.german,
            "english": self.english,
            "examples": self.examples
        }

    @staticmethod
    def from_dict(data):
        english = data.get("english", ["", "", ""])
        examples = data.get("examples", ["", "", ""])
        return Flashcard(
            data["german"],
            english + [""] * (3 - len(english)),
            examples + [""] * (3 - len(examples))
        )

class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("German Flashcard App")
        self.flashcards = []
        self.filename = "flashcards.json"
        self.load_flashcards()

        self.listbox = tk.Listbox(root, width=50)
        self.listbox.pack(pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Add Flashcard", command=self.add_flashcard).grid(row=0, column=0)
        tk.Button(btn_frame, text="Edit Flashcard", command=self.edit_flashcard).grid(row=0, column=1)
        tk.Button(btn_frame, text="Delete Flashcard", command=self.delete_flashcard).grid(row=0, column=2)
        tk.Button(btn_frame, text="Practice", command=self.practice_flashcards).grid(row=0, column=3)

        self.refresh_listbox()

    def save_flashcards(self):
        data = [fc.to_dict() for fc in self.flashcards]
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_flashcards(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    self.flashcards = [Flashcard.from_dict(d) for d in data]
                except json.JSONDecodeError:
                    messagebox.showerror("Error", "Could not load flashcards.")

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for card in sorted(self.flashcards, key=lambda c: c.german.lower()):
            self.listbox.insert(tk.END, card.german)

    def get_flashcard_data(self, card=None):
        data_window = tk.Toplevel(self.root)
        data_window.title("Flashcard Data")

        labels = ["German Word", "English 1", "English 2", "English 3",
                  "Example 1", "Example 2", "Example 3"]
        entries = []

        for i, label in enumerate(labels):
            tk.Label(data_window, text=label).grid(row=i, column=0)
            entry = tk.Entry(data_window, width=50)
            entry.grid(row=i, column=1)
            if card:
                if i == 0:
                    entry.insert(0, card.german)
                elif 1 <= i <= 3:
                    entry.insert(0, card.english[i - 1])
                else:
                    entry.insert(0, card.examples[i - 4])
            entries.append(entry)

        def submit():
            german = entries[0].get().strip()
            english = [e.get().strip() for e in entries[1:4]]
            examples = [e.get().strip() for e in entries[4:]]
            if not german or not examples[0] or not examples[1]:
                messagebox.showwarning("Input Error", "Please enter the German word and at least two examples.")
                return None
            data_window.destroy()
            return Flashcard(german, english, examples)

        submit_button = tk.Button(data_window, text="Submit", command=lambda: setattr(data_window, 'result', submit()))
        submit_button.grid(row=7, columnspan=2)

        data_window.wait_window()
        return getattr(data_window, 'result', None)

    def add_flashcard(self):
        new_card = self.get_flashcard_data()
        if new_card:
            self.flashcards.append(new_card)
            self.save_flashcards()
            self.refresh_listbox()

    def edit_flashcard(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Edit Flashcard", "Please select a flashcard to edit.")
            return
        index = selection[0]
        card = self.flashcards[index]
        updated_card = self.get_flashcard_data(card)
        if updated_card:
            self.flashcards[index] = updated_card
            self.save_flashcards()
            self.refresh_listbox()

    def delete_flashcard(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Delete Flashcard", "Please select a flashcard to delete.")
            return
        index = selection[0]
        card = self.flashcards[index]
        confirm = messagebox.askyesno("Confirm Delete", f"Delete '{card.german}'?")
        if confirm:
            del self.flashcards[index]
            self.save_flashcards()
            self.refresh_listbox()

    def practice_flashcards(self):
        if not self.flashcards:
            messagebox.showinfo("Practice", "No flashcards to practice.")
            return

        for card in self.flashcards:
            user_input = simpledialog.askstring("Practice", f"What is the meaning of '{card.german}'?")
            if user_input is None:
                continue

            user_input = user_input.strip().lower()
            correct_list = [e.strip().lower() for e in card.english if e.strip()]
            match = any(user_input == word for word in correct_list)

            if not match:
                # Try fuzzy matching for suggestions
                suggestion = difflib.get_close_matches(user_input, correct_list, n=1, cutoff=0.75)
                if suggestion:
                    feedback = f"❌ Not quite. Did you mean: '{suggestion[0]}'?\n\nCorrect: {', '.join(card.english)}"
                else:
                    feedback = f"❌ Incorrect.\nCorrect: {', '.join(card.english)}"
            else:
                feedback = "✅ Correct!"

            examples = "\n".join([f"• {ex}" for ex in card.examples if ex.strip()])
            messagebox.showinfo("Answer", f"{feedback}\n\nExamples:\n{examples}")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()
