from linkfinder.linkfinder.link_finder import preprocess_docs
from linkfinder.linkfinder.link_finder import strong_similarities_and_appropriate_links_thresh
from linkfinder.linkfinder.link_finder import perform_queries_and_get_links
from linkfinder.linkfinder.link_finder import find_links_between_in

import copy

def order_comments(comments):
    comments.reverse()

def join_all_comments_paragraphs(comments):
    for comment in comments:
        if comment['content'].__class__ == list:
            comment['content'] = " \n ".join(comment['content'])

def text_list_into_sentences_dict_and_list(text, start_id):
    import nltk.data
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

    dicts = []
    sentences = []

    if text.__class__ == list:
        for i, t in enumerate(text):
            for s in sent_detector.tokenize(t):
                new = {
                    'text': s,
                    'comment': i
                }
                dicts.append(new)
                sentences.append(s)
    else:
        for s in sent_detector.tokenize(text):
                new = {
                    'text': s,
                    'comment': -1
                }
                dicts.append(new)
                sentences.append(s)
    return dicts, sentences

def article_body_into_sentences_dict_and_list(article_body):
    joined_body = " \n ".join(article_body)
    dicts, sentences = text_list_into_sentences_dict_and_list(joined_body,
                                                             0)
    return dicts, sentences

def comments_to_sentences_dict_and_list(comments, start_id):
    join_all_comments_paragraphs(comments)
    paragraphs = [c['content'] for c in comments]
    dicts, sentences = text_list_into_sentences_dict_and_list(paragraphs,
                                                             start_id)
    return dicts, sentences

def split_into_sentences(article_dict):
    import copy

    a_dicts, a_sents = article_body_into_sentences_dict_and_list(
        article_dict['body']
    )
    start_comment_id = len(a_sents)
    c_dicts, c_sents = comments_to_sentences_dict_and_list(
        article_dict['comments'],
        start_comment_id
    )

    all_dicts = copy.deepcopy(a_dicts)
    all_sentences = copy.deepcopy(a_sents)
    all_dicts.extend(copy.deepcopy(c_dicts))
    all_sentences.extend(copy.deepcopy(c_sents))

    article_dict['comment_sentences'] = c_sents
    article_dict['article_sentences'] = a_sents
    article_dict['all_sentences'] = all_sentences
    article_dict['all_sentences_dicts'] = all_dicts

def preprocess_article(article_dict):
    order_comments(article_dict['comments'])
    split_into_sentences(article_dict)

def classify_links(s_dict, all_sentences, comment_start_index):
    '''
    Receive a similarity links structure in the form of
    {
    comment_sentence_no: [(list of tuples with sentence id,
                        and percentage)]
    }

    comment_start_index has the offset to add to the comment
    sentence number to change it into an id.

    It changes the list of links into an array, with the:
    [sentence_id, percentage, "type of link"]


    '''
    for comment_no, link_list in s_dict.iteritems():
        comment_sentence_id = comment_no + comment_start_index
        classified_links = []
        for l in link_list:
            # category = classify(all_sentences[comment_sentence_id],
            #           all_sentences[l[0]])
            category = 'stub'
            classified_links.append((l[0], l[1].item(), category))
        s_dict[comment_no] = classified_links

def summarize(article_dict):
    preprocess_article(article_dict)
    summary = copy.deepcopy(article_dict)
    del summary['body']

    docs = summary['all_sentences']
    comments = summary['comment_sentences']

    # note that the dictionary doesn't have the sentence id, but the
    # comment sentence number as key. So you have to add
    # len(summary['article_sentences']) to the key, to get the
    # comment sentence id.
    similarity_dict = find_links_between_in(docs, comments)
    summary['links'] = similarity_dict

    classify_links(summary['links'],
                   summary['all_sentences'],
                   len(summary['article_sentences']))

    return summary

