#!/usr/bin/python

import requests
import json
import html2text
from threading import Thread
import copy,sys
from Queue import Queue

authorizationObject = {
    "authorization":"Intuit_IAM_Authentication intuit_appid=Intuit.css.processmgmt.agentbuddyforcsa,intuit_app_secret=prdzOuvGLKEZjocYFd5KqpcL6Mf0ghHcaQCqfyfR",
    "cache-control":"no-cache",
    "x-intuit-auth-id":"helix_api_user",
    "x-lc-community-host":"community.intuit.com"
}

def getStringFromHtml(htmlText):
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_emphasis = True
    h.ignore_tables = True
    h.ignore_images = True
    h.unicode_snob = True
    h.open_quote = ''
    h.close_quote = ''
    h.strong_mark = ''
    extractedText = h.handle(htmlText)
    extractedText = extractedText.replace('\n', ' ')
    extractedText = extractedText.replace('\u00a0', ' ')
    return extractedText

def serialCall(ids):
    i = 0
    articleData = {}
    while(i < len(ids)):
        articleUrl = "https://live-community.platform.intuit.com/v2/shared/articles/" + str(ids[i])
        i = i + 1
        articleResponse = requests.request("GET", articleUrl, headers=authorizationObject)
        if articleResponse.ok == False :
            continue
        articleResponse = articleResponse.json()
        bodyOfArticle = articleResponse["article"]["body"]
        articleData[str(i)] = getStringFromHtml(bodyOfArticle)
    return articleData

parallelArticleData = {}
concurrent = 15
q = Queue(concurrent)

def GetResponseFromArticleAPI():
    while True:
        idTuple = q.get()
        try:
            articleResponseJson = CallArticleRestAPI(idTuple[1])
            #don't add if empty article
            if articleResponseJson['isOk'] == True:
                bodyOfArticle = articleResponseJson["article"]["body"]
                bodyOfArticleWithoutSpecialCharacters = getStringFromHtml(bodyOfArticle)
                titleOfArticle = articleResponseJson["article"]["title"]
                individualDocument = {
                    'content':bodyOfArticleWithoutSpecialCharacters,
                    'title':titleOfArticle
                    }
                parallelArticleData[str(idTuple[0])] = individualDocument
        except: pass
        q.task_done()

def CallArticleRestAPI(id):
    try:
        articleUrl = "https://live-community.platform.intuit.com/v2/shared/articles/" + id
        articleResponse = requests.request("GET", articleUrl, headers=authorizationObject)
        if articleResponse.ok == False :
            return {'isOk':False, 'reason':'unexpected response'}
        articleResponseJson = articleResponse.json()
        articleResponseJson['isOk'] = True
        return articleResponseJson
    except:
        return {'isOk' : False,'reason':'exception in http call'}


def ParallelCall(ids):
    i = 0
    while(i<len(ids)):
        t = Thread(target=GetResponseFromArticleAPI)
        i = i + 1
        t.daemon = True
        t.start()
    try:
        i=0
        while(i<len(ids)):
            idTuple = (i,str(ids[i]))
            q.put(idTuple)
            i = i + 1
        q.join()
    except KeyboardInterrupt:
        sys.exit(1)
        print "error in parallel call"

def GetResponseFromLC(query,communityHost="community.intuit.com"):
    url = "https://live-community.platform.intuit.com/v2/shared/search"

    urlParams = {
        'q':query,
        'products':[
            'name::QuickBooks Online'
        ],
        'country':[
            'IN'
        ],
        'document_type':'Article',
        'per_page':15
    }

    response = requests.get( url,params=urlParams, headers=authorizationObject)
    response = response.json()
    resultCollection = response["results"]
    i = 0
    ids = []
    while( i < len(resultCollection)):
        id = resultCollection[i]["type_id"]
        if id:
            ids.append(id)
        i = i + 1

    #articleData = serialCall(ids)
    ParallelCall(ids)
    articleData = copy.deepcopy(parallelArticleData)
    parallelArticleData.clear()
    return json.dumps(articleData)

def main(query):
    import time

    start = time.time()
    response = GetResponseFromLC(query)
    print(response)
    end = time.time()
    print(end - start)

if __name__ == '__main__':
   main(sys.argv[1])
