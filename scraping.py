# Data Extraction

import pandas as pd                                                   # importing for reading the file 
from bs4 import BeautifulSoup                                         # importing for data extraction
from tqdm import tqdm                                                 # importing tqdm for processing
import multiprocessing                                                # importing for multiprocessing the data 
import requests                                                       # importing for http protocols or interactions with webserver
import chardet                                                        # importing for knowing the encoding type of the text file 
import re                                                             # importing for removing uneccessary character in the text such as hyphens commas, 
import os                                                             # importing for setting file location
import nltk                                                           # importing nltk library
import nltk.data                                                      # going through data module  
from nltk.tokenize import word_tokenize,pos_tag                       # importing the word tokenizer 
from nltk.corpus import cmudict                        
from nltk.corpus import stopwords
tokenizer = nltk.data.load('tokenizers/punkt/PY3/english.pickle')     # loading the english pickle of words 


df = pd.read_excel('Input.xlsx')                                      # reading the file 
df.head()                                                             # head of the file


def collect_data(start,end):                                                       # function to data extraction
    for i in tqdm(df.values[start:end]):                                           # looping
        res      = requests.get(i[1])                                              # requesting for access the web
        soup     = BeautifulSoup(res.content,'html.parser')                        # parsing through the content
        try:
            # getting the title
            heading  = soup.title.text                                             
            # check the len of p
            if len(soup.find('div',class_ = 'td-post-content tagdiv-type').find_all('p')) > 10:  
                # feeding to content variable
                contents = ''.join([t.text for t in soup.find('div',class_ = 'td-post-content tagdiv-type').find_all('p')]) 
            else:         
                # combining the ul tags and paragraph tags together to the content
                contents = soup2.find('div',class_ = 'td-post-content tagdiv-type').find('p').text + soup2.find('div',class_ = 'td-post-content tagdiv-type').find('ul').text 
        except:
            # heading for exception 
            heading  = soup.title.text
            # loop through length of div class
            for j in range(len(soup.find_all('div',class_ = 'tdb-block-inner td-fix-index'))):
                # check if the val not empty
                if soup.find_all('div',class_ = 'tdb-block-inner td-fix-index')[j].find_all('p') != []: 
                    # feed to the content 
                    content = ''.join([t.text for t in soup.find_all('div',class_ = 'tdb-block-inner td-fix-index')[j].find_all('p')]) 
        # opening a folder called collection and writing the data onto the file 
        with open('Collections/'+str(i[0])+'.txt','w') as fd:                      
            fd.write(heading)                                                      # headers collected
            fd.write('\n')                                                         # spacing 
            fd.write(contents)                                                     # contents collected 
            fd.close()                                                             # closing the file


p1 = multiprocessing.Process(target = collect_data,args =(0,57))           # multiprocessing from 0 to 57 to the function
p2 = multiprocessing.Process(target = collect_data,args =(57,114))         # multiprocessing from 57 to 114 to the function
p1.start()                                                                 
p2.start()                                                                 
p1.join()
p2.join()


with open('MasterDictionary/positive-words.txt','r') as fd2:            # opening file of positive words 
    text = fd2.read()                                                   # reading the file 
    fd2.close()                                                         # closing the file

# opening file of negative words as in read binary file
with open('MasterDictionary/negative-words.txt', 'rb') as file:
    # using chardet library to check the encoding of the file 
    result = chardet.detect(file.read())                                 
    
# opening againg the file of negative words
with open('MasterDictionary/negative-words.txt', 'r', encoding=result['encoding']) as fd3:  
    ntext = fd3.read()                                                                     # reading it     
    fd3.close()                                                                            # closing it 

####################################################################################################################
###########################1.2.Creating a dictionary of Positive and Negative words#################################
####################################################################################################################

master_dict = {}                          # creating master dict

positive = []                             # empty positive list 
negative = []                             # empty negative list
for pos in text.split('\n'):              # loop through positive text
    positive.append(pos)                  # loading the value to positive list
for neg in ntext.split('\n'):             # loop through negative text
    negative.append(neg)                  # loading the value to negative list
    
master_dict['positive'] = positive        # loading positive list to master dict
master_dict['negative'] = negative        # loading negative list to master dict 


