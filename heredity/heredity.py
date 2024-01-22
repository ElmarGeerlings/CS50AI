import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # Initialise joint probability
    p = 1
    # Loop over every person
    for person in people:
        # Calculate conditional probability for genes, if the parents are in people dictionary
        if people[person]["mother"] and people[person]["father"]:
            mother = people[person]["mother"]
            father = people[person]["father"]
            
            # Calculate possibility pm for mother to pass on a gene
            if mother in one_gene:
                pm = 0.5
            elif mother in two_genes:
                pm = 0.99
            else:
                pm = 0.01
            
            # Calculate possibility pf for father to pass on a gene
            if father in one_gene:
                pf = 0.5
            elif father in two_genes:
                pf = 0.99
            else:
                pf = 0.01
            
            # Calculate probability for person to have one copy of the gene
            if person in one_gene:
                p = p * (pf * (1 - pm) + pm * (1 - pf))
                gene = 1
            # Calculate probability for person to have two copies of the gene
            elif person in two_genes:
                p = p * (pf * pm)
                gene = 2
            # Calculate probability for person to not have the gene
            else:
                p = p * ((1 - pf) * (1 - pm))
                gene = 0
        
        # Calculate unconditional probability for genes, if the parents are not in people dictionary
        else:
            # Calculate probability for person to have one copy of the gene
            if person in one_gene:
                p = p * PROBS["gene"][1]
                gene = 1
            # Calculate probability for person to have two copies of the gene
            elif person in two_genes:
                p = p * PROBS["gene"][2]
                gene = 2
            # Calculate probability for person to not have the gene
            else:
                p = p * PROBS["gene"][0]
                gene = 0
            
        # Calculate probability for person to have the trait based on number of genes
        if person in have_trait:
            p = p * PROBS["trait"][gene][True]
        # Calculate probability for person to not have the trait based on number of genes
        else:
            p = p * PROBS["trait"][gene][False]
            
    # Return joint probability
    return p


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    # Update probability for every person in probabilities
    for person in probabilities:
        
        genes = probabilities[person]["gene"]
        # Update probability for having one copy of the gene
        if person in one_gene:
            p_new = genes[1] + p
            genes.update({1: p_new})
        # Update probability for having two copies of the gene
        elif person in two_genes:
            p_new = genes[2] + p
            genes.update({2: p_new})
        # Update probability for not having the gene
        else:
            p_new = genes[0] + p
            genes.update({0: p_new})
        
        traits = probabilities[person]["trait"]
        # Update probability for having the trait
        if person in have_trait:
            p_new = traits[True] + p
            traits.update({True: p_new})
        # Update probability for not having the trait
        else:
            p_new = traits[False] + p
            traits.update({False: p_new})


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # Normalize probability for every person in probabilities
    for person in probabilities:
        genes = probabilities[person]["gene"]
        # Calculate the sum psum of all probabilities in gene
        psum = genes[0] + genes[1] + genes[2]
        # Update with normalized probability pnorm by dividing p by psum 
        for i in genes:
            pnorm = genes[i] / psum
            genes.update({i: pnorm})
        
        traits = probabilities[person]["trait"]
        # Calculate the sum psum of all probabilities in trait
        psum = traits[True] + traits[False]
        # Update with normalized probability pnorm by dividing p by psum         
        for i in traits:
            pnorm = traits[i] / psum
            traits.update({i: pnorm})
            

if __name__ == "__main__":
    main()
