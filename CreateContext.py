import json
import sys
import string

if (len(sys.argv) != 3):
    print('Enter python CreateContext.py <word1> <word2>')
    exit()

preprocessedCorpus = open("amazon_reviews.txt", 'r').read().lower().replace('&quot', '').translate(str.maketrans('', '', string.punctuation)).translate(str.maketrans('', '', string.digits)).split()

word1 = sys.argv[1]
word2 = sys.argv[2]
pseudoWord = ''.join([word1, word2])

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

for i in range(len(preprocessedCorpus)):
    if preprocessedCorpus[i] in [word1, word2]:
        originalWord = preprocessedCorpus[i]
        preprocessedCorpus[i] = word1 + word2
        sentence = ' '.join(preprocessedCorpus[i - 11: i + 11])
        allSentences.append({
            'originalWord': originalWord,
            'modifiedSentence': sentence
        })

trainingData = allSentences[: int(len(allSentences) * 0.8)]
testingData = allSentences[int(len(allSentences) * 0.8): ]

for i in range(len(trainingData)):
    originalWord = trainingData[i]['originalWord']
    sentence = trainingData[i]['modifiedSentence']
    sentenceSplit = trainingData[i]['modifiedSentence'].split()

    documents[originalWord]['totalWordCount'] += 21
    documents[originalWord]['sentences'].append(sentence)

    for w in sentenceSplit:
        try:
            documents[originalWord]['wordFrequency'][w] += 1
        except KeyError:
            documents[originalWord]['wordFrequency'][w] = 1

word1Set = list(documents[word1]['wordFrequency'].keys())
word2Set = list(documents[word2]['wordFrequency'].keys())
uniqueWordList = list(set(word1Set) | set(word2Set))
documents['uniqueWords'] = uniqueWordList

probabilityData = {}
probabilityData[word1] = {}
probabilityData[word2] = {}

probabilityOfWord1 = len(documents[word1]['sentences']) / (len(documents[word1]['sentences']) + len(documents[word2]['sentences']))
probabilityOfWord2 = len(documents[word2]['sentences']) / (len(documents[word1]['sentences']) + len(documents[word2]['sentences']))

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
    'accuracy': 0,
    'sentenceData': []
}

correctPredictions = 0
for x in testingData:
    sentence = x['modifiedSentence']
    v1 = probabilityOfWord1
    v2 = probabilityOfWord2

    for word in sentence.split():
        try:
            v1 *= probabilityData[word1][word]
            v2 *= probabilityData[word2][word]
        except KeyError:
            v1 *= 1
            v2 *= 1

    predictedWord = word1 if v1 > v2 else word2
    if predictedWord == x['originalWord']:
        correctPredictions += 1
    
    results['sentenceData'].append({
        'modifiedSentence': sentence,
        'originalWord': x['originalWord'],
        'predictedWord': predictedWord
    })
    results['accuracy'] = correctPredictions / len(results['sentenceData'])

with open(word1 + '_' + word2 + '_results.json', 'w') as file:
    file.write(json.dumps(results, indent=4))
