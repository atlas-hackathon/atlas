from src.atlasformatter import AtlasFormatter


def main():
    # AtlasFormatter.removeDuplicates("test_normalize.csv")
    AtlasFormatter.remove_frequent_words("test_normalize.csv", word_count=5)


if __name__ == "__main__":
    main()


