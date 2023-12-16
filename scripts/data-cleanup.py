# # Goals
#
# Tag study, grant and dataType
#

# setup
import pandas as pd
import numpy as np
import re
from datetime import datetime
import sys
import os
import ontologyScraper as ont
import textcleaning as tc

# read in raw data from snowflake
df = pd.read_csv("../data/portal-data-raw-20231214.csv", low_memory=False, index_col=0)

# # potential features
df = df.loc[
    :,
    [
        "ID",
        "TABLE",
        "TYPE",
        "NAME",
        "STUDY",
        "ASSAY",
        "DATATYPE",
        "DATASUBTYPE",
        "RESOURCETYPE",
        "FILEFORMAT",
        "GRANTS",
        "PARENTID",
        "PROJECTID",
        "STUDYID",
        "PROJECT",
        "CONTRIBUTOR",
        "PI",
    ],
]


df.info()

# cols that are lists represented as strings.

list_cols = ["STUDY", "DATATYPE", "ASSAY", "GRANTS"]
for l in list_cols:
    try:
        df[l] = df[l].str.replace('\n|\[|\]|"', "", regex=True).str.strip()
    except Exception as e:
        print(e)

# fill in empty cells with nan's
df = df.replace("", np.nan)
df = df.replace("undefined", np.nan)
df = df.replace("\t", " ", regex=False)

df.sample(20)

# # EDA
#

import seaborn as sns
import matplotlib.pyplot as plt

# unique values by column
unique_counts = df[list_cols].fillna("").apply(lambda x: len(np.unique(x)))
unique_counts = (
    pd.DataFrame(unique_counts)
    .reset_index()
    .rename(columns={"index": "Attr", 0: "Count"})
)
sns.barplot(
    unique_counts.sort_values("Count", ascending=False), x="Attr", y="Count"
).set(title="Unique Values by Column")

sns.despine()

# similar labels
assay_counts = (
    pd.DataFrame(df["ASSAY"].value_counts())
    .reset_index()
    .rename(columns={"index": "ASSAY", "ASSAY": "count"})
)

g = sns.barplot(x="ASSAY", y="count", data=assay_counts.loc[:10, :])

