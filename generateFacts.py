import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from collections import Counter
from heapq import nlargest
import json

def extract_facts_with_titles(text):
    # Load the English NLP model
    nlp = spacy.load("en_core_web_sm")
    
    # Process the text
    doc = nlp(text)
    
    # Calculate word frequencies
    word_frequencies = Counter()
    for word in doc:
        if word.text.lower() not in STOP_WORDS and word.text.lower() not in punctuation:
            word_frequencies[word.text] += 1
    
    # Normalize word frequencies
    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency
    
    # Calculate sentence scores
    sentence_scores = {}
    for sent in doc.sents:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]
    
    # Extract top sentences as facts
    select_length = min(5, len(sentence_scores))
    summary_sentences = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    
    def generate_title(sentence):
        # Try to find a named entity for the title
        for ent in sentence.ents:
            if ent.label_ in ['ORG', 'PERSON', 'GPE', 'PRODUCT']:
                return ent.text

        # If no suitable named entity, use the subject of the sentence
        for token in sentence:
            if token.dep_ == 'nsubj':
                return token.text

        # If no subject found, use the first noun chunk
        for chunk in sentence.noun_chunks:
            return chunk.text

        # If all else fails, return the first three words
        return ' '.join([token.text for token in sentence[:3]])

    # Create fact dictionary with relevant titles
    facts = []
    for sentence in summary_sentences:
        title = generate_title(sentence)
        facts.append({"question": title, "answer": sentence.text.strip()})
    
    return facts

# Function to save facts to a JSON file
import json
import os

def save_facts_to_json(facts, filename="extracted_facts.json"):
    # Check if the file exists and load existing data
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    else:
        existing_data = {"questions": []}
    
    # Append new facts to the existing data
    existing_data["questions"].extend(facts)
    
    # Save the combined data back to the file
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4)



# Example usage
text = """
SpaceX is an American aerospace manufacturer and space transportation services company headquartered in Hawthorne, California. It was founded in 2002 by Elon Musk with the goal of reducing space transportation costs to enable the colonization of Mars. SpaceX has developed several launch vehicles, including the Falcon 9 and Falcon Heavy, and the Dragon spacecraft, which is flown into orbit by the Falcon 9 and Falcon Heavy launch vehicles to supply the International Space Station (ISS) with cargo. SpaceX's achievements include the first privately funded liquid-propellant rocket to reach orbit, the first private company to successfully launch, orbit, and recover a spacecraft, and the first private company to send a spacecraft to the ISS. In 2020, SpaceX became the first private company to send astronauts to the ISS as part of NASA's Commercial Crew Program.
"""

facts = extract_facts_with_titles(text)
save_facts_to_json(facts)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # If a file path is provided as an argument, read from the file
        with open(sys.argv[1], 'r', encoding='utf-8') as file:
            input_text = file.read()
    else:
        # Otherwise, use the example text
        input_text = text

    extracted_facts = extract_facts_with_titles(input_text)
    save_facts_to_json(extracted_facts)
    print("Facts have been saved to extracted_facts.json")
