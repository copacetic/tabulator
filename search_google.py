import urllib.request, json
import lcs
import itertools
import operator

def get_most_common_word(sentences):
    substring_count = {}
    pairs = itertools.combinations(sentences, 2)
    print(list(pairs))
    for pair in pairs:
        x = lcs.LCS(pair[0], pair[1])
        print(x)
        if x in substring_count:
            substring_count[x] += 1
        else:
            substring_count[x] = 1
    return max(substring_count.items(), key=operator.itemgetter(1))[0]

if __name__ == "__main__":
    q="049000001327"
    url="http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q="+str(q)+"&hl=en&rsz=large"
    f = urllib.request.urlopen(url)
    x = f.read().decode('utf-8')
    z = json.loads(x)
    titles = []
    for m in z['responseData']['results']:
        titles.append(m['titleNoFormatting'])
    print(get_most_common_word(titles))    
    print(titles)
