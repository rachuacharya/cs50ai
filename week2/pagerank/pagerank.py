import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    all_pages = list(corpus.keys())
    links = corpus[page]
    num_links = len(links)
    num_pages = len(all_pages)

    transition_prob = dict()

    constant_prob = round((1 - damping_factor) / num_pages, 4)

    linked_prob = round(constant_prob + damping_factor / num_links, 4)

    for apage in all_pages:
        if apage in links:
            transition_prob[apage] = linked_prob
        else:
            transition_prob[apage] = constant_prob
    
    return transition_prob





def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    all_pages = list(corpus.keys())

    # Initialize an empty list for sample pages
    samples = []

    # Choose at random the starting pages
    current_page = random.choice(all_pages)

    # Append the first page to samples
    samples.append(current_page)

    # Generate samples until number of sample = n    
    while(len(samples) <= n ):
        # Get probability distribution for current_page
        distribution_dict = transition_model(corpus, current_page, damping_factor)
        distribution = list(distribution_dict.values())

        # Choose  another sample based on the given distribution
        current_page = random.choices(all_pages, distribution)[0]
        samples.append(current_page)
    
    page_rank = dict()
    print(samples.count("bfs.html"))
    for page in all_pages:
        page_rank[page] = round(samples.count(page) / n, 3)
    
    return page_rank




def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    incoming_links = dict()
    all_pages = corpus.keys()
   
    for page in all_pages:
        incoming = set()
        for other_page in all_pages:
            if page != other_page:
                if page in corpus[other_page]:
                    incoming.add(other_page)
        incoming_links[page] = incoming
    
    constant = round(1 / len(all_pages), 4)

    # Starting page rank
    pagerank = {page:constant for page in all_pages}

    # lets break down PR(p) = X + d * Y
    # X = (1-d)/ N and Y = sum(PR(i)/num_links)

    X = round((1-damping_factor)/len(all_pages), 4)

    # Start while loop here 
    while(True):
        new_pagerank = dict()

        for page in all_pages:
            Y = 0
            for incoming in incoming_links[page]:
                num_links = len(corpus[incoming])
                Y += pagerank[incoming] / num_links
            
            # print(page, Y)
            
            new_pagerank[page] = X + damping_factor * Y

        old_ranks = pagerank.values()
        new_ranks = new_pagerank.values()

        diff = min(abs(i -j) for i, j in zip(old_ranks, new_ranks))

        if diff < 0.0001:
            return new_pagerank
            break 

        pagerank = new_pagerank

if __name__ == "__main__":
    main()
