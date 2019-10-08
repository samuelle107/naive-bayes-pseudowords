#####################################################
# Author: Samuel Le
# Date: October 2, 2019
# Course: Statistical Natural Language Processing
# Purpose: Determine word sense using Naive Bayes
#############################################################
import json
import sys
import string

if (len(sys.argv) != 4):
    print('Enter python CreateContext.py <word1> <word2> <window_number>')
    exit()

# Remove residual HTML, punctuation, digits, and convert to lowercase
preprocessedCorpus = open("amazon_reviews.txt", 'r').read().lower().replace('&quot', '').translate(str.maketrans('', '', string.punctuation)).translate(str.maketrans('', '', string.digits)).split()

word1 = sys.argv[1].lower()
word2 = sys.argv[2].lower()
window = int(sys.argv[3])
pseudoWord = ''.join([word1, word2])

# Create a dictionary for the two word senses containing a list of the associated word sense, the word frequencies, and total word count
documents = {}
documents[word1] = {
    'totalWordCount': 0,
    'wordFrequency': {},
    'sentences': []
}
documents[word2] = {
    'totalWordCount': 0,
    'wordFrequency': {},
    'sentences': []
}

allSentences = []

wordCount = {}
# Loop through the corpus and create the context window.  Additionally save the original word and replace it with pseudoword
for i in range(len(preprocessedCorpus)):
    if preprocessedCorpus[i] in [word1, word2]:
        originalWord = preprocessedCorpus[i]
        
        # Count the word and increase count to correponding word sense
        try:
            wordCount[originalWord] += 1
        except KeyError:
            wordCount[originalWord] = 1

        preprocessedCorpus[i] = word1 + word2
        # Conver the list to a sentence
        sentence = ' '.join(preprocessedCorpus[i - (window + 1): i + (window + 1)])
        allSentences.append({
            'originalWord': originalWord,
            'modifiedSentence': sentence
        })

# Divide the data
trainingData = allSentences[ : int(len(allSentences) * 0.8)]
testingData = allSentences[int(len(allSentences) * 0.8) : ]

# Countsthe word frequencies of every sentence
for i in range(len(trainingData)):
    originalWord = trainingData[i]['originalWord']
    sentence = trainingData[i]['modifiedSentence']
    sentenceSplit = trainingData[i]['modifiedSentence'].split()

    documents[originalWord]['totalWordCount'] += 21
    documents[originalWord]['sentences'].append(sentence)

    # count freuqnecy of any word to a word sense and increment it to the corresponding word sense
    for w in sentenceSplit:
        try:
            documents[originalWord]['wordFrequency'][w] += 1
        except KeyError:
            documents[originalWord]['wordFrequency'][w] = 1

# These list will contain all the word frequencies correspodning to the word sense
word1Set = list(documents[word1]['wordFrequency'].keys())
word2Set = list(documents[word2]['wordFrequency'].keys())
# Will contain a list of all the unique words
uniqueWordList = list(set(word1Set) | set(word2Set))
documents['uniqueWords'] = uniqueWordList

probabilityData = {}
probabilityData[word1] = {}
probabilityData[word2] = {}

# Calculate P(class)
probabilityOfWord1 = len(documents[word1]['sentences']) / (len(documents[word1]['sentences']) + len(documents[word2]['sentences']))
probabilityOfWord2 = len(documents[word2]['sentences']) / (len(documents[word1]['sentences']) + len(documents[word2]['sentences']))

# Calculate P(word | class) for each word
for word in uniqueWordList:
    try:
        probabilityData[word1][word] = (documents[word1]['wordFrequency'][word] + 1) / (documents[word1]['totalWordCount'] + len(uniqueWordList))
    except:
        probabilityData[word1][word] = 1 / (documents[word1]['totalWordCount'] + len(uniqueWordList))

    try:
        probabilityData[word2][word] = (documents[word2]['wordFrequency'][word] + 1) / (documents[word2]['totalWordCount'] + len(uniqueWordList))
    except:
        probabilityData[word2][word] = 1 / (documents[word2]['totalWordCount'] + len(uniqueWordList))

results = {
    'accuracy': {},
    'sentenceData': []
}

results['accuracy'][word1] = {
    'frequency': 0,
    'correctPredictions': 0,
    'accuracy': 0
}

results['accuracy'][word2] = {
    'frequency': 0,
    'correctPredictions': 0,
    'accuracy': 0
}

correctPredictions = 0
# Try to predict the word sense of every sentence using Naive Bayes' Theorem
for x in testingData:
    sentence = x['modifiedSentence']
    v1 = probabilityOfWord1
    v2 = probabilityOfWord2

    for word in sentence.split():
        try:
            v1 *= probabilityData[word1][word]
            v2 *= probabilityData[word2][word]
        # If the word is not found in dictionary, multiple by 1.
        except KeyError:
            v1 *= 1
            v2 *= 1

    # The predicted word will be whatever yields the bigger v 
    predictedWord = word1 if v1 > v2 else word2

    originalWord = x['originalWord']

    results['accuracy'][originalWord]['frequency'] += 1

    if predictedWord == x['originalWord']:
        results['accuracy'][originalWord]['correctPredictions'] += 1
        correctPredictions += 1
    
    results['sentenceData'].append({
        'modifiedSentence': sentence,
        'originalWord': x['originalWord'],
        'predictedWord': predictedWord
    })

results['accuracy'][word1]['accuracy'] = results['accuracy'][word1]['correctPredictions'] / results['accuracy'][word1]['frequency']
results['accuracy'][word2]['accuracy'] = results['accuracy'][word2]['correctPredictions'] / results['accuracy'][word2]['frequency']
results['accuracy']['overall'] = correctPredictions / len(results['sentenceData'])

with open(word1 + '_' + word2 + '_results.json', 'w') as file:
    file.write(json.dumps(results, indent=4))
