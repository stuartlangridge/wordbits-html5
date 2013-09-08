# Parse the wordnet dictionary and get words that we like
import re
import json

lexnames = {
    "00": {"name":"adj.all", 
            "desc": "all adjective clusters"},
    "01": {"name":"adj.pert", 
            "desc":    "relational adjectives (pertainyms)"},
    "02": {"name":"adv.all", 
            "desc": "all adverbs"},
    "03": {"name":"noun.Tops", 
            "desc":   "unique beginner for nouns"},
    "04": {"name":"noun.act", 
            "desc":    "nouns denoting acts or actions"},
    "05": {"name":"noun.animal", 
            "desc": "nouns denoting animals"},
    "06": {"name":"noun.artifact", 
            "desc":   "nouns denoting man-made objects"},
    "07": {"name":"noun.attribute", 
            "desc":  "nouns denoting attributes of people and objects"},
    "08": {"name":"noun.body", 
            "desc":   "nouns denoting body parts"},
    "09": {"name":"noun.cognition", 
            "desc":  "nouns denoting cognitive processes and contents"},
    "10": {"name":"noun.communication", 
            "desc":  "nouns denoting communicative processes and contents"},
    "11": {"name":"noun.event", 
            "desc":  "nouns denoting natural events"},
    "12": {"name":"noun.feeling", 
            "desc":    "nouns denoting feelings and emotions"},
    "13": {"name":"noun.food", 
            "desc":   "nouns denoting foods and drinks"},
    "14": {"name":"noun.group", 
            "desc":  "nouns denoting groupings of people or objects"},
    "15": {"name":"noun.location", 
            "desc":   "nouns denoting spatial position"},
    "16": {"name":"noun.motive", 
            "desc": "nouns denoting goals"},
    "17": {"name":"noun.object", 
            "desc": "nouns denoting natural objects (not man-made)"},
    "18": {"name":"noun.person", 
            "desc": "nouns denoting people"},
    "19": {"name":"noun.phenomenon", 
            "desc": "nouns denoting natural phenomena"},
    "20": {"name":"noun.plant", 
            "desc":  "nouns denoting plants"},
    "21": {"name":"noun.possession", 
            "desc": "nouns denoting possession and transfer of possession"},
    "22": {"name":"noun.process", 
            "desc":    "nouns denoting natural processes"},
    "23": {"name":"noun.quantity", 
            "desc":   "nouns denoting quantities and units of measure"},
    "24": {"name":"noun.relation", 
            "desc":   "nouns denoting relations between people or things or ideas"},
    "25": {"name":"noun.shape", 
            "desc":  "nouns denoting two and three dimensional shapes"},
    "26": {"name":"noun.state", 
            "desc":  "nouns denoting stable states of affairs"},
    "27": {"name":"noun.substance", 
            "desc":  "nouns denoting substances"},
    "28": {"name":"noun.time", 
            "desc":   "nouns denoting time and temporal relations"},
    "29": {"name":"verb.body", 
            "desc":   "verbs of grooming, dressing and bodily care"},
    "30": {"name":"verb.change", 
            "desc": "verbs of size, temperature change, intensifying, etc."},
    "31": {"name":"verb.cognition", 
            "desc":  "verbs of thinking, judging, analyzing, doubting"},
    "32": {"name":"verb.communication", 
            "desc":  "verbs of telling, asking, ordering, singing"},
    "33": {"name":"verb.competition", 
            "desc":    "verbs of fighting, athletic activities"},
    "34": {"name":"verb.consumption", 
            "desc":    "verbs of eating and drinking"},
    "35": {"name":"verb.contact", 
            "desc":    "verbs of touching, hitting, tying, digging"},
    "36": {"name":"verb.creation", 
            "desc":   "verbs of sewing, baking, painting, performing"},
    "37": {"name":"verb.emotion", 
            "desc":    "verbs of feeling"},
    "38": {"name":"verb.motion", 
            "desc": "verbs of walking, flying, swimming"},
    "39": {"name":"verb.perception", 
            "desc": "verbs of seeing, hearing, feeling"},
    "40": {"name":"verb.possession", 
            "desc": "verbs of buying, selling, owning"},
    "41": {"name":"verb.social", 
            "desc": "verbs of political and social activities and events"},
    "42": {"name":"verb.stative", 
            "desc":    "verbs of being, having, spatial relations"},
    "43": {"name":"verb.weather", 
            "desc":    "verbs of raining, snowing, thawing, thundering"},
    "44": {"name":"adj.ppl", 
            "desc": "participial adjectives"},
}

def longest_common_substring(s1, s2):
    m = [[0] * (1 + len(s2)) for i in xrange(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in xrange(1, 1 + len(s1)):
        for y in xrange(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]

def getwords(wordtype):
    fp=open('/usr/share/wordnet/index.%s' % wordtype)
    idx = [l.split() for l in fp.readlines() if l.split() and not l.startswith('#')]
    fp.close()
    mat = [{"word": x[0], "offset": int(x[-1])} for x in idx 
        if re.match("^[a-z]+$", x[0]) and len(x[0]) > 5 and len(x[0]) < 13 and x[2] == "1"
        and x[0][-1] != "a" and x[0][-2:] != "ae"] # exclude words ending in a, 'cos Latin
    okwords = {}
    fp = open('/usr/share/wordnet/data.%s' % wordtype)
    for m in mat:
        fp.seek(m["offset"])
        line = fp.read(400)
        parts = line.split("|")
        word_metadata = parts[0].split()
        lex_file = lexnames[word_metadata[1]]["name"]

        if len(parts) >= 2 and "\n" in parts[1]:
            defn = parts[1].split("\n")[0].strip()
            if len(defn) < 30 and not re.search("[A-Z]", defn):
                # find lcs, to avoid definitions which are stupid, such as
                # "countertop: the top of a counter"
                lcs = longest_common_substring(defn.upper(), m["word"].upper())
                if len(lcs) < 5 and lex_file not in ["noun.animal", "noun.plant"]:
                    okwords[m["word"]] = defn
    fp.close()
    return okwords

words = {"ubuntu": "an operating system for human beings"}
words.update(getwords("noun"))
words.update(getwords("verb"))
words.update(getwords("adj"))
words.update(getwords("adv"))

fp = open("words.js", "w")
fp.write("GLOBALS.wordload(%s)" % json.dumps(words.items()))
fp.close()

print "Dictionary contains %s words" % len(words.keys())
