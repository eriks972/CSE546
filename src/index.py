from collections import defaultdict
import token

from torch import mode
from src.tokenize import tokenize
from src.crypto import prf, prf_forward_private
from src.crypto import encrypt_posting_list, decrypt_posting_list
from src.crypto import prf, keyword_counters

def build_index(documents, key, mode="normal", remove_stopwords=False):

    temp_index = defaultdict(list)
    prf_cache = {}
    counter_map = defaultdict(int)

    for doc_id, text in documents.items():

        tokens = tokenize(text, remove_stopwords=remove_stopwords)

        # ⚠️ DO NOT convert to set — we want frequency!
        # tokens = set(tokens)  # ❌ REMOVE if you had this

        for token in tokens:

            if mode == "forward_private":
                counter_map[token] += 1
                trapdoor = prf(key, f"{token}_{counter_map[token]}")
            else:
                if token not in prf_cache:
                    prf_cache[token] = prf(key, token)
                trapdoor = prf_cache[token]

            # ✅ FIX: ALWAYS append (preserve frequency signal)
            temp_index[trapdoor].append(doc_id)

    # Encrypt posting lists
    encrypted_index = {}

    for trapdoor, posting_list in temp_index.items():
        encrypted_index[trapdoor] = encrypt_posting_list(key, posting_list)

    return encrypted_index

def add_document(doc_id, text, index, key):
    """
    Dynamically insert a document into the encrypted index
    """

    tokens = tokenize(text)

    for token in tokens:

        trapdoor = prf(key, token)

        # retrieve encrypted posting list
        encrypted_posting = index.get(trapdoor)

        if encrypted_posting:
            posting_list = decrypt_posting_list(key, encrypted_posting)
        else:
            posting_list = []

        # add document ID
        if doc_id not in posting_list:
            posting_list.append(doc_id)

        # re-encrypt updated posting list
        index[trapdoor] = encrypt_posting_list(key, posting_list)