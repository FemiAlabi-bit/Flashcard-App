import json
import os
import random

# Flashcard class
class Flashcard:
    def __init__(self, german, english1="", english2="", english3="", example1="", example2="", example3=""):
        self.german = german
        self.english = [english1, english2, english3]
        self.examples = [example1, example2, example3]

    def to_dict(self):
        return {
            "german": self.german,
            "english": self.english,
            "examples": self.examples
        }

    @staticmethod
    def from_dict(data):
        english = data["english"]
        if isinstance(english, str):
            english = [english]

        examples = data["examples"] if isinstance(data["examples"], list) else [data["examples"]]

        return Flashcard(
            data["german"],
            *(english + [""] * (3 - len(english))),
            *(examples + [""] * (3 - len(examples)))
        )

    def show(self):
        print(f"\n 🗒️✍️  {self.german} → {', '.join([e for e in self.english if e.strip()])}")
        for i, ex in enumerate(self.examples):
            if ex.strip():
                print(f"  → Beispiel {i+1}: {ex}")

# FlashcardManager class
class FlashcardManager:
    def __init__(self, filename="flashcards.json"):
        self.filename = filename
        self.flashcards = []
        self.load()

    def add_flashcard(self):
        german = input("🔹 Deutsches Wort: ").strip()
        english1 = input("🔸 Englische Bedeutung 1: ").strip()
        english2 = input("🔸 Englische Bedeutung 2 (optional): ").strip()
        english3 = input("🔸 Englische Bedeutung 3 (optional): ").strip()

        example1 = input(" → Beispiel 1 (Pflicht ⚠️  bitte einen deutschen Satz eingeben): ").strip()
        example2 = input(" → Beispiel 2 (Pflicht ⚠️  bitte einen deutschen Satz eingeben): ").strip()
        example3 = input(" Beispiel 3 (optional  deutscher Satz): ").strip()

        if not (example1 and example2):
            print("❗ Du hast keine zwei Beispiele eingegeben. Die Flashcard wird nicht gespeichert.")
            return

        card = Flashcard(german, english1, english2, english3, example1, example2, example3)
        self.flashcards.append(card)
        self.save()

    def save(self):
        data = [fc.to_dict() for fc in self.flashcards]
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    self.flashcards = [Flashcard.from_dict(item) for item in data]
                except json.JSONDecodeError:
                    print("⚠️ Fehler beim Laden der Datei.")

    def show_all(self):
        if not self.flashcards:
            print("\n📭 Keine Flashcards vorhanden.")
            return

        print("\n📚 Deine gespeicherten Flashcards:")
        for card in self.flashcards:
            card.show()

    def list_words(self):
        if not self.flashcards:
            print("\n📭 Keine Flashcards vorhanden.")
            return

        print("\n🔠 Verfügbare Wörter:")
        for i, card in enumerate(sorted(self.flashcards, key=lambda c: c.german.lower()), start=1):
            print(f"{i}. {card.german}")

    def edit_flashcard(self):
        if not self.flashcards:
            print("\n📭 Keine Flashcards vorhanden.")
            return

        self.list_words()

        word = input("\n🔍 Welches deutsches Wort möchtest du bearbeiten? ").strip()
        card = self.find_flashcard(word)

        if not card:
            print("❌ Wort nicht gefunden.")
            return

        print("✏️ Neue Werte eingeben (Enter drücken, um alten Wert zu behalten):")

        new_german = input(f"Deutsches Wort ({card.german}): ").strip()
        new_english1 = input(f"Englisch 1 ({card.english[0]}): ").strip()
        new_english2 = input(f"Englisch 2 ({card.english[1]}): ").strip()
        new_english3 = input(f"Englisch 3 ({card.english[2]}): ").strip()
        new_example1 = input(f"Beispiel 1 ({card.examples[0]}): ").strip()
        new_example2 = input(f"Beispiel 2 ({card.examples[1]}): ").strip()
        new_example3 = input(f"Beispiel 3 ({card.examples[2]}): ").strip()

        if new_german:
            card.german = new_german
        if new_english1:
            card.english[0] = new_english1
        if new_english2:
            card.english[1] = new_english2
        if new_english3:
            card.english[2] = new_english3
        if new_example1:
            card.examples[0] = new_example1
        if new_example2:
            card.examples[1] = new_example2
        if new_example3:
            card.examples[2] = new_example3

        self.save()
        print("✅ Flashcard wurde aktualisiert.")

    def delete_flashcard(self):
        if not self.flashcards:
            print("\n📭 Keine Flashcards vorhanden.")
            return

        self.list_words()

        word = input("\n❌ Welches deutsches Wort möchtest du löschen? ").strip()
        card = self.find_flashcard(word)

        if not card:
            print("❌ Wort nicht gefunden.")
            return

        confirm = input(f"Bist du sicher, dass du '{card.german}' löschen möchtest? (ja/nein): ").strip().lower()
        if confirm == "ja":
            self.flashcards.remove(card)
            self.save()
            print("✅ Flashcard wurde gelöscht.")
        else:
            print("🚫 Abgebrochen.")

    def find_flashcard(self, german_word):
        for card in self.flashcards:
            if card.german.lower() == german_word.lower():
                return card
        return None

    def practice(self):
        if not self.flashcards:
            print("\n📭 Keine Flashcards zum Üben vorhanden.")
            return

        print("\n📚▶️  Übungsmodus gestartet!")
        random.shuffle(self.flashcards)

        for card in self.flashcards:
            print(f"\n🔹 Was ist die Bedeutung von '{card.german}'?")
            answer = input("Deine Antwort: ").strip()

            if answer.lower() in [e.lower() for e in card.english if e.strip()]:
                print("✅ Richtig!")
            else:
                print(f"❌ Falsch! Mögliche richtige Antworten: {', '.join([e for e in card.english if e.strip()])}")

            print("\nBeispiele:")
            card.show()
            input("\nDrücke Enter, um zur nächsten Karte zu gehen.")

# Main menu function
def main():
    manager = FlashcardManager()

    while True:
        print("\n===== Flashcard App Menü =====")
        print("1️⃣  Neue Flashcard hinzufügen")
        print("2️⃣  Alle Flashcards anzeigen")
        print("3️⃣  Flashcard bearbeiten")
        print("4️⃣  Flashcard löschen")
        print("5️⃣  Übungsmodus starten")
        print("6️⃣  Beenden")

        choice = input("Wähle eine Option: ").strip()

        if choice == "1":
            manager.add_flashcard()
        elif choice == "2":
            manager.show_all()
        elif choice == "3":
            manager.edit_flashcard()
        elif choice == "4":
            manager.delete_flashcard()
        elif choice == "5":
            manager.practice()
        elif choice == "6":
            print("👋 Programm wird beendet.")
            break
        else:
            print("❌ Ungültige Eingabe. Bitte versuche es erneut.")

if __name__ == "__main__":
    main()
