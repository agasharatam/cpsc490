collection.py: 
  - Used for initial data collection
  - writes data/billboard-list.json: a compiled list of songs on the Billboard Hot 100
  - writes data/songs.json: a list of features for each SongID
  
combiner.py:
  - Merges data/billboard-list.json and data/songs.json
  - Writes data/billboard-merged.json: A 327,600-row file (100 x 3,276 weeks) with song features when available
  
dataset-writer-*:
  - Writes the dataset used for training and testing models used in this project

draw.py, plot.py:
  - Used for plotting

old/:
  - Folder with various outdated, no longer needed, or miscellaneous files.
  
jupyter/:
  - Contains .ipynb files used for actual training of NNs
  - Use online notebooks to use GPU, since it greatly accelerates NN training/testing.
  
analysis.R:
  - Used for easy access to CSV files
  

 
