from jpype import JClass, JString, getDefaultJVMPath, shutdownJVM, startJVM
from os.path import join
import pandas as pd


class AtlasFormatter:
    """
       A class used to represent formatter tools for preparing nlp data training.

       Methods
       -------
        get_comments(file=None)
            Returns the comment column from the csv file as a list.
        get_scores(file=None)
            Returns the comment scores from the csv file as a list.
        list_to_file(list, file)
            Writes a list to a file
        convert_to_zemberek_train(file)
            Converts a formatted csv file to the zemberek training dataset format.
        normalize_comments(unformatted_file, normalized_file)
            Normalize comments from a file and writes them in another file
        remove_duplicates(file)
            Remove duplicate comments from the csv file.
        find_frequent_words(file, count=5)
            Returns the most common words from the comments column in the csv file.
        sortSecond(val)
            Returns the second column of a list
        get_path(file)
            Returns the path of the raw_data directory with the file name.
       """

    @staticmethod
    def get_comments(file=None):
        """
        Returns the comment column from the csv file as a list.

        Parameters
        ----------
        file : str
            The name of the csv file under the raw_data directory
        """
        path = AtlasFormatter.get_path(file)
        comments = []
        with open(path, 'r') as f:
            try:
                line = f.readline()
                while line:
                    line = f.readline()
                    if line:
                        comments.append(line.split('|')[0])
                        line = f.readline()
                f.close()
            except Exception as ex:
                print(str(ex))

        return comments

    @staticmethod
    def get_scores(file=None):
        """
        Returns the scores column from the csv file as a list.

        Parameters
        ----------
        file : str
            The name of the csv file under the raw_data directory
        """
        path = AtlasFormatter.get_path(file)
        scores = []
        with open(path, 'r') as f:
            try:
                line = f.readline()
                while line:
                    line = f.readline()
                    if line:
                        try:
                            scores.append(float(line.split('|')[1]))
                        except Exception:
                            print("Error in" + line)
                        line = f.readline()
                f.close()
            except Exception as ex:
                print(str(ex))
        return scores

    @staticmethod
    def list_to_file(list, file):
        """
        Writes a list into a file.

        Parameters
        ----------
        list : list
            List object
        file : str
            The name of the csv file which will be created under the raw_data directory
        """
        path = AtlasFormatter.get_path(file)
        try:
            f = open(path, 'w')
        except Exception as ex:
            print(str(ex))
            exit(1)

        for item in list:
            f.write(item)

        f.close()

    @staticmethod
    def convert_to_zemberek_train(file):
        """
        Converts the csv file to the zemberek training format which shown on the below:

            __label__olumlu sentences
            __label__notr sentences
            __label__olumsuz sentences

        Parameters
        ----------
        file : str
            The name of the csv file under the raw_data directory
        """
        path = AtlasFormatter.get_path(file)
        set = AtlasFormatter.get_path(str(file).split(".csv")[0] + "_zemberek_set")
        w = open(set, 'w')
        with open(path, 'r') as f:
            line = f.readline()
            while line:
                line = f.readline()
                if line:
                    tmp = line.split('|')
                    if float(tmp[1].rstrip("\n")) > 0:
                        score = "olumlu"
                    elif float(tmp[1].rstrip("\n")) == 0:
                        score = "notr"
                    else:
                        score = "olumsuz"
                    w.write("__label__" + score + " " + tmp[0] + "\n")
            f.close()
            w.close()
        print("Zemberek eğitim dosyası oluşturuldu. Dosya " + set)

    @staticmethod
    def normalize_comments(unformatted_file, normalized_file):
        """
        Normalize the comments from a csv file and writes them a new file under the raw_data directory.

        Parameters
        ----------
        unformatted_file : str
            The name of the input csv file under the raw_data directory
        normalized_file : str
            The name of the output csv file under the raw_data directory
        """
        ZEMBEREK_PATH: str = join('..', 'bin', 'zemberek-full.jar')

        print(ZEMBEREK_PATH)

        startJVM(
            getDefaultJVMPath(),
            '-ea',
            f'-Djava.class.path={ZEMBEREK_PATH}',
            convertStrings=False
        )

        TurkishMorphology: JClass = JClass('zemberek.morphology.TurkishMorphology')
        TurkishSentenceNormalizer: JClass = JClass(
            'zemberek.normalization.TurkishSentenceNormalizer'
        )
        Paths: JClass = JClass('java.nio.file.Paths')

        normalizer = TurkishSentenceNormalizer(
            TurkishMorphology.createWithDefaults(),
            Paths.get(
                join('..', 'data', 'normalization')
            ),
            Paths.get(
                join('..', 'data', 'lm', 'lm.2gram.slm')
            )
        )

        comments = AtlasFormatter.get_comments(unformatted_file)
        scores = AtlasFormatter.get_scores(unformatted_file)

        final = []
        for i, comment in enumerate(comments):
            if comment.__len__() > 1:
                normalizer.normalize(JString(comment))
                final.append(comment.strip("\n") + "|" + str(format(scores[i], ".2f")))

        shutdownJVM()

        pretrained = []
        pretrained.append("Comment|Score\n")
        for i in range(len(final) - 1):
            tmp = final[i]
            if tmp != final[i + 1]:
                pretrained.append(tmp + "\n")

        AtlasFormatter.list_to_file(pretrained, normalized_file)

    @staticmethod
    def remove_duplicates(file):
        """
        Removes the duplicate comments from the csv file.

        Parameters
        ----------
        file : str
            The name of the input csv file under the raw_data directory
        """
        path = AtlasFormatter.get_path(file)
        # Advanced CSV loading example

        data = pd.read_csv(
            path,  # relative python path to subdirectory
            sep='|',  # Tab-separated value file.
            quotechar="'",  # single quote allowed as quote character
            usecols=['Comment', 'Score']  # Only load the three columns specified.
        )

        # sorting by first name
        data.sort_values("Comment", inplace=True)

        # dropping ALL duplicte values
        data.drop_duplicates(subset="Comment",
                             keep="first", inplace=True)
        data.to_csv(path_or_buf=path, sep="|", index=False)

    @staticmethod
    def find_frequent_words(file, count=5):
        """
        Returns the certain amount of frequent words from a csv file.

        Parameters
        ----------
        file : str
            The name of the input csv file under the raw_data directory
        count : int
            The number of the frequent words.
        """
        path = AtlasFormatter.get_path(file)

        data = pd.read_csv(
            path,  # relative python path to subdirectory
            sep='|',  # Tab-separated value file.
            quotechar="'",  # single quote allowed as quote character
            usecols=['Comment', 'Score']  # Only load the three columns specified.
        )
        comments = data['Comment'].tolist()

        words = []
        for c in comments:
            csv_words = str(c).lower().split(" ")
            for i in csv_words:
                words.append(i)

        words_counted = []
        for i in words:
            if i != '':
                x = words.count(i)
                words_counted.append((i, x))

        # sorts the array in descending according to
        # second element
        words_counted.sort(key=AtlasFormatter.sortSecond, reverse=True)

        freq = list(dict.fromkeys(words_counted))[:count]

        freq_words = []
        for i in freq:
            freq_words.append(i[0])

        return freq_words

    @staticmethod
    def remove_frequent_words(file, word_count=5):
        """
        Removes the certain amount of frequent words from a csv file.

        Parameters
        ----------
        file : str
            The name of the input csv file under the raw_data directory
        word_count : int
            The number of the frequent words.
        """
        freq = AtlasFormatter.find_frequent_words(file, count=word_count)
        path = AtlasFormatter.get_path(file)

        comments = AtlasFormatter.get_comments(file)
        scores = AtlasFormatter.get_scores(file)
        final = []
        for i, comment in enumerate(comments):
            if comment.__len__() > 1:
                commentwords = comment.split()
                resultwords = [word for word in commentwords if word.lower() not in freq]
                result = ' '.join(resultwords)
                final.append(result.strip("\n") + "|" + str(format(scores[i], ".2f") + "\n"))

        AtlasFormatter.list_to_file(final, "removed_frequent_words.csv")

    @staticmethod
    def sortSecond(val):
        """
        Returns the second column of a list

        Parameters
        ----------
        val : list
            List object
        """
        return val[1]

    @staticmethod
    def get_path(file):
        """
        Returns the raw_data directory with the file name.

        Parameters
        ----------
        file : str
            File name
        """
        return str(join('..', 'raw_data', file))
