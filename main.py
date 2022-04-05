import pyautogui
import png
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


def determineFreq(words, yellowLetters, alpha):
    ALPHABET = alpha
    freqs = {}
    for char in ALPHABET:
        freqs[char] = [0, 0, 0, 0, 0]
    for i in range(0, 5):
        for word in words:
            if word[i] in ALPHABET:
                freqs[word[i]][i] += 1
                # Weight letters that have been classified as present
                if word[i] in yellowLetters:
                    freqs[word[i]][i] += 1000
    return freqs


def determineGuess(words, freq, numGuess):
    guessCtr = 0
    if numGuess <= 1:
        goodGuess = False
        while not goodGuess and guessCtr < 100:
            guess = random.choice(words)
            goodGuess = True
            # Could make more efficient but I don't really care
            for ch in guess:
                if guess.count(ch) > 1:
                    goodGuess = False
            guessCtr += 1
    else:
        newGuess = ""
        maxFitness = -1
        for word in words:
            currentFittness = 0
            for i in range(0, 5):
                currentFittness += freq[word[i]][i]
            if currentFittness > maxFitness:
                maxFitness = currentFittness
                newGuess = word
        guess = newGuess

    return guess


def main():
    validChars = "abcdefghijklmnopqrstuvwxyz"
    fin = open("wordle_words.txt")
    words = fin.readlines()
    fin.close()
    for i in range(len(words)):
        words[i] = words[i].strip()

    freq = determineFreq(words, [], validChars)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.nytimes.com/games/wordle/index.html")
    driver.maximize_window()
    time.sleep(3)

    bodyElement = driver.find_element(by=By.TAG_NAME, value="body")
    bodyElement.click()
    time.sleep(5)

    # find where the board is on the screen
    gameBoard = pyautogui.locateOnScreen("Wordle Board.png", confidence=0.8)
    time.sleep(3)

    # Input first guess
    badLetters = []
    goodLetters = []
    answer = ['', '', '', '', '']
    solved = False
    numGuess = 0
    guess = determineGuess(words, freq, numGuess)

    print("Num of Words:", len(words))

    while not solved and numGuess < 6:
        bodyElement.send_keys(guess)
        bodyElement.send_keys(Keys.ENTER)

        time.sleep(3)

        # see what happened with the guess
        screen = pyautogui.screenshot(region=(gameBoard.left, gameBoard.top, gameBoard.width, gameBoard.height))
        screen.save(r".\test.png")


        yellow = (181, 159, 59)
        green = (83, 141, 78)
        gray = (58, 58, 60)
        pixels = []
        for col in range(0, 5):
            pixels.append(screen.getpixel((4 + col * 68, 4 + numGuess * 70)))

        yellowLetters = ['', '', '', '', '']
        for i in range(0, 5):
            if pixels[i] == green:
                answer[i] = guess[i]
            elif pixels[i] == gray:
                badLetters.append(guess[i])
            elif pixels[i] == yellow:
                yellowLetters[i] = guess[i]
                goodLetters.append(guess[i])

        delBadLetters = badLetters.copy()

        for char in badLetters:
            if char in yellowLetters or char in answer:
                delBadLetters.remove(char)
            else:
                validChars = validChars.replace(char, "")
        badLetters = delBadLetters.copy()

        # remove all words that don't have correct letter in right spot
        delWords = words.copy()
        for word in words:
            delete = False
            c = 0
            while c < 5 and not delete:
                if answer[c] != '':
                    if word[c] != answer[c]:
                        delete = True
                        delWords.remove(word)
                c += 1

        words = delWords.copy()
        delWords = words.copy()

        # remove all words that have yellow letters in the wrong location
        for word in words:
            delete = False
            c = 0
            while c < 5 and not delete:
                if yellowLetters[c] != '':
                    if word[c] == yellowLetters[c]:
                        delete = True
                        delWords.remove(word)
                c += 1

        words = delWords.copy()
        delWords = words.copy()

        # remove words where gray letter is in specific location
        # case where word has repeat letter where one is green or yellow

        # remove all words that have already guessed letters in them
        for word in words:
            delete = False
            for c in badLetters:
                if c in word:
                    delete = True
            if delete:
                delWords.remove(word)

        words = delWords.copy()

        # determine if solved
        solved = True
        for c in answer:
            if c == '':
                solved = False

        freq = determineFreq(words, goodLetters, validChars)
        numGuess += 1
        guess = determineGuess(words, freq, numGuess)

        print("Guess:", guess)
        print("Num of Words:", len(words))
        time.sleep(3)

    if solved:
        print("I did it! :)")
    input("Hit Enter to Continue...")


if __name__ == "__main__":
    main()
