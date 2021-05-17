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
    joint_prob = 1

    for person in people:
        person_gene = 1 *(person in one_gene) + 2 * (person in two_genes)
        has = person in have_trait

        father = people[person]["father"]
        mother = people[person]["mother"]

        # If parents not in the list
        if mother is None:
            trait_prob = PROBS["gene"][person_gene] * PROBS["trait"][person_gene][has]
        
        # if parents in the list
        else:
            mother_gene = 1 * (mother in one_gene) + 2 * (mother in two_genes)
            father_gene = 1 * (father in one_gene) + 2 * (father in two_genes)
        
            # Calculating person's gene probability based on the mother and father genes
            mutation = PROBS["mutation"]
            no_mutation = 1 - PROBS["mutation"]

            # Probabilities for 0 gene pair 
            if person_gene == 0:

                # (0, 0) leads to 0 if no mutation takes place
                if mother_gene == 0 and father_gene == 0:
                    gene_prob = no_mutation * no_mutation
               # 1 leads to 0 50% of time and when 0 undergoes no mutation
                elif (mother_gene == 0 and father_gene == 1) or (mother_gene== 1 and father_gene == 0):
                    gene_prob = 0.5 * no_mutation
               # (0, 2) or (2, 0) leads to zero only when 2 pair gene undergoes mutation 
                elif (mother_gene == 0 and father_gene == 2) or (mother_gene == 2 and father_gene== 0):
                    gene_prob = no_mutation * mutation
               # (1, 1) each gene leads to 0 with half a probability 
                elif (mother_gene == 1 and father_gene == 1):
                    gene_prob = 0.5 * 0.5 
                # For (0,2 ) or (2, 0) 2 needs to undergo mutation
                elif (mother_gene == 1 and father_gene == 2) or (mother_gene == 2 and father_gene == 1):
                    gene_prob = 0.5 * mutation
                # (2, 2) both pair should undergo mutation
                elif (mother_gene == 2 and father_gene == 2):
                    gene_prob = mutation * mutation

            if person_gene == 1:
                # (0, 0) and (2, 2) one  gene in the both gene pair needs mutation
                if (mother_gene == 0 and father_gene == 0) or (mother_gene == 2 and father_gene == 2):
                    gene_prob = mutation * no_mutation 
                # (0, 2) and (2, 0) : Either both undergo mutation or neither does 
                elif (mother_gene == 0 and father_gene == 2) or (mother_gene == 2 and father_gene==0):
                    gene_prob = no_mutation * no_mutation + mutation * mutation
                # (1, 1) leds to 1 50% if the time
                elif (mother_gene == 1 and father_gene == 1):
                    gene_prob =  2* 0.5  * 0.5
                #(0, 1), (1, 0), (2, 1), (1, 2)
                else:
                    gene_prob = no_mutation * 0.5 + mutation * 0.5

            if person_gene == 2:
                # (0, 0)
                if mother_gene == 0 and father_gene == 0:
                    gene_prob = mutation * mutation
                # (0, 1)
                elif (mother_gene == 0 and father_gene == 1) or (father_gene == 0 and mother_gene == 1):
                    gene_prob = 0.5 * mutation
                # (0, 2)and (2, 0)
                elif (mother_gene == 0 and father_gene == 2) or (father_gene == 0 and mother_gene==2):
                    gene_prob = mutation * no_mutation
                # (1, 1)
                elif (mother_gene == 1 and father_gene == 1):
                    gene_prob = 0.5  * 0.5
                # (1, 2) and (2, 1)
                elif (mother_gene == 1 and father_gene == 2) or (father_gene == 1 and mother_gene == 2):
                    gene_prob = 0.5 * no_mutation
                # (2, 2)
                elif(mother_gene ==2 and father_gene == 2):
                    gene_prob = no_mutation * no_mutation
            
            # Probabiliity of having or not having the trait given gene probability
            trait_prob = gene_prob * PROBS["trait"][person_gene][has]

        joint_prob *= trait_prob
    
    return joint_prob



def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        person_gene = 1 * (person in one_gene) + 2 * (person in two_genes)
        has = person in have_trait

        # Sum of probabilities of all scenario
        probabilities[person]["gene"][person_gene] += p
        probabilities[person]["trait"][has] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        gene_sum = 0
        for i in range(0, 3):
            gene_sum += probabilities[person]["gene"][i]
        
        trait_sum = probabilities[person]["trait"][True] + probabilities[person]["trait"][False]
        
        for i in range(0, 3):
            probabilities[person]["gene"][i] /= gene_sum
        
        probabilities[person]["trait"][True] /= trait_sum
        probabilities[person]["trait"][False] /= trait_sum

if __name__ == "__main__":
    main()