def text_analysis(start,stop):                                          # main function
    def count_cleaned_words(text):                                      # to count total number of words 
        cleaned_word_count = len(words)
        return cleaned_word_count

    def count_syllables(word):                                          # count the syllables in each words
        word = word.lower()
        if word.endswith("es") or word.endswith("ed"):                  # handling the exception word ending with 'ed' and 'es'
            return max(1, len(re.findall(r'[aeiouy]+', word)))          # using re module to return maximum count of vowels
        else:
            return len(re.findall(r'[aeiouy]+', word))                  # else return the len of word

    def count_syllables_in_text(text):
        words = re.findall(r'\b\w+\b', text)                                   # Tokenize the text into words
        syllable_counts = [count_syllables(word) for word in words]
        return syllable_counts

    def find_complex_words(text):
        # Tokenize the text into words and find complex words
        words = re.findall(r'\b\w+\b', text)                                   
        complex_words = [word for word in words if count_syllables(word) > 2]
        return complex_words

    # counting the total number of personal pronoun present in the paragraph or the data extracted
    def count_pp(para):
        personal_pronouns = ['I','we','you','he','she','it','they','my','mine','our','ours','your','yours','his','her',
                         'hers','its','their','theirs','myself','yourself','himself','herself','itself','ourselves',
                         'yourselves','themselves']
        ls = []
        for i in para.split(' '):
            if i in personal_pronouns:
                ls.append(i)
        return len(ls)
    
    # calculating the average word length of text or article 
    def calculate_average_word_length(text):
        words = text.split()
        total_char_count = sum(len(word) for word in words)
        total_word_count = len(words)

        if total_word_count == 0:
            return 0  # Avoid division by zero

        average_word_length = total_char_count / total_word_count
        return average_word_length
    
    data = []                                                             # creating empty data of list 
    for i in tqdm(df.values[start:stop]):                                 # going through the values   
        with open('Collections/' + str(i[0]) + '.txt','r') as fd:         # opening the text file 
            text = fd.read()                                              # reading the text file
        # cleaning the text by removing the stopwords
        custom_stopwords = set()
        for filename in os.listdir(stopwords_folder):                     # goinf through stopwords folder
            if filename.endswith(".txt"):                                 # if the file name ends with .txt
                # open the file 
                with open(os.path.join(stopwords _folder, filename), "r",encoding = result['encoding']) as file:
                    custom_stopwords.update(line.strip() for line in file) 

        words          = word_tokenize(text)                                              # Tokenize the paragraph into words
        filtered_words = [word for word in words if word.lower() not in custom_stopwords] # Remove stopwords
        # Join the filtered words to reconstruct the paragraph
        clean_para     = " ".join(filtered_words)                                         
        
    #####################################################################################################################
    ######################################1.3. Extracting Derived variables##############################################
    #####################################################################################################################
        # calculating the total number of sentences in the article
        tot_sent = len(tokenizer.tokenize(clean_para))                           
        sent = tokenizer.tokenize(clean_para)                                   # sentences in the file 
        word_pattern = r"[\w'+,-]+"                                             # word pattern 
        words = re.findall(word_pattern, clean_para)
        p = 0                                                                   # positive scoring 
        n = 0                                                                   # negative scoring 
        for words in text.split(' '):                                        
            if (words) in master_dict['positive']:                              # word present in positive list then +1 
                p += 1 
            elif (words) in master_dict['negative']:                            # else negative score +1
                n += 1
        polarity_score = round((p-n)/((p+n)+0.000001),3)                       
        subjective_score = round(((p + n)/((len(words))+0.000001)),3)          
        complex_words = len(find_complex_words(clean_para))
        
    #####################################################################################################################
    ##########################################2. Analysis of Readability#################################################
    #####################################################################################################################

        average_sentence_length = round(len(words) / tot_sent,3)                # average length of sentence 
        try:
            Per_Complex_words       = round((complex_words / len(words)*100),3) # percentage of complex word 
        except:  
            Per_Complex_words       = 0                                         # to handle zero division error
        fog_idx                 = round(0.4 * (average_sentence_length + Per_Complex_words),3) # fog index

    #####################################################################################################################
    #####################################3.Average Number of Words Per Sentence##########################################
    #####################################################################################################################

        average_word_length = round(len(words) / tot_sent,3)         # number of words per 

    #####################################################################################################################
    ##########################################4.complex Word count#######################################################
    #####################################################################################################################

        complex_words                                               # complex words
 
    #####################################################################################################################
    ###############################################5. Word count#########################################################
    #####################################################################################################################

        tot_word = count_cleaned_words(clean_para)                    # total words 
     
    #####################################################################################################################
    ##########################################6. Syllable Count Per Word#################################################
    #####################################################################################################################

        total_syllable = sum(count_syllables_in_text(text))         # total syllable in each words sum

    #####################################################################################################################
    ###########################################7. personal pronoun#######################################################
    #####################################################################################################################
        
        count_personal_pro = count_pp(text)                        # count of personal pronoun
         
    #####################################################################################################################
    ###########################################8.average word length#####################################################
    #####################################################################################################################
               
        average_length = round(calculate_average_word_length(text),3)     # average word length
            
    #####################################################################################################################
        
        data.append([i[0],i[1],p,n,polarity_score,subjective_score,average_sentence_length,Per_Complex_words,fog_idx,average_word_length,complex_words,tot_word,total_syllable,count_personal_pro,average_length])    # putting all the values calculated into the data list 
        # creating dataframe 
    final = pd.DataFrame(data,
                         columns= ['URL_ID','URL','POSITIVE SCORE','NEGATIVE SCORE','POLARITY SCORE',
                                   'SUBJECTIVITY SCORE','AVG SENTENCE LENGTH','PERCENTAGE OF COMPLEX WORDS',
                                   'FOG INDEX','AVG NUMBER OF WORDS PER SENTENCE','COMPLEX WORD COUNT','WORD COUNT',
                                   'SYLLABLE PER WORD','PERSONAL PRONOUNS','AVG WORD LENGTH'])    
    
    
    return final

output = text_analysis(0,114)                     # saving in output file
output.to_excel('Final.xlsx',index = False)       # saving to excel file