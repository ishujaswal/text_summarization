# text_summarization
Automated Text Summarization of text


A program that takes a text file as input and outputs the set of lexical chains in the text.

1. Creates lexical chains based on the lexical relationships of synonymy, antonymy, and one level of hyper/hyponymy. In other words, if a noun is related by one of these relationships to an existing lexical chain, it should be added to it, otherwise it should start a new chain.

Output is in the form:

Chain 1: girl(2), woman(1), women(3), person(1), she(4)
Chain 2: hat(2), skirt(1), pants(2), clothes(1), shirt(2)
...
Each chain lists the words it contains, with the number of word occurrences in parentheses.

2. Evaluates the results (qualitatively).
3. Uses the lexical chains to automatically create a summary of the input article.
