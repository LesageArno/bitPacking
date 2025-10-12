library(dplyr)
library(ggplot2)


#### Import data ####
classifierList <- list()
classifierList[["NoSplit"]] <- read.csv("OUT\\nosplitBenchmark.out", stringsAsFactors = TRUE, strip.white = TRUE) %>% select(-benchID) %>% mutate(source = as.factor("NoSplit"))
classifierList[["Split"]] <- read.csv("OUT\\splitBenchmark.out", stringsAsFactors = TRUE, strip.white = TRUE) %>% select(-benchID) %>% mutate(source = as.factor("Split"))
classifierList[["O1"]] <- read.csv("OUT\\overflow1Benchmark.out", stringsAsFactors = TRUE, strip.white = TRUE) %>% select(-benchID) %>% mutate(source = as.factor("Overflow1"))
classifierList[["O2"]] <- read.csv("OUT\\overflow2Benchmark.out", stringsAsFactors = TRUE, strip.white = TRUE) %>% select(-benchID) %>% mutate(source = as.factor("Overflow2"))
classifierList[["O4"]] <- read.csv("OUT\\overflow4Benchmark.out", stringsAsFactors = TRUE, strip.white = TRUE) %>% select(-benchID) %>% mutate(source = as.factor("Overflow4"))
classifierList[["O8"]] <- read.csv("OUT\\overflow8Benchmark.out", stringsAsFactors = TRUE, strip.white = TRUE) %>% select(-benchID) %>% mutate(source = as.factor("Overflow8"))
classifierList[["O12"]] <- read.csv("OUT\\overflow12Benchmark.out", stringsAsFactors = TRUE, strip.white = TRUE) %>% select(-benchID) %>% mutate(source = as.factor("Overflow12"))

for (classifier in names(classifierList)) {
    classifierList[[classifier]] <- classifierList[[classifier]] %>% 
        mutate(inFile = factor(inFile, 
                               levels = c(
                                   "smallInt_small", "smallInt_medium", "smallInt_large", "smallInt_superLarge",
                                   "largeInt_small", "largeInt_medium", "largeInt_large", "largeInt_superLarge",
                                   "boltzmann_small", "boltzmann_medium", "boltzmann_large", "boltzmann_superLarge",
                                   "superLargeInt_small", "superLargeInt_medium", "superLargeInt_large"
                               ),
                               ordered = TRUE
                        )
        
        )
}

allClassifier <- classifierList$NoSplit
for (classifier in names(classifierList)) {
    if (classifier != "NoSplit") {
        allClassifier <- bind_rows(allClassifier,classifierList[[classifier]])
    }
}

#### Functions ####
getErrorMargin <- function(classifier) {
    return(
        classifier %>% 
            group_by(inFile, source, func) %>% 
            summarise(
                mu = mean(time),
                std = sd(time),
                n = n(),
                EM95_low = max(0,mu - 1.96 * std/sqrt(n)),
                EM95_high = mu + 1.96 * std/sqrt(n),
                .groups = "drop"
            ) %>%
            filter(func %in% c("transmit", "transmitRaw")) %>%
            droplevels()
    )
}

getTimeDecomp <- function(classifier) {
    return(
        classifier %>%
            filter(func!="transmitRaw") %>%
            group_by(inFile, source, func) %>%
            summarise(
                mu = mean(time),
                .groups = "drop"
            )
    )
}

#### Plots ####
##### Average transmission time with respect to compressor and Benchmark output #####
allClassifierEM <- getErrorMargin(allClassifier)
ggplot(allClassifierEM, aes(x = inFile, y = mu, color = func, group = func)) +
    geom_point(position = position_dodge(width = 0.3), size = 3) +
    geom_errorbar(
        aes(ymin = EM95_low, ymax = EM95_high),
        width = 0.2,
        position = position_dodge(width = 0.3)
    ) +
    geom_line(position = position_dodge(width = 0.3)) +
    facet_wrap(~source) +
    labs(
        x = "Benchmark files",
        y = "Average transmission time (in seconds)",
        color = "Transmission type"
    ) +
    theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
    ggtitle("Average transmission time with respect to the compressor and benchmark output")

##### Total average process time with respect to compressor and benchmark output ####
allClassifierTimeDecomp <- getTimeDecomp(allClassifier)
ggplot(allClassifierTimeDecomp, aes(x = inFile, y = mu, fill = func)) +
    geom_bar(stat = "identity") +
    facet_wrap(~source) +
    scale_fill_manual(values = c(
        "compress" = "#1f77b4",
        "decompress" = "#2ca02c",
        "transmit" = "#ff7f0e"
    )) +
    labs(
        x = "Benchmark files",
        y = "Total average process time (in seconds)",
        fill = "Operation"
    ) +
    theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
    ggtitle("Total average process time with respect to compressor and benchmark output")

#### Hypothesis testing ####
# For all compressor
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw") %>% select(time))$time,
    alternative = "less"
)

# For Split compressor
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit", source=="Split") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw", source=="Split") %>% select(time))$time,
    alternative = "less"
)

# For NoSplit compressor
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit", source=="NoSplit") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw", source=="NoSplit") %>% select(time))$time,
    alternative = "less"
)

# For Overflow1 compressor
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit", source=="Overflow1") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw", source=="Overflow1") %>% select(time))$time,
    alternative = "less"
)

# For Overflow2 compressor
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit", source=="Overflow2") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw", source=="Overflow2") %>% select(time))$time,
    alternative = "less"
)

# For Overflow4 compressor
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit", source=="Overflow4") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw", source=="Overflow4") %>% select(time))$time,
    alternative = "less"
)

# For Overflow8 compressor
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit", source=="Overflow8") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw", source=="Overflow8") %>% select(time))$time,
    alternative = "less"
)

# For Overflow12 compressor
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit", source=="Overflow12") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw", source=="Overflow12") %>% select(time))$time,
    alternative = "less"
)

# For smallInt_small
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit", inFile=="smallInt_small") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw", inFile=="smallInt_small") %>% select(time))$time,
    alternative = "less"
)

# For smallInt_medium
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit", inFile=="smallInt_medium") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw", inFile=="smallInt_medium") %>% select(time))$time,
    alternative = "less"
)

# For smallInt_large
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit", inFile=="smallInt_large") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw", inFile=="smallInt_large") %>% select(time))$time,
    alternative = "less"
)

# For smallInt_superLarge
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit", inFile=="smallInt_superLarge") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw", inFile=="smallInt_superLarge") %>% select(time))$time,
    alternative = "less"
)

# For largeInt_small
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit", inFile=="largeInt_small") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw", inFile=="largeInt_small") %>% select(time))$time,
    alternative = "less"
)

# For largeInt_medium
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit", inFile=="largeInt_medium") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw", inFile=="largeInt_medium") %>% select(time))$time,
    alternative = "less"
)

# For largeInt_large
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit", inFile=="largeInt_large") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw", inFile=="largeInt_large") %>% select(time))$time,
    alternative = "less"
)

# For largeInt_superLarge
DescTools::SignTest(
    as.vector(allClassifier %>% filter(func=="transmit", inFile=="largeInt_superLarge") %>% select(time))$time,
    as.vector(allClassifier %>% filter(func=="transmitRaw", inFile=="largeInt_superLarge") %>% select(time))$time,
    alternative = "less"
)