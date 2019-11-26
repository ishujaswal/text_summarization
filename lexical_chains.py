
# coding: utf-8

# In[104]:

"""
    LEXICAL CHAIN - TEXT SUMMARIZATION
    ISHU JASWAL
"""

# -*- coding: utf-8 -*-
import nltk
from collections import Counter, defaultdict
from nltk.corpus import wordnet as wn
import argparse


def get_data(filename):
    """
        Method to read data from a file
        param: filename
        returns: data converted to lowercase
    """
    with open(filename, 'r') as fp:
        data = fp.read().lower()
    return data

def get_tokens(data):
    """
        Method to tokenize data 
        param: data
        returns: tokens
    """
    tokens = nltk.tokenize.word_tokenize(data)
    return tokens

def get_nouns(tokens):
    """
        Method to extract NOUNS from tokens using POS TAGS 
        param: tokens
        returns: list of NOUNS
    """
    nouns = []
    postags = nltk.pos_tag(tokens)
    for word in postags:
        if word[1] in ['NN','NNS', 'NNP', 'NNPS']:
            nouns.append(word[0])
    return nouns


def create_lexical_chains(nouns, token_count):
    """
        Method to create lexical chains of nouns related by 
        Synonyms, Antonyms, Hypernyms, Hyponyms 
        param: nouns, token_count
        returns: 
            dictionary of lexical chains 
            formatted as: Chain <number>: [list of related words which are present in text]
    """
    count = 0
    lexical_chain = {}
    for noun in nouns:   
        chain = []
        try:
            for synset in wn.synsets(noun):
                for lemma in synset.lemmas():
                    if lemma.name() in token_count:
                        chain.append(lemma.name())
                        del token_count[lemma.name()]
                    if lemma.antonyms():
                        for antonym in lemma.antonyms():
                            if antonym in token_count:
                                chain.append(antonym)
                                del token_count[antonym]
                if synset.hypernyms():
                    for hyper in synset.hypernyms():
                        if hyper in token_count:
                            chain.append(hyper)
                            del token_count[hyper]
                if synset.hyponyms():
                    for hypo in synset.hyponyms():
                        if hypo in token_count:
                            chain.append(hypo)
                            del token_count[hypo]
        except:
            pass
        
        if len(chain) > 0:
            lexical_chain['Chain '+str(count)] = chain
            count = count + 1
    
    return lexical_chain


def print_lexical_chains(lexical_chains, token_count):
    """
        Method to print formatted lexical chains 
        param: lexical_chains, token_count
    """
    for key, value in lexical_chains.items():
        if len(value) > 0:
            print key, ":",
            print [str(val) +"("+str(token_count[val])+")" for val in value]

            
def homogenity(length, distinct_words):
    """
        Method to calculate homogenity
        param: length, distinct_words
        returns homogenity as similarity measure for chains
    """
    return float(1.0 - float(distinct_words)/float(length))
    
    
def score_lexical_chains(lexical_chain, token_count):
    """
        Method to assign a score per lexical chain
        to filter out lexical chains
        param: lexical_chain, token_count
        returns chain score
    """
    chain_score = {}
    for no, chain in lexical_chain.items():
        length = [token_count[word] for word in chain]
        chain_score[no] = float (sum(length) * homogenity(sum(length), len(chain)))

    return chain_score
    
def find_segments_chain_member_cnts(data, lexical_chains):
    """
        Method to calculate number of seg in which 
        chain Member Occurs
        
        param: data, lexical_chains
        returns: segment chain count
    """
    seg_chain_member_cnt = defaultdict(int)
    data = data.split(".")
       
    for no, chain in lexical_chains.items():
        for word in chain:
            for segment in data:
                if word in segment:
                    seg_chain_member_cnt[word] += 1

    return seg_chain_member_cnt
    
def get_score(lexical_chains, segment, seg_chain_memb_cnts):
    """
        Method to get score for each segment to summarize data
        based on top lexical chains filtered by scores
        param: lexical_chains, segment, seg_chain_memb_cnts
        returns score
    """
    score = 0.0
    for no, chain in lexical_chains.items():
        for word in chain:
            if word in segment:
                word_occurences_in_segment = segment.count(word)
                score = score + (float(word_occurences_in_segment)/float(seg_chain_memb_cnts[word]))
    return score


def get_segment_scores(data, lexical_chain, seg_chain_memb_cnts):
    """
        Method to get all segments scores
        param: data, lexical_chain, seg_chain_memb_cnts
        returns segment_score
    """
  
    segment_score = []
    
    for segment in data.split("."):
        score = get_score(lexical_chain, segment, seg_chain_memb_cnts)
        segment_score.append((segment,score))
    return segment_score 


def main():
    argparser = argparse.ArgumentParser('''Lexical Chain - Text Summarization''')
    argparser.add_argument('filename')
    args = argparser.parse_args()
    
    # read data from file
    data = get_data(filename=args.filename)
    # data = get_data('/Users/ishujaswal/Downloads/new_30.txt')
    # get tokens
    tokens = get_tokens(data)
    token_count_bckup = Counter(tokens)
    token_count = Counter(tokens)
    
    # get nouns
    nouns = get_nouns(tokens)
    
    # create lexical chains
    lexical_chains = create_lexical_chains(nouns, token_count)
    
    print "\nLEXICAL CHAINS ARE: "
    print_lexical_chains(lexical_chains, token_count_bckup)
    
    # Text Summarization
    
    # finding chain scores
    chain_score = score_lexical_chains(lexical_chains, token_count_bckup)
    
    # get top lexical chains
    most_freq_chain_number = sorted(dict((k, v) for k, v in chain_score.items() if v > 0).items(), key=lambda(k,v): (v), reverse=True) # only chains which has score > 0
    top_lexical_chains = dict((k, lexical_chains[k]) for k, v in most_freq_chain_number) 
    print "\nTOP LEXICAL CHAINS"
    print top_lexical_chains
    
    # get segment chainmember counts
    seg_chain_memb_cnts = find_segments_chain_member_cnts(data, top_lexical_chains)

    # get segment score for summary
    seg_scores = get_segment_scores(data, top_lexical_chains, seg_chain_memb_cnts)
    seg_score_list = []
    number_segments = len(data.split('.'))
    
    for s in seg_scores:
        seg_score_list.append(s[1])
    seg_score_list.sort(reverse=True)

    score_threshold = seg_score_list[int(number_segments/3)]
    
    print "\nTEXT SUMMARY\n"
    # Print TEXT - SUMMARY
    for segment in seg_scores:
        if segment[1] >= score_threshold:
            print segment[0],

if __name__ == "__main__":
    main()

