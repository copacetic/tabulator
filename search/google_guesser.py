import urllib.request, json
import itertools
import operator
import string


def LongestCommonSubstring(S1, S2):
    #THIS CODE IS NOT MINE
    #CREDITS TO: http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Longest_common_substring#Python
    M = [[0]*(1+len(S2)) for i in range(1+len(S1))]
    longest, x_longest = 0, 0
    for x in range(1,1+len(S1)):
        for y in range(1,1+len(S2)):
            if S1[x-1] == S2[y-1]:
                M[x][y] = M[x-1][y-1] + 1
                if M[x][y]>longest:
                    longest = M[x][y]
                    x_longest  = x
            else:
                M[x][y] = 0
    return S1[x_longest-longest: x_longest]

def get_most_common_word(sentences):
    temp = []
    for sentence in sentences:
        for char in string.punctuation:
            sentence = sentence.replace(char, '')
        temp.append(sentence)
    sentences = temp
    substring_count = {}
    pairs = itertools.combinations(sentences, 2)
    pairs = list(pairs)
    for pair in pairs:
        x = LongestCommonSubstring(pair[0], pair[1])
        longest = ''.join(x)
        if longest in substring_count:
            substring_count[longest] += 1
        else:
            substring_count[longest] = 1
    if substring_count == {}:
        return None
    return max(substring_count.items(), key=operator.itemgetter(1))[0]

def guess(q):
    url="http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q="+str(q)+"&hl=en&rsz=large"
    ajaxURL = urllib.request.urlopen(url)
    jsonBytes = ajaxURL.read().decode('utf-8')
    json_data = json.loads(jsonBytes)
    titles = []
    for result in json_data['responseData']['results']:
        titles.append(str(result['titleNoFormatting']))
    return get_most_common_word(titles)