g.set_xticklabels(g.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

sns.despine()

plt.show()

# Missing annotations

# # Cleanup Attributes
#

# get spelling from public ontology source for assay
# vv_assay = ont.purl_main(
#     "http://purl.obolibrary.org/obo/OBI_0000070")
# vv_assay = pd.Series(vv_assay)
# vv_assay.to_csv('./data/valid_values_assay.csv')

vv_assay = (
    pd.read_csv("../data/valid_values_assay.csv")
    .drop(columns="Unnamed: 0")
    .rename(columns={"0": "values"})
)

vv_assay["values"] = vv_assay["values"].replace("assay", "", regex=True)

# manually recode
assay_recoder = {
    "(?i)3D\s*Confocal\s*Imaging": "3D confocal imaging",
    "(?i)active\s*avoidance\s*learning\s*behavior": "active avoidance learning behavior",
    "(?i)ATAC-*seq": "ATAC-seq",
    "(?i)(err)?bisulfite\s*seq(uencing)?": "bisulfite sequencing",
    "(?i)Blood\s*Chemistry\s*Measurement": "blood chemistry measurement",
    "cell\s*proliferation": "cell proliferation",
    "(?i)ChIP-*Seq": "ChIP-seq",
    "contextual\s*conditioning\s*behavior": "contextual conditioning behavior",
    "(?i)electrophysiology": "electrophysiology",
    "exomeSeq": "whole exome sequencing",
    "(?i)flow\s*cytometry": "flow cytometry",
    "(?i)Genotyping": "genotyping",
    "(?i)Immunoprecipitation": "immunoprecipitation",
    "liquid\s*chromatography/tandem\s*mass\s*spectrometry": "liquid chromatography-tandem mass spectrometry",
    "liquidchromatography/tandemmassspectrometry": "liquid chromatography-tandem mass spectrometry",
    "localfieldpotentialrecording": "local field potential recording",
    "(?i)mass\s*spectrometry": "mass spectrometry",
    "(?i)methylationArray": "methylation array",
    "microscopy": "microscopy",
    "novelty\s*response\s*behavior": "novelty response behavior",
    "photography": "photograph",
    "(?i)polymerase\s*chain\s*reaction": "polymerase chain reaction",
    "(?i)Positron\s*Emission\s*Tomography": "positron emission tomography imaging",
    "(?i)positronemissiontomography": "positron emission tomography imaging",
    "(?i)proximityextensionassay": "proximity extension",
    "HI-C": "Hi-C",
    "(?i)RNA-*\s*seq": "RNA-seq",
    "(?i)rnaArray": "RNA array",
    "(?i)scATAC-*seq\s*(assay)?": "single-cell ATAC-seq",
    "(?i)scRNA-*seq\s*assay": "single-cell RNA-seq",
    "scwholeGenomeSeq": "single-cell whole genome sequencing",
    "sorbitoldehydrogenaseactivitylevelassay": "sorbitol dehydrogenase activity level",
    "(?i)single-*cell\s*RNA-seq\s*(assay)?": "single-cell RNA-seq",
    "(?i)snATAC-*seq\s*(assay)?": "single-nucleus ATAC-seq",
    "(?i)snRNA-?seq assay": "single-nucleus RNA-seq",
    "(?i)snpArray": "SNParray",
    "(?i)T\s*cell\s*receptor\s*repertoire\s*sequencing": "T cell receptor repertoire sequencing",
    "(?i)TMT\s*quantitation": "TMT quantitation",
    "TMT\s*quantification": "TMT quantitation",
    "(?i)western\s*blot": "western blot",
    "(?i)Whole\s*Exome\s*Seq(uencing)?": "whole exome sequencing",
    "(?i)whole\s*genome\s*seq(uencing)?": "whole genome sequencing",
    "whole-cell\s*patch\s*clamp": "whole-cell patch clamp",
}

# for reordering if necessary
k = assay_recoder.keys()
k = sorted(k, key=str.casefold)
for ki in k:
    print('"' + ki + '"' + ":" + '"' + assay_recoder[ki] + '"' + ",")

df = df.replace("\t", " ", regex=True)

# fuzzy matching to self
col_recode = "ASSAY"

# A good cut off is 95, otherwise similar but not exact matches arise like whole exome sequencing versus whome genome sequencing
df[col_recode] = df[col_recode].replace(assay_recoder, regex=True)
df[col_recode] = df[col_recode].replace("assay", "", regex=True)

results = tc.fuzzy_matcher(df[col_recode], df[col_recode].fillna("").unique(), 90)

results["antCount"] = results["Annotation"].apply(
    lambda x: len(df[df[col_recode] == x])
)

with pd.option_context("display.max_rows", None):
    display(results)

# take the annotation with the best score match
idx = results.groupby("Annotation")["Score"].idxmax()

max_scores = (
    results.loc[idx]
    .sort_values(
        by=["Annotation", "Score"],
        key=lambda x: x.str.lower() if pd.api.types.is_string_dtype(x.dtype) else x,
    )
    .reset_index(drop=True)
)

# Works for most but not for example "whole exome sequencing" which matches to "whole genome sequencing assay" instead of "exome sequencing assay"

for k, v in assay_recoder.items():
    max_scores.loc[max_scores["Annotation"] == k, "ontologyWord"] = v

# max_scores

# fuzzy matching to ontology
col_recode = "ASSAY"

# A good cut off is 95, otherwise similar but not exact matches arise
results = tc.fuzzy_matcher(df[col_recode], vv_assay["values"], 90)
results["antCount"] = results["Annotation"].apply(
    lambda x: len(df[df[col_recode] == x])
)

with pd.option_context("display.max_rows", None):
    display(results)

sorted(df["ASSAY"].dropna().unique(), key=str.casefold)

# similar labels
assay_counts = (
    pd.DataFrame(df["ASSAY"].value_counts())
    .reset_index()
    .rename(columns={"index": "ASSAY", "ASSAY": "count"})
)

g = sns.barplot(x="ASSAY", y="count", data=assay_counts.loc[:10, :])

g.set_xticklabels(g.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

plt.show()

assay_counts.iloc[:20, :]

# Fix studies
#

DATATYPE_recoder = {"Analysis": "analysis", "Volume": "volume"}

# fix data type
sorted(df["DATATYPE"].fillna("").unique(), key=str.casefold)

df["DATATYPE"] = df["DATATYPE"].replace(DATATYPE_recoder)

# fix resourceType
fix_col = "RESOURCETYPE"

recoder = {"ExperimentalData": "experimentalData", " tool": "tool"}

# fix col type
sorted(df[fix_col].fillna("").unique(), key=str.casefold)

df[fix_col] = df[fix_col].replace(recoder)

# fix resourceType
fix_col = "DATASUBTYPE"

recoder = {"ExperimentalData": "experimentalData", " tool": "tool"}

# fix data type
sorted(df[fix_col].fillna("").unique(), key=str.casefold)

# df[fix_col] = df[fix_col].replace(recoder)

# fix resourceType
fix_col = "FILEFORMAT"

recoder = {
    "(?i)bash\s*script": "sh",
    "R script": "R",
    "(?i)synapse\s*Table": "SynapseTable",
    "(?i)Python\s*script": "py",
    "Fastq": "fastq",
    "(?i)powerpoint": "ppt",
    "(?i)RData": "Rdata",
}

df[fix_col] = df[fix_col].replace(recoder, regex=True)

# fix data type
print(sorted(df[fix_col].fillna("").unique(), key=str.casefold))

df["FILEFORMAT"] = df["FILEFORMAT"].replace("", np.nan).str.lower()

# file formats
# file_formats = ont.purl_main('http://edamontology.org/format_1915')
# pd.Series(file_formats).to_csv('./data/file-formats.csv', index = False)
file_formats = pd.read_csv("../data/file-formats.csv").rename(columns={"0": "values"})

file_formats["values"] = file_formats["values"].str.replace("format", "")
# get as an array
file_formats = list(file_formats["values"].values)

new_terms = [
    "txt",
    "mzXML",
    "mds",
    "sf3",
    "tbz",
    "drv",
    "crai",
    "dbm",
    "svs",
    "svg",
    "tmp",
    "unr",
    "gmt",
    "R",
    "Rmd",
    "Rdata",
    "fam",
    "gz",
    "h5",
    "hdr",
    "img",
    "tgz",
    "XSL",
    "XLS",
    "zip",
    "seq",
    "rtf",
    "sh",
    "doc",
    "bgz",
    "bib",
    "ipynb",
    "py",
    "xlsb",
    "qc",
]

file_formats += new_terms + list(df["FILEFORMAT"].dropna().values)

file_formats = sorted(np.unique(file_formats), key=lambda x: x.lower())

file_formats

df["FILEFORMAT"].unique()

np.sum(df["FILEFORMAT"].isna())

df["ISZIPPED"] = df["NAME"].str.contains("gz|zip|gzip", na=False, regex=True)

df[df["ISZIPPED"]]

temp = (
    df.loc[df["FILEFORMAT"].isna(), "NAME"]
    .str.replace(r".gz", "", regex=False)
    .str.rsplit(r".", 1, expand=True)
)

print(f"Before: {np.sum(df['FILEFORMAT'].isna())}")

df["FILEFORMAT"] = df["FILEFORMAT"].fillna(
    temp.loc[temp[1].str.lower().isin([f.lower() for f in file_formats])][1]
)

print(f"After: {np.sum(df['FILEFORMAT'].isna())}")

sorted(df["FILEFORMAT"].dropna().unique(), key=lambda x: x.lower())

np.sum(df["FILEFORMAT"].isna())

with pd.option_context("display.max_colwidth", None):
    display(
        df.loc[
            df["FILEFORMAT"].isna(), ["ID", "NAME", "TYPE", "FILEFORMAT", "ISZIPPED"]
        ]
    )

# # cleanup "types"
#

df.loc[
    df["NAME"].str.contains("Dictionary", flags=re.IGNORECASE, na=False), "METADATATYPE"
] = "dataDictionary"

df.loc[
    (df["NAME"].str.contains("metadata", flags=re.IGNORECASE, na=False))
    & (df["RESOURCETYPE"].isnull())
    & (~df["FILEFORMAT"].isin(["py", "ipynb"])),
    "RESOURCETYPE",
] = "metadata"

df.loc[
    (df["NAME"].str.contains("metadata", flags=re.IGNORECASE, na=False))
    & (df["RESOURCETYPE"].isnull()),
]

df.loc[df["DATASUBTYPE"].isnull(),]

# ASSUMING ALL ROWS ARE FILES
df.loc[(~df["FILEFORMAT"].isnull()) & (df["TYPE"].isnull()), "TYPE"] = "file"

df.loc[df["TYPE"].isnull()]

df.to_csv(f"../data/cleaned-data-{datetime.now().strftime('%Y%m%d')}.csv", index=False)
