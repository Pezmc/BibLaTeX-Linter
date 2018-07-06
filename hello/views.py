from django.shortcuts import render
from django.http import HttpResponse

libraries = [
  ("Scholar", "http://scholar.google.de/scholar?hl=en&q="),
  ("Google", "https://www.google.com/search?q="),
  ("DBLP", "http://dblp.org/search/index.php#query="),
  ("IEEE", "http://ieeexplore.ieee.org/search/searchresult.jsp?queryText="),
  ("ACM", "http://dl.acm.org/results.cfm?query="),
]

# fields that are required for a specific type of entry
requiredFields = {
  "article": ["author", "title", "journaltitle/journal", "year/date"],
  "book": ["author", "title", "year/date"],
  "mvbook": "book",
  "inbook": ["author", "title", "booktitle", "year/date"],
  "bookinbook": "inbook",
  "suppbook": "inbook",
  "booklet": ["author/editor", "title", "year/date"],
  "collection": ["editor", "title", "year/date"],
  "mvcollection": "collection",
  "incollection": ["author", "title", "booktitle", "year/date"],
  "suppcollection": "incollection",
  "manual": ["author/editor", "title", "year/date"],
  "misc": ["author/editor", "title", "year/date"],
  "online": ["author/editor", "title", "year/date", "url"],
  "patent": ["author", "title", "number", "year/date"],
  "periodical": ["editor", "title", "year/date"],
  "suppperiodical": "article",
  "proceedings": ["title", "year/date"],
  "mvproceedings": "proceedings",
  "inproceedings": ["author", "title", "booktitle", "year/date"],
  "reference": "collection",
  "mvreference": "collection",
  "inreference": "incollection",
  "report": ["author", "title", "type", "institution", "year/date"],
  "thesis": ["author", "title", "type", "institution", "year/date"],
  "unpublished": ["author", "title", "year/date"],

  # semi aliases (differing fields)
  "mastersthesis": ["author", "title", "institution", "year/date"],
  "techreport": ["author", "title", "institution", "year/date"],

  # other aliases
  "conference": "inproceedings",
  "electronic": "online",
  "phdthesis": "mastersthesis",
  "www": "online",
  "school": "mastersthesis"
}

import string
import re
import sys
from optparse import OptionParser

# Create your views here.
def index(request):
  # return HttpResponse('Hello from Python!')
  return render(request, 'index.html')

def validate(request):
  usedIds = set()

  completeEntry = ""
  currentId = ""
  ids = []
  currentType = ""
  currentArticleId = ""
  currentTitle = ""
  fields = []
  problems = []
  subproblems = []

  counterMissingFields = 0
  counterFlawedNames = 0
  counterWrongTypes = 0
  counterNonUniqueId = 0
  counterWrongFieldNames = 0

  removePunctuationMap = dict((ord(char), None) for char in string.punctuation)

  file = request.POST['file']
  for line in file.splitlines():
    line = line.strip("\n")
    if line.startswith("@"):
      if currentId in usedIds or not usedIds:
        for fieldName, requiredFieldsType in requiredFields.items():
          if fieldName == currentType.lower():
            # alises use a string to point at another set of fields
            currentRequiredFields = requiredFieldsType
            while isinstance(currentRequiredFields, str):
              currentRequiredFields = requiredFields[currentRequiredFields] # resolve alias

            for requiredFieldsString in currentRequiredFields:
              # support for author/editor syntax
              typeFields = requiredFieldsString.split('/')

              # at least one the required fields is not found
              if set(typeFields).isdisjoint(fields):
                subproblems.append(
                  "missing field '" + requiredFieldsString + "'")
                counterMissingFields += 1
      else:
        subproblems = []

      if currentId in usedIds or (currentId and not usedIds):
        cleanedTitle = currentTitle.translate(removePunctuationMap)
        problem = "<div id='" + currentId + \
          "' class='problem severe" + str(len(subproblems)) + "'>"
        problem += "<h2>" + currentId + " (" + currentType + ")</h2> "
        problem += "<div class='links'>"

        list = []
        for name, site in libraries:
          list.append(
            " <a href='" + site + cleanedTitle + "' target='_blank'>" + name + "</a>")
        problem += " | ".join(list)

        problem += "</div>"
        problem += "<div class='reference'>" + currentTitle
        problem += "</div>"
        problem += "<ul>"
        for subproblem in subproblems:
          problem += "<li>" + subproblem + "</li>"
        problem += "</ul>"
        problem += "<form class='problem_control'><label>checked</label><input type='checkbox' class='checked'/></form>"
        problem += "<div class='bibtex_toggle'>Current BibLaTex Entry</div>"
        problem += "<div class='bibtex'>" + completeEntry + "</div>"
        problem += "</div>"
        problems.append(problem)
      fields = []
      subproblems = []
      currentId = line.split("{")[1].rstrip(",\n")
      if currentId in ids:
        subproblems.append("non-unique id: '" + currentId + "'")
        counterNonUniqueId += 1
      else:
        ids.append(currentId)
      currentType = line.split("{")[0].strip("@ ")
      completeEntry = line + "<br />"
    else:
      if line != "":
        completeEntry += line + "<br />"
      if currentId in usedIds or not usedIds:
        if "=" in line:
          # biblatex is not case sensitive
          field = line.split("=")[0].strip().lower()
          fields.append(field)
          value = line.split("=")[1].strip("{} ,\n")
          if field == "author":
            currentAuthor = filter(
              lambda x: not (x in "\\\"{}"), value.split(" and ")[0])
          if field == "citeulike-article-id":
            currentArticleId = value
          if field == "title":
            currentTitle = re.sub(r'\}|\{', r'', value)

          ###############################################################
          # Checks
          ###############################################################

          # check if type 'proceedings' might be 'inproceedings'
          if currentType == "proceedings" and field == "pages":
            subproblems.append(
              "wrong type: maybe should be 'inproceedings' because entry has page numbers")
            counterWrongTypes += 1

          # check if abbreviations are used in journal titles
          if currentType == "article" and (field == "journal" or field == "journaltitle"):

            if "." in line:
              subproblems.append(
                "flawed name: abbreviated journal title '" + value + "'")
              counterFlawedNames += 1

          # check booktitle format; expected format "ICBAB '13: Proceeding of the 13th International Conference on Bla and Blubb"
          # if currentType == "inproceedings" and field == "booktitle":
            # if ":" not in line or ("Proceedings" not in line and "Companion" not in line) or "." in line or " '" not in line or "workshop" in line or "conference" in line or "symposium" in line:
              #subproblems.append("flawed name: inconsistent formatting of booktitle '"+value+"'")
              #counterFlawedNames += 1

           # check if title is capitalized (heuristic)
           # if field == "title":
            # for word in currentTitle.split(" "):
              #word = word.strip(":")
              # if len(word) > 7 and word[0].islower() and not "-" in word and not "_" in word and not "[" in word:
              #subproblems.append("flawed name: non-capitalized title '"+currentTitle+"'")
              #counterFlawedNames += 1
              # break

          ###############################################################

  problemCount = counterMissingFields + counterFlawedNames + counterWrongFieldNames + counterWrongTypes + counterNonUniqueId

  return render(request, 'results.html', {
    'problems': sorted(problems),
    'problemCount': problemCount,
    'counterMissingFields': counterMissingFields,
    'counterFlawedNames': counterFlawedNames,
    'counterWrongTypes': counterWrongTypes,
    'counterNonUniqueId': counterNonUniqueId,
    'counterWrongFieldNames': counterWrongFieldNames,
    'entriesCount': len(problems),
  })
