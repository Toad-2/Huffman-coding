"""
huffman_compressor_v1.py

This is an experimental implementation of huffman coding/compression using python

Ideas for improvements:
 - Find a more efficient way to store the nested lists of the decompression tree than pickle
 This would likely take some sort of custom logic/function
 The saved object does not need to be the actual list, could also be something that could be used to reconstruct the list during decompression
 - Add CLI arguments to allow for
"""


def frequency_counter(to_analyze:str) -> dict:
    """
    Takes in a text string and returns a dictionary with the frequency of each character in the string
    :param to_analyze: string to be analyzed
    :returns: dictionary containing the frequency of all characters in string (in the form of {a:12, b:10})
    """

    frequency = {}
    # passed in string is enumerated through and for each occurrence of a character, its frequency value is += by one
    for char in to_analyze:
        if char in frequency:
            frequency[char] += 1
        else:
            frequency[char] = 1

    return frequency

def tree_builder(to_grow: dict) -> tuple:
    """
    Converts a frequency dictionary into a huffman tree
    Also generates a dictionary with each character and its associated path in the tree
    :param to_grow: the frequency dictionary to be converted into tree
    :returns: A set of nested lists representing a huffman tree and dictionary hhhhhh containing path information for characters
    """

    # sorts passed frequency dictionary by number of occurrences per character (largest to smallest)
    # dictionary contents are layed out in tuple with an additional dictionary to track character paths
    # form: (char, [freq, {trace}])
    sorted_frequency = [(char[0], [char[1], {char[0]: ""}]) for char in
                        sorted(to_grow.items(), key=lambda keys: keys[1], reverse=True)]

    # lambda function to increment the character trace with desired character
    char_count = lambda app_val, count_loc: {char: app_val + counter for char, counter in count_loc.items()}

    while len(sorted_frequency) > 2:
        set1, set2 = sorted_frequency.pop(-1), sorted_frequency.pop(-1)  # pops last two elements from list

        # creates new branch element
        branch_worker = [set1[0], set2[0]]  # new branch
        branch_freq = set1[1][0] + set1[1][0]  # calculates new frequency for branch
        char_tracker = char_count("0", set1[1][1]) | char_count("1", set2[1][1])  # updates trace dicts and combines
        new_branch = (branch_worker, [branch_freq, char_tracker])  # combines work into complete new element

        sorted_frequency.append(new_branch)  # re-appends new element to list
        sorted_frequency = [char for char in
                            sorted(sorted_frequency, key=lambda keys: keys[1][0], reverse=True)]  # re-sorts

    grown_tree = [leaf[0] for leaf in sorted_frequency]  # strips elements to pure branch lists
    tracker = char_count("0", sorted_frequency[0][1][1]) | char_count("1", sorted_frequency[1][1][
        1])  # strips out and combines trace dicts

    return grown_tree, tracker

def encoder(map:dict, to_encode:str) -> str:
    """
    Encodes given string as its bit representation using the passed in huffman tree trace dictionary
    :param map: takes character path dictionary used for encoding
    :param to_encode: the string to be encoded
    :return: string of 1s and 0s representing encoded string
    """

    # all this code... just to run this stupid, simple for loop...
    # gonna cry
    encoded = ""

    for char in to_encode:
        encoded += map[char]

    return encoded

def to_bits(to_convert:str) -> bytearray:
    """
    Takes in string of 1s and 0s and coverts to actual binary using int and bytearray
    :param to_convert: string of 1s and 0s to be converted into bytes
    :return: bytearray with 1s and 0s of passed in string
    """

    # pads bits up to the nearest byte so things don't break
    # number of padded bytes is recorded and stored in binary data
    padding = 0
    while len(to_convert) % 8 != 0:
        to_convert += "1"
        padding += 1

    # separates string into 8 character chunks and converts into integer values, adding to a list
    # pythons byte level working makes me want to cry
    chunked = [padding]
    for chunk in range(0, len(to_convert), 8):
        chunked.append(int(to_convert[chunk:chunk + 8], 2))

    byte_convert = bytearray(chunked)  # converts list of ints into byte string
    return byte_convert

