library(Hmisc)

setwd("/Users/agasharatam/Documents/yale/cpsc490/data/")
list <- read.csv('billboard-list.csv', stringsAsFactors = FALSE)
features <- read.csv('hot-100-features.csv', stringsAsFactors = FALSE)
combined <- read.csv('hot-combined.csv', stringsAsFactors = FALSE)
merged <- read.csv('billboard-merged.csv', stringsAsFactors = FALSE)

small <- subset(features, Performer == 'Gloria Estefan')

numWeeks <- max(combined$WeekNumber)
weeks <- 1:numWeeks
avg_tempo <- integer(numWeeks)
for (i in 1:numWeeks) {
  avg_tempo[i] <- mean(combined[(100*(i-1)+1):(100*i),]$Tempo, na.rm = TRUE)
}

plot(weeks, avg_tempo, 
     type = 'l')

for (i in 1:3257) {
  if (nrow(subset(combined, WeekNumber == i)) != 100) {
    print(i)
  }
}

trend <- read.csv('individual-trend.csv', stringsAsFactors = FALSE)
plot(trend$t, trend$value,
     type = 'l')


pred <- read.csv('small-test-pred.csv', header = FALSE)
length = 1000
plot(1:length, pred$V1[1:length])
plot(1:length, pred$V1[(length+1):(2*length)])
plot(1:(2*length), pred$V1)

averages <- read.csv('averages.csv')
plot(1:3206, averages$Tempo[1:3206], type = 'l',
     xlab = 'Week',
     ylab = 'Average Tempo (bpm)')

mariah <- subset(merged, SongID == 'All I Want For Christmas Is You')


