# Portal Analyitics

This repository is my attempt to perform some analysis on the merged raw data from the portals. My goal was to try and find some correlations between variables in the hope of creating some derived or automated annotations.

## To Do

- [ ] Develop decision tree model
- [ ] Implement [Hydra]() in project for experimentation
- [ ] Explore mutal information between features
  - [ ] Explore connection between file format and assay because assay might constrain what file formats are available
  - [ ] Connectino between assay and study
  - [ ] Connection between file name and resource type
  - [ ] Between Assay and datatype
  - [ ] resource type & datasubtype
Cleaning
- [ ] Replace acronyms with full spellings for more features

## Setup

1. Rename the `.env-template` -> `.env`
2. Update the `.env` file with your information.

## Data

`snowflakeData.csv` was taken from the `SAGE.PORTAL_RAW.PORTAL_MERGE` on October 31st, 2023.

### Cleaning

The data is pulled from Snowflake and dated when it was pulled. Any columns that are completley empty are removed from the dataset. The data was cleaned using `./cleaning.ipynb`. The major work was to clean up the names and differences in spellings for variables like assay. I used [Levenshtien distance](https://en.wikipedia.org/wiki/Levenshtein_distance#:~:text=Informally%2C%20the%20Levenshtein%20distance%20between,considered%20this%20distance%20in%201965.) to determine which spellings were similar. This is ongoing work as I work through the EDA part.

I pulled terms from [OLS4](https://www.ebi.ac.uk/ols4) as a cross reference for variables like assay types and file formats using `./ontologyScraper.py` in the hope of matching our annotations with a known 3rd party ontology source.

I also derived some file formats by splitting by ".". This causes the zip files to be a larger portion of the data so further cleanup to remove zip extensions to look at the underlying file types would be a good next step.

---

### EDA

*Proportions are only shown for values that have greater than 5% in the dataset.

#### File Formats

Most of the files are "BAM" or "gz".
| fileFormat   |   count |   proportion |
|:-------------|--------:|----------:|
| BAM          |   33143 |   10.10 |
| gz           |  133007 |   40.53   |

#### Study

<img src="./imgs/study-counts.jpg" alt="assay counts" width="500"/>

#### Assay

<img src="./imgs/assay-counts.jpg" alt="assay counts" width="500"/>

#### *Data Types*

<img src="./imgs/dataType-counts.jpg" alt="assay counts" width="500"/>

#### *Data Subtypes*

| dataSubtype   |   count |   proportion |
|:--------------|--------:|-------------:|
| raw           |  124908 |       67.072 |
| processed     |   51846 |       27.84  |

<img src="./imgs/dataSubtype-counts.jpg" alt="assay counts" width="500"/>

#### *Resource Types*

<img src="./imgs/resourceType-counts.jpg" alt="assay counts" width="500"/>

<br>

My initial EDA shows that the file formats vary across the assay types which seems a little odd to me. I think splitting up "RAW" vs. "Processed/Analysis" types would help differentiate which files are used in different processed.
![ATAC-seq file types](./imgs/file-format-ATAC-seq.png)

# References

[Snowflake Python SDK](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector)

- Programmatic access: [Link](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-api#label-account-format-info)