def decoder(tree:list, string:str) -> str:
    """

    :param tree: huffman tree of nested list to be used for decoding
    :param string: string of ones and zeros to be decoded back to text
    :return: decoded string
    """

    def recursion(branch:list, section:str) -> tuple:
        """
        Recursive function to decoded characters from tree
        :param branch: slice of nested tree to be looked in
        :param section: string of 1s and 0s that is being recoded
        :return: final recursion layer returns a single character and the string
        """

        new_val = int(section[0])  # takes first "bit" from string and converts to int
        cut_down = section[1:]  # removes character from string

        # checks if new int returns character from tree
        # if it does the character is returned, if not function is recursed
        if isinstance(branch[new_val], str):
            return branch[new_val], cut_down
        else:
            return recursion(branch[new_val], cut_down)

    work_string = string
    decoded = ""
    # while loop runs so long as characters are decode string
    while work_string:
        char, new_work = recursion(tree, work_string)
        decoded += char  # appends found character to string
        work_string = new_work  # assigns cut down string to decode string

    return decoded

def encode():
    from pickle import dumps

    compress_file = input("What file would you like to compress? ")
    with open(compress_file, "r") as file:  # ensures the file is imported with ascii encoding
        file_content = file.read()  # dumps the files content as a string
    print(f"{compress_file} opened")

    freq_dict = frequency_counter(file_content)  # converts file contents into frequency dictionary
    grown, tracked = tree_builder(freq_dict)  # converts to huffman tree
    encoded_str = encoder(tracked, file_content)  # uses huffman tree to convert original text into encoded bits
    byte_encode = to_bits(encoded_str)  # encodes to byte array for writing

    tree_to_bits = dumps(grown)  # converts nested tree into bytes
    # converts length of pickled list into bytes
    try:
        len_tree = len(tree_to_bits).to_bytes(2, "big")

        final_write = len_tree + tree_to_bits + byte_encode  # builds final byte string

        save_file = input("What do you want to name the compressed file? ")
        with open(save_file, "wb") as file:
            file.write(final_write)

        print(f"Compressed text save to {save_file}, compression ratio of {round((len(final_write) / len(file_content)) * 100, 2)}%")

    except OverflowError:
        exit("Something has failed catastrophically during encoding")

def decode():
    from pickle import loads

    input_file = input("What file would you like to decompress? ")
    with open(input_file, "rb") as file:
        compressed = file.read()
    print(f"{input_file} opened")

    len_tree = int.from_bytes(compressed[:2], "big")  # grabs length of encoded decompress tree
    decomp_tree = loads(compressed[2:len_tree + 2])  # pulls decompress tree from file and converts to list with pickle
    padding = compressed[len_tree + 2]  # pulls out length of bit padding for compressed string
    decode_string = compressed[len_tree + 3:]  # pulls compressed string

    bit_list = [byte for byte in decode_string]
    bit_string = ""
    for num in bit_list:
        bit_string += bin(num)[2:].zfill(8)

    final = decoder(decomp_tree, bit_string[:-padding])
    print(final)

    while True:
        user = input("\n\nDo you want to save the decoded text to a file? (y/n): ")[0].lower()
        if user == "n":
            break
        elif user == "y":
            file_name = input("What do you want the file to be named? ")
            with open(file_name, "w") as file:
                file.write(final)

            print(f"Decompressed text saved to {file_name}")
            break
        else:
            print("Could not determine answer, please try again.")

if __name__ == "__main__":
    while True:
        user_in = input("Would you like to compress or decompress a file? (c/d): ")[0].lower()
        if user_in == "c":
            print("Mode: compression")
            encode()
            break
        elif user_in == "d":
            print("Mode: decompression")
            decode()
            break
        else:
            print("Could not determine answer, please try again.")