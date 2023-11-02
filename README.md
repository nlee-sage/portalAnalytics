# Portal Analyitics

This repository is my attempt to perform some analysis on the merged raw data from the portals. My goal was to try and find some correlations between variables in the hope of creating some derived or automated annotations.

## Data

`snowflakeData.csv` was taken from the `SAGE.PORTAL_RAW.PORTAL_MERGE` on October 31st, 2023.

### Cleaning

The data was cleaned using `./cleaning.ipynb`. The major work was to clean up the names and differences in spellings for variables like assay. This is ongoing work as I work through the EDA part.

I pulled terms from [OLS4](https://www.ebi.ac.uk/ols4) as a cross reference for variables like assay types and file formats using `./ontologyScraper.py` in the hope of matching our annotations with a known 3rd party ontology source.

I also derived some file formats by splitting by ".". This causes the zip files to be a larger portion of the data so further cleanup to remove zip extensions to look at the underlying file types would be a good next step.

### EDA

My initial EDA shows that the file formats vary across the assay types which seems a little odd to me. I think splitting up "RAW" vs. "Processed/Analysis" types would help differentiate which files are used in different processed.
![ATAC-seq file types](./imgs/file-format-ATAC-seq.png)

#### File Formats

Most of the files are "BAM" or "gz".
| fileFormat   |   count |   proportion |
|:-------------|--------:|----------:|
| BAM          |   33143 |   10.0994 |
| gz           |  133007 |   40.53   |

#### Assay

*Counts*  
<img src="./imgs/assay-counts.jpg" alt="assay counts" width="500"/>

*Proportion*

| assay                         |   count |   proportion |
|:------------------------------|--------:|----------:|
| RNA-seq assay                 |  142883 |    43.539 |
| whole genome sequencing assay |   65646 |    20.004 |
| methylation array             |   23599 |     7.191 |
| ChIP-seq assay                |   18288 |     5.573 |
