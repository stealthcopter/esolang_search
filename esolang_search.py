import os, os.path, shutil
import requests
import argparse
from bs4 import BeautifulSoup
from termcolor import colored
import random

# Grab all languages on https://esolangs.org
URL_ESOLANG_BASE = "https://esolangs.org"
URL_WIKI = URL_ESOLANG_BASE + "/wiki"
LANGUAGE_LIST = "/wiki/Language_list"

CACHE_DIR = "cache/"

HTML_DESC_TAGS = ["p","li"]
HTML_CODE_TAGS = ["pre","code"]

verboseness = 1

class language(object):
    def __init__(self, title, link):
        self.title = title
        self.link = link
        self.titleHits = {}
        self.descHits = {}
        self.codeHits = {}
        
    def getScore(self):
        return len(self.titleHits) * 10 + len(self.descHits) * 10 + len(self.codeHits) * 10
    
    def addHit(self, dic, term):
        if term in dic:
            dic[term] += 1
        else:
            dic[term] = 1
    
    def addTitleHit(self, term):
        self.addHit(self.titleHits, term)
    def addDescHit(self, term):
        self.addHit(self.descHits, term)    
    def addCodeHit(self, term):
        self.addHit(self.codeHits, term)
    def getMatches(self):
        matches = "\t"
        if len(self.titleHits) > 0:
            matches += "Title: "+(','.join(self.titleHits.keys())+"\t")
        if len(self.descHits) > 0:
            matches += "Desc: "+(','.join(self.descHits.keys())+"\t")        
        if len(self.codeHits) > 0:
            matches += "Code: "+(','.join(self.codeHits.keys())+"\t")
        return matches
def printVerbose(level, message):
    if verboseness >= level:
        print(message)

def print_color(message, color):
    print(colored(message, color))
def print_error(message):
    print_color(message,'red')

def banner():
    color = random.choice(['green', "yellow", "red", "magenta", "cyan"])
    print("")
    print_color("  ▓█████   ██████  ▒█████   ██▓    ▄▄▄       ███▄    █   ▄████", color)
    print_color("  ▓█   ▀ ▒██    ▒ ▒██▒  ██▒▓██▒   ▒████▄     ██ ▀█   █  ██▒ ▀█▒", color)
    print_color("  ▒███   ░ ▓██▄   ▒██░  ██▒▒██░   ▒██  ▀█▄  ▓██  ▀█ ██▒▒██░▄▄▄░", color)
    print_color("  ▒▓█  ▄   ▒   ██▒▒██   ██░▒██░   ░██▄▄▄▄██ ▓██▒  ▐▌██▒░▓█  ██▓", color)
    print_color("  ░▒████▒▒██████▒▒░ ████▓▒░░██████▒▓█   ▓██▒▒██░   ▓██░░▒▓███▀▒", color)
    print_color("  ░░ ▒░ ░▒ ▒▓▒ ▒ ░░ ▒░▒░▒░ ░ ▒░▓  ░▒▒   ▓▒█░░ ▒░   ▒ ▒  ░▒   ▒ ", color)
    print_color("   ░ ░  ░░ ░▒  ░ ░  ░ ▒ ▒░ ░ ░ ▒  ░ ▒   ▒▒ ░░ ░░   ░ ▒░  ░   ░ ", color)
    print_color("     ░   ░  ░  ░  ░ ░ ░ ▒    ░ ░    ░   ▒      ░   ░ ░ ░ ░   ░ ", color)
    print_color("     ░  ░      ░      ░ ░      ░  ░     ░  ░         ░       ░ \n", color)
    print_color("    ██████ ▓█████ ▄▄▄       ██▀███   ▄████▄   ██░ ██           ", color)
    print_color("  ▒██    ▒ ▓█   ▀▒████▄    ▓██ ▒ ██▒▒██▀ ▀█  ▓██░ ██▒          ", color)
    print_color("  ░ ▓██▄   ▒███  ▒██  ▀█▄  ▓██ ░▄█ ▒▒▓█    ▄ ▒██▀▀██░          ", color)
    print_color("    ▒   ██▒▒▓█  ▄░██▄▄▄▄██ ▒██▀▀█▄  ▒▓▓▄ ▄██▒░▓█ ░██           ", color)
    print_color("  ▒██████▒▒░▒████▒▓█   ▓██▒░██▓ ▒██▒▒ ▓███▀ ░░▓█▒░██▓          ", color)
    print_color("  ▒ ▒▓▒ ▒ ░░░ ▒░ ░▒▒   ▓▒█░░ ▒▓ ░▒▓░░ ░▒ ▒  ░ ▒ ░░▒░▒          ", color)
    print_color("  ░ ░▒  ░ ░ ░ ░  ░ ▒   ▒▒ ░  ░▒ ░ ▒░  ░  ▒    ▒ ░▒░ ░          ", color)
    print_color("  ░  ░  ░     ░    ░   ▒     ░░   ░ ░         ░  ░░ ░          ", color)
    print_color("        ░     ░  ░     ░  ░   ░     ░ ░       ░  ░  ░          ", color)
    print_color("                                    ░                          \n", color)
    print(" Website: https://github.com/stealthcopter/esolang_search")
    print(" Author: Stealthcopter\n")
    print(" Search for esoteric languages by title, descriptions and or code examples\n")

