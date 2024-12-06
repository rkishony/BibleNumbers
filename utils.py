def find_all_start_indices(text, query):
    start = 0
    while True:
        start = text.find(query, start)
        if start == -1:
            return
        yield start
        start += 1
