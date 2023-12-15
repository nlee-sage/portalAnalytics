# apply fuzzy matching to find misspellings

from thefuzz import fuzz
import numpy as np
import pandas as pd
import string


def find_score_duplicates(score_df):
    for i in range(len(score_df)):
        try:  # indexes might get dropped during the process.
            temp = score_df.loc[i, ["Annotation", "ontologyWord"]].values
            indexes = score_df.loc[
                (score_df["Annotation"] == temp[1])
                & (score_df["ontologyWord"] == temp[0])
            ].index

            score_df = score_df.drop(index=indexes)
        except:
            pass

    return score_df.reset_index(drop=True)


def fuzzy_matcher(ar, reference_ar, target_score=90):
    """find strings that have similar scores

    Args:
        ar (array): array of string values
        reference_ar (array): array of values to compare ar values against
        target_score (int): score out of 100 to return values

    Returns:
        dataframe: data frame of scores for word matchings
    """

    # unique values in array
    vv = np.unique(ar.fillna(""))

    scores = []

    for v in vv:
        # process term. Remove all punctuation to compare just the character values
        v_temp = v.translate(str.maketrans("", "", string.punctuation)).lower()

        v_search = "|".join(v_temp.split(" "))

        # limit results to reduce comparisions since most will not be a match
        # filtered_vv = reference_ar[reference_ar.str.contains(v_search, case=False)]

        for v2 in reference_ar:
            if v == v2:  # if the two values are the exact same spelling skip
                continue
            else:
                v2_temp = (
                    v2.translate(str.maketrans("", "", string.punctuation))
                    .lower()
                    .strip("assay")
                )  # assay has been common in all the ontology words under assay

                score = fuzz.ratio(
                    v_temp, v2_temp
                )  # remove any sort of spelling and see if they are similar
                if score >= target_score:
                    scores.append(
                        [{"Annotation": v, "ontologyWord": v2, "Score": score}]
                    )

    # convert scores to dataframe
    df = (
        pd.concat([pd.DataFrame(s) for s in scores])
        .sort_values(
            by=["Annotation", "Score"],
            key=lambda x: x.str.lower() if pd.api.types.is_string_dtype(x.dtype) else x,
        )
        .reset_index(drop=True)
    )

    df = find_score_duplicates(df)

    # errors
    # - ValueError: No objects to concatenate

    return df