def examples():
    print("\nExamples:\n")
    print("python3.6 esolang_search.py")
    print("  - Enter interactive mode (wizard like)")
    print("python3.6 esolang_search.py -t \"pie\" -d \"abstract art David Morgan\"")
    print("  - Search for a language with pie in the title and the terms 'abstract', 'art', 'David' and 'Morgan' in the description")
    print("python3.6 esolang_search.py -t \"fuck\" -c \"+++ ] , < >\"")
    print("  - Search for a language with fuck in the title and code that contains symbols like +++ ] , < >\n\n")

def responseToFile(title, content):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    file = open(CACHE_DIR+title, "w")
    file.write(content)
    file.close()

def createFileSafeName(url):
    return url.replace(URL_WIKI+"/","").replace("/","\\x2f")
    
def getAllLanguages():
    # Grab all the languages from the esolang indexing page
    
    if os.path.isfile(CACHE_DIR+"index.html"):
       # Use the cached index page
       printVerbose(3, "Using cached index page")
       with open (CACHE_DIR+"index.html", "r") as cacheFile:
            content = cacheFile.read()
    else:
        # Download the index page
        r = requests.get(URL_ESOLANG_BASE+LANGUAGE_LIST)

        # Grab language list from esolangs
        if r.status_code != requests.codes.ok:
            print_error("Sorry! Could not download esolang list :(Status code:"+str(r.status_code))
            return []

        content = r.text

        responseToFile("index.html", content)

        printVerbose(1,"Language list downloaded")
    
    langs = []

    for langLine in content.split("\n"):
        if "<li> <a href=\"/wiki/" in langLine:
            
            s = langLine.find("title=\"") + 7
            title = langLine[s:langLine.find("\"", s)] 
            
            s = langLine.find("href=\"") + 6
            link = URL_ESOLANG_BASE+langLine[s:langLine.find("\"", s)] 
            
            langs.append(language(title, link))
    
    printVerbose(1, "Languages to search"+str(len(langs)))
    
    return langs

def getAllLanguagesPages(languages):
    # TODO: Progress?
    # TODO: Parrellize?
    for language in languages:
        
        url = language.link
        urlPageName = createFileSafeName(url)
        
        if os.path.isfile(CACHE_DIR+urlPageName):
            # Already in cache, no need to fetch again
            continue
        
        printVerbose(3, "Url:"+url+" page: "+urlPageName)

        r = requests.get(language.link)
        if r.status_code != requests.codes.ok:
            print("Error downloading article ",url," Status code:", r.status_code)
            continue
        
        responseToFile(urlPageName, r.text)

def searchLanguagesByName(languages, searchTerms, caseSensitive = False):
    if len(languages) == 0:
        print_error("Error languages size is 0")
        return languages
    
    printVerbose(1, "Searching by name..."+('[%s]' % ', '.join(map(str, searchTerms))))

    for lang in languages:
        title = lang.title
        link = lang.link
        for term in searchTerms:
            if (caseSensitive and term in title) or (term.lower() in title.lower()):
                lang.addTitleHit(term)
    
    return languages

def searchLanguagePageForDesc(languages, descTerms, caseSensitive = False):
    printVerbose(1, "Searching by description..."+('[%s]' % ', '.join(map(str, descTerms))))
    
    for language in languages:
        url = language.link
        urlPageName = createFileSafeName(url)
        
        if not os.path.isfile(CACHE_DIR+urlPageName):
            print_error("Error language not in cache")
            return
        
        with open (CACHE_DIR+urlPageName, "r") as cacheFile:
            page = cacheFile.read()
        
        soup = BeautifulSoup(page, 'html.parser')
        
        listings_data = soup.find_all(HTML_DESC_TAGS)

        for data in listings_data:
            for term in descTerms:
                if (caseSensitive and term in data.text) or (term.lower() in data.text.lower()):
                    language.addDescHit(term)

    return languages

