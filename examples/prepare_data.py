from src.atlasformatter import AtlasFormatter


def main():

    # Comment kısımlarını Zemberek kullanarak normalize eder ve çıktısını raw_data/test_normalize.csv dosyasına yazar.
    AtlasFormatter.normalize_comments("test.csv", "test_normalize.csv")

    # Normalize edilmiş dosyadaki tekrarlanan yorumları siler.
    AtlasFormatter.remove_duplicates("test_normalize.csv")

    # Dosyanın içerisinde yer alan comment kısmında en çok tekrar eden 5 kelimeyi bulur ve yorumların içinden siler.
    AtlasFormatter.remove_frequent_words("test_normalize.csv", word_count=5)

    # raw_data/test_normalize_removed_stopwords_zemberek_set dosyasını oluşturur.
    AtlasFormatter.convert_to_zemberek_train("test_normalize_removed_stopwords.csv")


if __name__ == "__main__":
    main()
