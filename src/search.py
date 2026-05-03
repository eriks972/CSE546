from src.crypto import prf
from src.crypto import keyword_counters
from src.crypto import decrypt_posting_list

def search(keyword, index, key, mode="normal"):

    if mode == "forward_private":
        results = []

        for i in range(1, keyword_counters[keyword] + 1):
            trapdoor = prf(key, f"{keyword}_{i}")
            if trapdoor in index:
                posting = decrypt_posting_list(key, index[trapdoor])
                results.extend(posting)

        return list(set(results))

    else:
        trapdoor = prf(key, keyword)

        if trapdoor not in index:
            return []

        return decrypt_posting_list(key, index[trapdoor])