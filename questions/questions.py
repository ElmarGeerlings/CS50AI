import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    # Initialise output dictionary
    file_dict = {}

    # Iterate through every file in directory
    for filename in os.listdir(directory):
        # Check if a txt-file
        if filename.endswith('.txt'):
            # Switch to file path
            file_path = os.path.join(directory, filename)
            # Read contents of file and add to output dictionary
            with open(file_path, 'r') as file:
                file_text = file.read()
                file_dict[filename] = file_text

    # Return a dictionary mapping filename with contents
    return file_dict


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    # Tokenize document text in lowercase
    tokenized = nltk.word_tokenize(document.lower())

    wordslist=[]
    # Iterate through every word in tokenized text
    for word in tokenized:
        # Continue if stopword
        if word in nltk.corpus.stopwords.words("english"):
            continue
        else:
            # Check if there is punctuation
            all_punct = True
            for char in word:
                if char not in string.punctuation:
                    all_punct = False
                    break
            # Add word to list of all the words in document
            if not all_punct:
                wordslist.append(word)

    # Return list of words in the document
    return wordslist


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # Number of documents
    n = len(documents)
    # Dictionary to store idf value for each word
    idfs = dict()

    # Go through every document
    for document in documents:
        # Create a set of unique words in the document
        words = set(documents[document])
        # Update count for every word in document
        for word in words:
            # Add 1 to document count for word
            if word not in idfs:
                idfs[word] = 1
            else:
                idfs[word] += 1

    # Calculate idf value for each word
    for word in idfs:
        # Apply idf formula
        idfs[word] = math.log((n / idfs[word]))

    # Return dictionary with idf value for each word
    return idfs

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # Empty list to store tf-idf value for every file
    tf_list = []
    # Iterate through every file
    for file in files:
        # Initialise tf-idf value
        tf_idf = 0
        # Calculate tf_idf value for every word in query
        for word in query:
            # Count term frequency
            tf = files[file].count(word)
            # Multiply term frequency with idf value
            tf_idf_word = tf * idfs[word]
            # Sum up tf-idf value
            tf_idf = tf_idf + tf_idf_word
        # Add filename and tf-idf value to list
        tf_list.append((file,tf_idf))

    # Sort based on tf-idf value
    sortedlist = sorted(tf_list, key=lambda item: item[1], reverse=True)

    # Make a list of only the filenames without the tf-idf values
    filenames = []
    for filename in sortedlist:
        filenames.append(filename[0])

    # Return a list of n filenames ranked on their tf-idf value
    return filenames[:n]

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentencelist = []
    # Loop through every sentence
    for sentence in sentences:
        # Intialise idf value for sentence and wordcount
        idf = 0
        wordcount = 0
        # Loop through every word in query
        for word in query:
            # Check if word appears in sentence
            if word in sentences[sentence]:
                idf += idfs[word]
                wordcount += sentences[sentence].count(word)
        # Calculate query term density by dividing wordcount by length of sentence
        qtd = wordcount / len(nltk.word_tokenize(sentence))
        # Append sentence with idf and qtd
        sentencelist.append((sentence, idf, qtd))

    # Sort sentencelist
    sortedlist = sorted(sentencelist, key=lambda item: (item[1], item[2]), reverse=True)

    # Make a list of only the sentences without idf and qtd values
    rankedsentences = []
    for row in sortedlist:
        rankedsentences.append(row[0])

    # Return ranked list of n sentencens
    return rankedsentences[:n]

if __name__ == "__main__":
    main()
