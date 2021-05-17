import nltk
import sys

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
    import os

    # file_dict = {filename:[contents]}
    file_dict = dict()

    for a_file in os.listdir(directory):

        file_dir = os.path.join(directory, a_file)
        
        with open(file_dir, "r") as reader:

            file_content = reader.read() 

        # load file contents
        file_dict[a_file] = file_content
    
    return file_dict


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    import string

    # tokenize using nltk tokenizer
    tokens = nltk.word_tokenize(document)

    # convert all letters to lower cases
    tokens = [w.lower() for w in tokens]

    # create a mapping table using make.trans()
    # the third argument in mapped to None
    table = str.maketrans('', '', string.punctuation)

    # translate tokens using mapping table
    translated = [word.translate(table) for word in tokens]

    # Filter out non-alphabetic words
    all_alphabetics = []

    for word in translated:

        all_alpha = True

        for letter in word:

            if not letter.isalpha():

                all_alpha = False

                break
        
        if all_alpha:

            all_alphabetics.append(word)

    # Finally, remove stopwords
    stop_words = nltk.corpus.stopwords.words("english")
    filtered = [word for word in all_alphabetics if word not in stop_words]

    return filtered

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    import math

    word_idf = dict()

    # Total number of documents
    total_doc = len(documents)

    # list of all the words in documents dictionary values
    all_words = []

    for word_lst in documents.values():

        all_words.extend(word_lst)

    # set of all unique words
    vocab = set(all_words)

    # Find number of documents containing "word"
    # to find idf
    for word in vocab:

        count = 0  

        for word_lst in documents.values():

            if word in set(word_lst):
                count += 1
            
        word_idf[word] = math.log(total_doc / count)

    return word_idf


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # Initialize file score dictionary
    file_score = dict()

    for filename in files: 

        # list of words in a file
        file_words = files[filename]

        for word in query:

            if word not in file_words:
                continue
            
            # tf_idf = term frequency in a doc * idf of word
            tf_idf = file_words.count(word) * idfs[word]

            # file score is a sum of tf_idf of any word in
            # query that also appears in the file
            file_score[filename]= file_score.get(filename, 0) + tf_idf

    sorted_score = {k:v for k, v in sorted(file_score.items(), key = lambda item: -item[1])}

    return list(sorted_score.keys())[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # sentence score is a dict such that
    # sentence_score = {sentence:[idf, query_term_density]}
    sentence_score = dict()

    for sentence in sentences:

        sentence_words = sentences[sentence]
        common_count = 0.00
        matching_word_measure = 0.00

        for word in query:
            
            if word not in sentence_words:
                continue

            common_count += 1

            matching_word_measure += idfs[word]

        query_term_density = common_count / len(sentence_words)

        sentence_score[sentence] = [matching_word_measure, query_term_density]

    # sort dictionary first based on matching word measure
    # and for conflicting values sort based on query term density
    sorted_score = {
        k:v for k, v in sorted(
            sentence_score.items(), key = lambda item:(-item[1][0], -item[1][1])
        )
    }

    return list(sorted_score.keys())[:n]

if __name__ == "__main__":
    main()