def searchLanguagePageForCode(languages, codeTerms, caseSensitive = False):
    printVerbose(1, "Searching by code..."+('[%s]' % ', '.join(map(str, codeTerms))))
    
    for language in languages:
        url = language.link
        urlPageName = createFileSafeName(url)
        
        if not os.path.isfile(CACHE_DIR+urlPageName):
            print_error("Error language not in cache")
            return
        
        with open (CACHE_DIR+urlPageName, "r") as cacheFile:
            page = cacheFile.read()
        
        soup = BeautifulSoup(page, 'html.parser')
        
        listings_data = soup.find_all(HTML_CODE_TAGS)

        for data in listings_data:
            for term in codeTerms:
                if (caseSensitive and term in data.text) or (term.lower() in data.text.lower()):
                    language.addCodeHit(term)

    return languages

def printResult(results, max_results = 10):
    if len(results) == 0:
        print_error("Sorry there were no results")
        return
    
    printVerbose(1, "\nScore | Title | Link")
    noResults = 0
    for result in sorted(results, key=lambda lang: lang.getScore(), reverse=True):
        noResults+=1
        if noResults > max_results or result.getScore() == 0:
                break
        
        print(result.getScore(),colored(result.title, "cyan",None,["bold"]), colored(result.link, "magenta",None,["underline"]))
        matches = result.getMatches()
        if verboseness > 0 and not matches == "":
            print(matches)
    print()

def run(searchTerms, descTerms, codeTerms, max_results = 10):
    # Setup search parameters
    searchByName = len(searchTerms) != 0
    searchByDesc = len(descTerms) != 0
    searchByCode = len(codeTerms) != 0
    needsLanguagePages = searchByDesc or searchByCode
    
    # Download the index page
    languages = getAllLanguages()

    # Download all language pages iff needed
    if needsLanguagePages:
        getAllLanguagesPages(languages)

    if searchByName:
        languages = searchLanguagesByName(languages, searchTerms)

    if searchByDesc:
        languages = searchLanguagePageForDesc(languages, descTerms)

    if searchByCode:
         languages = searchLanguagePageForCode(languages, codeTerms)

    # Print results
    printResult(languages, max_results = max_results)

def interactiveInputMode():
    searchTerms=[]
    descTerms=[]
    codeTerms=[]
    
    printVerbose(1, "Entering interactive mode:")
    termInput = input("Enter title search terms separated by a space (blank for none): \n")
    
    if termInput is not "":
        searchTerms = termInput.split(" ")

    termInput = input("Enter description search terms separated by a space (blank for none): \n")
    if termInput is not "":
        descTerms = termInput.split(" ")

    termInput = input("Enter code examples separated by a space (blank for none): \n")
    if termInput is not "":
        codeTerms = termInput.split(" ")

    if len(searchTerms) == 0 and len(descTerms) == 0 and len(codeTerms) == 0:
        print("You must enter at least one search term or code example to search for")
        exit
        
    run(searchTerms, descTerms, codeTerms)


parser = argparse.ArgumentParser(description='Search for esoteric languages by their name, description or code examples')
parser.add_argument("-t", "--title", help="text to search for in the title of a language")
parser.add_argument("-d", "--desc", help="text to search for in the description of a language")
parser.add_argument("-c", "--code", help="text to search for in the code examples of a language")

# parser.add_argument("-dsh", "--dont-show-hits", help="Don't show the search hits for each result", action='count')
parser.add_argument("-m", "--max-results", help="Maximum number of results to show",  type=int, default=10)
parser.add_argument("-dc", "--delete-cache", help="Delete the cache following completion", action='count')

parser.add_argument("-q", "--quiet", help="Only output results", action='count')
parser.add_argument("-v", "--verbose", action='count')

args = parser.parse_args()

print(args)

# Set verboseness global
if args.verbose != None:
    verboseness = args.verbose

# Set quiet flag
if args.quiet != None:
    verboseness = 0

if (args.title == None and args.desc == None and args.code == None):
    if args.quiet == None:
        banner()
        examples()
    interactiveInputMode()
    
else:
    if args.quiet == None:
        banner()
    
    searchTerms=[]
    descTerms=[]
    codeTerms=[]        
        
    if args.title is not None:
        searchTerms = args.title.split(" ")
    if args.desc is not None:
        descTerms = args.desc.split(" ") 
    if args.code is not None:
        codeTerms = args.code.split(" ") 
    
    run(searchTerms, descTerms, codeTerms, max_results = args.max_results)


if args.delete_cache is not None:
    print("Deleting cache folder")
    shutil.rmtree(CACHE_DIR)
    
