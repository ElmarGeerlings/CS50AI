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
    # Create dictionary to store output in
    output = dict()
    
    # Pages that are linked from current page
    links = corpus.get(page)
    # Probability for a certain page in corpus to be linked to from current page
    if links:
        p_link = damping_factor / len(links)
    # Determine landing probability for every page
    for pages in corpus:
        # Probability to choose a random page out of all pages in the corpus
        p = (1 - damping_factor) / len(corpus)
        
        # Add probability to land on a page via a link from the current page
        if pages in links:
            p = p + p_link
        # Add page and landing probability to output dictionary
        output.update({pages: p})
    
    # Return probability distribution over which page to visit next     
    return output


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Create output dictionary with every page in corpus and initial PageRank value of 0
    output = dict()
    for pages in corpus:
        output.update({pages: 0})
    
    # Choose a random starting page and update PageRank value
    page = random.choice(list(corpus.keys()))  
    output.update({page: 1/n})
    
    # Sample further only if n > 1
    if n > 1:
        # Sample PageRank n-1 times
        for i in range(n-1):
            # Get probability distribution for current page
            p_dict = transition_model(corpus, page, damping_factor)
            
            # Create a list with every page and cumulative probability
            p_list = []
            sum_p = 0
            for key in p_dict:
                sum_p = sum_p + p_dict.get(key)
                p_list.append([key, sum_p])
            
            # Take a random number between 0 and 1
            rand = random.uniform(0,1)
          
            # Choose a random page based on the probability distribution
            for i in range(len(p_list)):
                if rand < p_list[i][1]:
                    page = p_list[i][0]
                    break
            
            # Update PageRank value for chosen page
            PR = output.get(page) + 1/n
            output.update({page: PR})
    
    # Return dictionary with pagenames and PageRank values   
    return output


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Create output dictionary with every page in corpus and initial PageRank value of 1/(number of pages)
    output = dict()
    for pages in corpus:
        p = 1 / len(corpus)
        output.update({pages: p})
        
    # Repeat until PageRank values do not change more than 0.001
    while True:
        # Initiate a variable to measure PageRank value change
        dif = 0
        # Update PageRank value for every page p in corpus
        for page in output:
            # PageRank value of current page p
            PR = output.get(page)
            # Intialise new PageRank value for page p as with the probability to land on the page at random
            PR_new = (1 - damping_factor) / len(corpus)
            # Calculate PageRank contribution from other pages i
            for otherpage in corpus:
                # PageRank value of page i
                PR_link = output.get(otherpage)
                # Number of links on page i
                NumLinks = len(corpus.get(otherpage))
                # If page i has no links, it is treated as having a link to every page
                if NumLinks == 0:
                    PR_new = PR_new + damping_factor * PR_link / len(corpus)    
                # Add Sum part of PageRank equation for every page i that links to page p
                elif page in corpus.get(otherpage):
                    # Add contribution of page i to the PageRank of page p, as per the PageRank formula
                    PR_new = PR_new + damping_factor * PR_link / NumLinks
            # Save new PageRank value in output dictionary
            output.update({page: PR_new})
            # Calculate the change in PageRank value and save this value if it's larger than for other pages
            newdif = abs(PR_new - PR)
            dif = max(dif, newdif)
        # Break if PageRank values do not change more than 0.001
        if dif < 0.001:
            break
    
    # Return dictionary with pagenames and PageRank values   
    return output


if __name__ == "__main__":
    main()
