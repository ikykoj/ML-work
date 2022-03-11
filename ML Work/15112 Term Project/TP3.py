#This is the 15-112 term project by Kay Nam
#Title : Road to 270!

#data from:
#https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/42MVDX 
#https://public.tableau.com/profile/marc.bettis#!/vizhome/ElectionTurnout2020/DesktopLayoutTurnout
#idea and data from:
#https://edition.cnn.com/election/2020/results/president?iid=politics_election_national_map

#appStarted, mousePressed, redrawAll, keyPressed and timerFired were all function names from:
#https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids

#all canvas.create functions came from:
#https://www.cs.cmu.edu/~112/notes/notes-graphics.html

#the struture of this project, is a modification of:
# https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#subclassingModalApp

from cmu_112_graphics import *
import pandas as pd
import csv
import tweepy
import re
from nltk.corpus import stopwords 
from textblob import TextBlob
import string, math, random

class MapMode2020(Mode):
    cState = ''
    cDemSupport = -1
    cDemVotes = -1
    cRepSupport = -1
    cRepVotes = -1
    cDemProp = -1
    cRepProp = -1
    
    #model for MapMode2020
    def appStarted(mode):
        mode.rows = 11
        mode.cols = 13
        mode.cellWidth = mode.width//mode.cols
        mode.cellHeight = mode.height//mode.rows
        mode.board = [([False]*mode.cols) for row in range(mode.rows)]
        mode.colors = [(['white']*mode.cols) for row in range(mode.rows)]
        mode.stateName = [([False]*mode.cols) for row in range(mode.rows)]
        mode.stateInfo = {
        "AK":[1,0,'Rep'], "ME":[1,12,'Dem'], "WA":[3,1,'Dem'], "ID":[3,2,'Rep'],"MT":[3,3,'Rep'], "ND":[3,4,'Rep'],
        "MN":[3,5,'Dem'], "IL":[3,6,'Dem'],"WI":[3,7,'Dem'], "MI":[3,8,'Dem'], "NY":[3,9,'Dem'], "RI":[3,10,'Dem'],
        "MA":[3,11,'Dem'], "VT":[2,10,'Dem'], "NH":[2,11,'Dem'], "OR":[4,1,'Dem'],"NV":[4,2,'Dem'], "WY":[4,3,'Rep'], 
        "SD":[4,4,'Rep'], "IA":[4,5,'Rep'], "IN":[4,6,'Rep'], "OH":[4,7,'Rep'],"PA":[4,8,'Dem'], "NJ":[4,9,'Dem'],
        "CT":[4,10,'Dem'], "CA":[5,1,'Dem'], "UT":[5,2,'Rep'], "CO":[5,3,'Dem'], "NE":[5,4,'Rep'], "MO":[5,5,'Rep'],
        "KY":[5,6,'Rep'], "WV":[5,7,'Rep'], "VA":[5,8,'Dem'], "MD":[5,9,'Dem'], "DE":[5,10,'Dem'], "AZ":[6,2,'Dem'],
        "NM":[6,3,'Dem'], "KS":[6,4,'Rep'], "AR":[6,5,'Rep'], "TN":[6,6,'Rep'], "DC":[6,9,'Dem'], "OK":[7,4,'Rep'],
        "LA":[7,5,'Rep'], "MS":[7,6,'Rep'], "NC":[6,7,'Rep'], "SC":[6,8,'Rep'], "AL":[7,7,'Rep'], "GA":[7,8,'Dem'],
        "HI":[8,0,'Dem'], "TX":[8,4,'Rep'], "FL":[8,9,'Rep']}
        for key in mode.stateInfo:
            row = mode.stateInfo[key][0]
            col = mode.stateInfo[key][1]
            mode.board[row][col] = True
            winParty = mode.stateInfo[key][2]
            if winParty == 'Dem':
                mode.colors[row][col] = 'blue'
            else:
                mode.colors[row][col] = 'red'
            mode.stateName[row][col] = str(key)
        mode.currData = dict()
        mode.currYearDataProcessor()
        mode.pastData = {'1976': {}, '1980': {}, '1984': {}, '1988': {}, '1992': {}, '1996': {}, '2000': {}, '2004': {}, '2008': {}, '2012': {}, '2016': {}}
        mode.pastYearDataProcessor()
        mode.pressed = False
    
    #processes data for presidential election 2020
    #https://stackoverflow.com/questions/6740918/creating-a-dictionary-from-a-csv-file
    def currYearDataProcessor(mode):
        filename = "2020data.csv"
        with open(filename,'r') as data:
            for line in csv.reader(data):
                state = line[0]
                line[3] = line[3].replace(',', '')
                line[4] = line[4].replace(',', '')
                mode.currData[state] = [[line[1], line[3]],[line[2], line[4]]]

    #processes data for presidential elections from 1976 to 2016
    #https://stackoverflow.com/questions/6740918/creating-a-dictionary-from-a-csv-file
    def pastYearDataProcessor(mode):
        filename="1976-2016-president.csv"
        with open(filename,'r') as data: 
            for line in csv.reader(data): 
                year = line[0]
                state = line[1]
                rest = line[2:7]
                if state in mode.pastData[year]:
                    mode.pastData[year][state] += [rest]
                else:
                    mode.pastData[year][state] = [rest]

    #a controller function
    def mousePressed(mode, event):
        row, col = mode.getCell(event.x, event.y)
        if mode.board[row][col] != False:
            MapMode2020.cState = mode.stateName[row][col]
            MapMode2020.cDemSupport = float(mode.currData[MapMode2020.cState][0][0])
            MapMode2020.cDemVotes = int(mode.currData[MapMode2020.cState][0][1])
            MapMode2020.cRepSupport = float(mode.currData[MapMode2020.cState][1][0])
            MapMode2020.cRepVotes = int(mode.currData[MapMode2020.cState][1][1])
            MapMode2020.cDemProp = (MapMode2020.cDemSupport)/(MapMode2020.cDemSupport+MapMode2020.cRepSupport)
            MapMode2020.cRepProp = (MapMode2020.cRepSupport)/(MapMode2020.cDemSupport+MapMode2020.cRepSupport)
            mode.app.setActiveMode(mode.app.VisualizeState)
        if mode.pressed == False:
            mode.pressedCoor = [event.x, event.y]
        if mode.pressed == True:
            mode.pressed = False

    #a controller function        
    def keyPressed(mode, event):
        if event.key == 'Left':
            mode.app.setActiveMode(mode.app.MainInstructionMode)

    #modified from course notes https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    #draws the grid that serve as reference points for the map drawing
    def drawGrid(mode, canvas):
        for row in range(mode.rows):
            for col in range(mode.cols):
                if mode.board[row][col] != False:
                    (x0, y0, x1, y1) = mode.getCellBounds(canvas, row, col)
                    canvas.create_rectangle(x0, y0, x1, y1, fill = mode.colors[row][col], outline = 'black')
                    canvas.create_text((x0+x1)/2, (y0+y1)/2, text = mode.stateName[row][col], 
                                        font = 'Arial 20 bold')

    #from course notes https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    #get x, y values from row, col input
    def getCellBounds(mode, canvas, row, col):
        x0 = col * mode.cellWidth
        x1 = (col+1) * mode.cellWidth
        y0 = row * mode.cellHeight
        y1 = (row+1) * mode.cellHeight
        return x0, y0, x1, y1

    #from course notes https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    #get row, col values from x, y input
    def getCell(mode, x, y):
        row = int(y/mode.cellHeight)
        col = int(x/mode.cellWidth)
        return row, col

    #draws the title and the main instructions
    def drawTitle(mode, canvas):
        canvas.create_text(mode.width/2, 70, text = "Presidential Election 2020", 
                    font = 'Arial 30 bold')
        canvas.create_text(mode.width/2, 100, text = "Click on a state to view more information!", 
                    font = 'Arial 30 bold') 

    #the view
    def redrawAll(mode, canvas):
        mode.drawTitle(canvas)
        mode.drawGrid(canvas)

class VisualizeState(MapMode2020):
    #the model for VisualizeState
    def appStarted(mode):
        super().appStarted() 
        mode.plotRows = 10
        mode.plotCols = 11
        mode.demPoints = []
        mode.repPoints = []
        mode.configureAllPoints()
        mode.currDemPoints = []
        mode.currRepPoints = []
        mode.yearList = [key for key in mode.pastData]
        mode.cellWidth = mode.width
        mode.cellHeight = (mode.height/2)/mode.plotRows
        mode.buttonList = []
        mode.startYear = ''
        mode.plot = False
        mode.zoom = False
        mode.zoomCoor = []
        mode.pressed1 = False
        mode.pressed2 = False
        mode.distBetweenPointsD = 0 
        mode.distBetweenPointsR = 0
        mode.pointsCoordD = []
        mode.pointsCoordR = []
        mode.zoomPointsD = []
        mode.zoomPointsR = []

    #draws bar graph that represents the vote proportions of each party in that particular state
    def drawBar(mode, canvas):
        #process data 
        canvas.create_text(mode.width/2, mode.height/14, 
        text = f"State of {MapMode2020.cState} 2020 Election Results", 
        font = 'Arial 20 bold')
        scaledDemWidth = (mode.width/2)*MapMode2020.cDemProp
        scaledRepWidth = (mode.width/2)*MapMode2020.cRepProp

        #draw bar chart
        start = mode.width/4
        end = (mode.width/4)*3
        lowH = mode.height/10
        highH = mode.height/7
        canvas.create_rectangle(start, lowH, start + scaledDemWidth, highH, fill = 'blue')
        canvas.create_text((start*2+scaledDemWidth)/2, (lowH+highH)/2, 
        text = 'Democrats', font = 'Arial 15 bold')
        canvas.create_rectangle(start + scaledDemWidth, lowH, end, highH, fill = 'red')
        canvas.create_text((start+scaledDemWidth+end)/2, (lowH+highH)/2, 
        text = 'Republicans', font = 'Arial 15 bold')
        canvas.create_text((start*2+scaledDemWidth)/2, highH+20, 
        text = f'{MapMode2020.cDemVotes} votes', font = 'Arial 15 bold')
        canvas.create_text((start+scaledDemWidth+end)/2, highH+20, 
        text = f'{MapMode2020.cRepVotes} votes', font = 'Arial 15 bold')

    #draws the scaffolding grid that the line graph would be base on.
    #modified from course notes https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    def drawTrendGraph(mode, canvas):
        for row in range(mode.plotRows):
            for col in range(mode.plotCols):
                (x0, y0, x1, y1) = mode.getCellBounds(canvas, row, col)
                x0 += mode.width/10
                x1 -= mode.width/10
                y0 += mode.height/2.5
                y1 += mode.height/2.5
                canvas.create_rectangle(x0, y0, x1, y1, 
                fill = 'white', outline = 'black')

    #draws the axis for the line graph
    def drawAxis(mode, canvas):
        w, h, ch = mode.width, mode.height, mode.cellHeight
        #draw y axis
        canvas.create_line(w/10, h/2.5, w/10, h/2.5 + ch*10, 
        fill = 'red', width = 5)
        #draw x axis
        canvas.create_line(w/10, h/2.5 + ch*10, w-(w/10), h/2.5+ch*10, 
        fill = 'red', width = 5)
        #draw labels
        canvas.create_text(w/20, h/2.5 + ch*5, text = 'Percentage(%)',
        font = 'Arial 10 bold', angle = 90)
        canvas.create_text(w/2, h/2.5 + ch*11, text = 'Year',
        font = 'Arial 12 bold')

    #draws the multiple options for starting points
    def drawSlider(mode, canvas):
        cx, cy = mode.width/10, mode.height/3.5
        canvas.create_text(mode.width/2, cy-50, 
        text = f"\tSupport for parties over the years in {mode.cState}(1976-2016)\
        \n Choose a starting point for the plot by clicking on the buttons below!",
        font = 'Arial 13 bold')
        step = (mode.width-mode.width/10*2)/(len(mode.pastData)-1)
        r = 20 
        yearList = [key for key in mode.pastData]
        currState = MapMode2020.cState
        for year in yearList:
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill = 'pink')
            canvas.create_text(cx, cy, text = year)
            candidateList = mode.pastData[year][currState]
            firstCandidate = candidateList[0][0]
            secondCandidate = candidateList[1][0]
            canvas.create_text(cx, cy+2*r, text = f"{firstCandidate}\n          
            vs. \n {secondCandidate}", font = 'Arial 8')
            mode.buttonList.append([year, cx, cy])
            cx += step

    #controller function
    def mousePressed(mode, event):
        for button in mode.buttonList:
            year = button[0]
            cx, cy = button[1], button[2]
            if distance(cx, cy, event.x, event.y) < 20:
                mode.startYear = year 
                index = mode.yearList.index(year)
                mode.currDemPoints = mode.demPoints[index:]
                mode.currRepPoints = mode.repPoints[index:] 
                mode.croppedYearList = mode.yearList[index:]
                mode.plot = True
        if (mode.pressed1 == True and mode.width/10<event.x<(mode.width)-mode.width/10 and 
                mode.height/2.5 < event.y < mode.height):
            mode.zoomCoor.append((event.x, event.y))
            mode.pressed2 = True
            mode.zoom = True
        elif mode.pressed1 == True and mode.pressed2 == True:
            mode.pressed1 = False
            mode.pressed2 = False
            mode.zoom = False
            mode.zoomCoor = []
            mode.zoomPointsD = []
            mode.zoomPointsR = []
        else:
            if (mode.width/10<event.x<(mode.width)-mode.width/10 and 
                mode.height/2.5 < event.y < mode.height):
                mode.pressed1 = True
                mode.zoomCoor.append((event.x, event.y))

    #controller function
    def keyPressed(mode, event):
        if event.key == 'Left':
            mode.app.setActiveMode(mode.app.MapMode2020)
            mode.currDemPoints = []
            mode.currRepPoints = []

    #called when zoom feature is enabled, and configures the points that are going to be zoomed
    def zoomAction(mode, canvas):
        (cx1, cy1) = mode.zoomCoor[0]
        (cx2, cy2) = mode.zoomCoor[1]
        row1, col1 = mode.getCell(cx1, cy1)
        row2, col2 = mode.getCell(cx2, cy2)
        canvas.create_rectangle(cx1, cy1, cx2, cy2, fill='', outline = 'yellow', width = '10')
        for i in range(len(mode.pointsCoordD)):
            dx, dy = mode.pointsCoordD[i]
            rx, ry = mode.pointsCoordR[i]
            if cx1 < dx < cx2 and cy1 < dy < cy2:
                mode.zoomPointsD.append(i)
            if cx1 < rx < cx2 and cy1 < ry < cy2:
                mode.zoomPointsR.append(i)

    #configures all points for the line graph
    def configureAllPoints(mode):
        currState = MapMode2020.cState
        for year in mode.pastData:
            currList = mode.pastData[year][currState]
            for i in range(len(currList)):
                if currList[i][1] == 'republican':
                    mode.repPoints.append(float(currList[i][4]))
                else:
                    mode.demPoints.append(float(currList[i][4]))

    #plot trend points for the democratic party
    def plotDemPoints(mode, canvas):
        start = mode.width/5 
        end = mode.width - start
        mode.distBetweenPointsD = (mode.width*0.6)/(len(mode.currDemPoints)-1)
        mode.pointsCoordD = []
        for i in range(len(mode.currDemPoints)):
            cx = start+i*mode.distBetweenPointsD
            cy = (mode.height/2.5)+(mode.cellHeight*10*(1-mode.currDemPoints[i]))
            r = 10
            mode.pointsCoordD.append((cx, cy))
            if mode.zoomCoor != [ ] and mode.zoom: #different configurations for zoom mode
                cx1, cy1 = mode.zoomCoor[0]
                cx2, cy2 = mode.zoomCoor[1]
                if cx1 < cx < cx2 and cy1 < cy < cy2:
                    canvas.create_oval(cx-2*r, (cy+r)-2*r, cx+2*r, (cy+r)+2*r, 
                    fill = 'blue')
                    mode.zoomPointsD.append((cx, cy-r))
                    canvas.create_text(cx, cy+r, 
                    text = f'{int(mode.currDemPoints[i]*100)}', 
                    font = 'Arial 20 bold', fill = 'white')
            else:
                canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill = 'blue')
                canvas.create_text(cx, cy, text = f'{int(mode.currDemPoints[i]*100)}',
                font = 'Arial 12 bold', fill = 'white')
                canvas.create_text(cx, mode.height/2.5 + mode.cellHeight*10.5, 
                text = f'{mode.croppedYearList[i]}',
                font = 'Arial 12 bold')
            if i > 0:
                (cx1, cy1) = mode.pointsCoordD[i-1]
                canvas.create_line(cx, cy, cx1, cy1, fill = 'blue')

    #plot trend points for the republican party    
    def plotRepPoints(mode, canvas):
        start = mode.width/5 
        end = mode.width - start
        mode.distBetweenPointsR = (mode.width*0.6)/(len(mode.currRepPoints)-1)
        mode.pointsCoordR = []
        for i in range(len(mode.currRepPoints)):
            cx = start+i*mode.distBetweenPointsR
            cy = (mode.height/2.5)+(mode.cellHeight*10*(1-mode.currRepPoints[i]))
            r = 10
            mode.pointsCoordR.append((cx, cy))
            if mode.zoomCoor != [ ] and mode.zoom:
                cx1, cy1 = mode.zoomCoor[0]
                cx2, cy2 = mode.zoomCoor[1]
                if cx1 < cx < cx2 and cy1 < cy < cy2:
                    canvas.create_oval(cx-2*r, (cy-r)-2*r, cx+2*r, (cy-r)+2*r, 
                    fill = 'red')
                    mode.zoomPointsR.append((cx, cy-r))
                    canvas.create_text(cx, cy-r, 
                    text = f'{int(mode.currRepPoints[i]*100)}',
                    font = 'Arial 20 bold', fill = 'white')
            else:
                canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill = 'red')
                canvas.create_text(cx, cy, text = f'{int(mode.currRepPoints[i]*100)}',
                font = 'Arial 12 bold', fill = 'white')
                canvas.create_text(cx, mode.height/2.5 + mode.cellHeight*10.5, text = f'{mode.croppedYearList[i]}',
                font = 'Arial 12 bold')
            if i > 0:
                (cx1, cy1) = mode.pointsCoordR[i-1]
                canvas.create_line(cx, cy, cx1, cy1, fill = 'red')
            
    #the view
    def redrawAll(mode, canvas):
        mode.drawBar(canvas)
        mode.drawTrendGraph(canvas)
        mode.drawAxis(canvas)
        mode.drawSlider(canvas)
        if mode.plot:
            mode.plotDemPoints(canvas)
            mode.plotRepPoints(canvas)
        if mode.zoom:
            mode.zoomAction(canvas)
        if mode.pressed1:
            cx, cy = mode.zoomCoor[0]
            r = 5
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill = 'yellow')
        if mode.pressed2:
            cx, cy = mode.zoomCoor[1]
            r = 5
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill = 'yellow')

#formula from https://www.google.com/search?q=distance+formula&oq=distance+formula&aqs=chrome.0.0i457j0l7.5113j0j4&sourceid=chrome&ie=UTF-8
#function to compute distance between two points
def distance(x0, y0, x1, y1):
    return ((x0-x1)**2+(y0-y1)**2)**0.5

class TwitterMode(Mode):
    processed = dict()
    avgOverallSentiment = 0
    wordFreqDict = dict()
    hashtag = '#'
    #The code for extracting authentication information from twitter:
    #https://medium.com/python-in-plain-english/scraping-tweets-with-tweepy-python-59413046e788
    #the model function
    def appStarted(mode):
        mode.apiKey = 'OnLEvveu5cWI3uQnKcAY0hHRq'
        mode.apiSecret = 'QDo4k0fUhdz5cINLDUcrKLVkzre35iwkCnqiS7VnFtmzKRsuXa'
        mode.accessToken = '1330750942812065797-llzjA4RdOHQ7WinYU2mekApyJ5fphp'
        mode.accessTokenSecret = 'WzMSja3fglex51MbkhUDRmJHOfIff0vAv79QHQwtnTmVR'

        #create authentication object
        mode.authenticate = tweepy.OAuthHandler(mode.apiKey, mode.apiSecret)

        #set access token and access token secret
        mode.authenticate.set_access_token(mode.accessToken, mode.accessTokenSecret)

        #create api object while passing in auth info
        mode.api = tweepy.API(mode.authenticate, wait_on_rate_limit = True)
        
        mode.query = []
        mode.tweets = []
        mode.warningScreen = False
        mode.warnCount = 0
    
    #controller function
    def keyPressed(mode, event):
        if (event.key in string.ascii_letters or event.key in string.digits
            or event.key in string.punctuation):
            TwitterMode.hashtag += f'{event.key}'
        if event.key == 'Delete':
            if len(TwitterMode.hashtag) > 1:
                TwitterMode.hashtag = TwitterMode.hashtag[:-1]
        if event.key == 'Enter':
            if len(TwitterMode.hashtag) > 1:
                mode.app.setActiveMode(mode.app.LoadingScreenMode)
                #code from https://towardsdatascience.com/how-to-scrape-more-information-from-tweets-on-twitter-44fd540b8a1f
                mode.query = tweepy.Cursor(mode.api.search, q = TwitterMode.hashtag).items(20)
                mode.tweets = [tweet.text for tweet in mode.query]
                mode.processTweets()
            else:
                mode.warningScreen = True
        if event.key == 'Left':
            mode.app.setActiveMode(mode.app.MainInstructionMode)

    #I learned the syntax for textblob here:
    #https://towardsdatascience.com/my-absolute-go-to-for-sentiment-analysis-textblob-3ac3a11d524
    #process tweets so that they have gone through data cleaning and basic sentiment analysis
    def processTweets(mode):
        stopWords = set(stopwords.words("english")) #from https://www.youtube.com/watch?v=w36-U-ccajM
        for line in mode.tweets:
            cleanedLine = mode.cleanTweets(line)
            filteredList = cleanedLine.split(" ")
            overallSentiment = 0 
            for word in filteredList:
                currSentiment = 0 
                if word.lower() not in stopWords and len(word) > 2:
                    word = word.strip(string.punctuation)
                    analysis = TextBlob(word)
                    if analysis.sentiment.polarity > 0:
                        currSentiment += 1
                    elif analysis.sentiment.polarity < 0:
                        currSentiment -= 1
                    mode.wordFreqDict[word] = 1 + mode.wordFreqDict.get(word, 0)
                    overallSentiment += currSentiment
        TwitterMode.avgOverallSentiment = overallSentiment / len(mode.tweets)

    #utilized information from https://docs.python.org/3/howto/regex.html
    #helper function to clean each line of tweet so that meaningless characters are disregarded
    def cleanTweets(mode, line):
        line = re.sub(r"RT @[\w]*:","",line)
        line = re.sub(r"@[\w]*","",line)
        line = re.sub(r"#[\w]*","",line)
        line = re.sub(r"https?://[A-Za-z0-9./]*","",line)
        line = re.sub(r"[^\x00-\x7F]", "",line)
        line = re.sub(r"\n","",line)
        return line
            
    #visualize the title and instructions for twitter mode
    def twitterTitle(mode, canvas):
        canvas.create_text(mode.width/2, mode.height/4, text = 'Welcome to Twitter Mode!!',
            font = 'Courier 30 bold', fill = 'skyblue')
        canvas.create_text(mode.width/2, mode.height/4-50, 
        text = 'Enter a hashtag related to the 2020 Presidential election',
            font = 'Courier 20 bold', fill = 'skyblue')
        canvas.create_text(mode.width/2, mode.height/2.5, 
            text = '\t\tEnter your hashtag here!\
            \n\n\t Some examples of hashtags are: \
            \n\t#DonaldTrump, #JoeBiden, #presidentialdebate\
            \n\n\t When you have finished typing it, \
            \n\t hit the enter button to start the analysis!\
            \n\n\t Press a key to start typing!',
            font = 'Courier 16 bold', fill = 'black')

    #draws the hashtag box that the user can type into
    def drawHashTag(mode, canvas):
        if len(TwitterMode.hashtag) < 10:
            canvas.create_rectangle(mode.width/2-100, mode.height/2+50, 
                                    mode.width/2+100, mode.height/2+150,
                                    fill = 'pink')
        else:
            h = len(TwitterMode.hashtag)
            canvas.create_rectangle(mode.width/2-100-(7*h), mode.height/2+50, 
                                    mode.width/2+100+(7*h), mode.height/2+150,
                                    fill = 'pink')
        canvas.create_text(mode.width/2, mode.height/2+100, 
        text = f"{TwitterMode.hashtag}", font = 'Arial 40 bold')

    #draw the warning screen: the warning screen is triggered when the user does not enter anything.
    def drawWarningScreen(mode, canvas):
        w, h = mode.width, mode.height
        canvas.create_rectangle(w/3, h/3, w/1.5, h/1.5, fill = 'red')
        canvas.create_text(w/2, h/2, text = '\tYou have not \n\tentered anything.\
            \n\tPlease enter a hashtag', fill = 'white', font = 'Courier 16 bold')

    #controller function
    def timerFired(mode):
        if mode.warningScreen:
            mode.warnCount += 1 
            if mode.warnCount == 30:
                mode.warningScreen = False
                mode.warnCount = 0

    #the view
    def redrawAll(mode, canvas):
        mode.twitterTitle(canvas)
        mode.drawHashTag(canvas)
        if mode.warningScreen:
            mode.drawWarningScreen(canvas)
        

class LoadingScreenMode(TwitterMode):
    #the model function
    def appStarted(mode):
        super().appStarted() 
        mode.count = 0
        mode.step = 50
        mode.colors = ['pink', 'lightgreen', 'red', 'orange', 'violet']
        mode.currColor = 'gold'
        mode.currPercent = 0
        mode.timerDelay = 200

    #controller function
    def timerFired(mode):
        mode.count += 1
        mode.currColor = random.choice(mode.colors)
        mode.currPercent += 4
        if mode.count == 25:
            mode.count = 0
            mode.app.setActiveMode(mode.app.WordCloudMode)
            
    #draw the loading sign(circle, text) while the scraping from twitter is happening
    def drawLoadingSign(mode, canvas):
        cx, cy = mode.width/2, mode.height/2
        r = mode.width/4
        canvas.create_text(cx, cy-r-50, text = 'Loading...', fill = mode.currColor, 
                font = 'Courier 40 bold')
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill = mode.currColor, width = 10)
        canvas.create_text(cx, cy, text = f"{mode.currPercent}%", 
                font = 'Courier 50 bold')
        canvas.create_text(cx, cy+r+50, 
                text = 'The program is currently scraping the data off Twitter.', 
                fill = mode.currColor, font = 'Courier 20 bold')

    #the view
    def redrawAll(mode, canvas):
        mode.drawLoadingSign(canvas)

class WordCloudMode(TwitterMode):
    #the model
    def appStarted(mode):
        super().appStarted() 
        mode.rectCoord = []
        mode.ymargin = mode.width/3
        mode.rows = 10
        mode.cols = 10
        mode.board = [[False]*mode.cols for row in range(mode.rows)]
        mode.cellHeight = (mode.height-mode.ymargin)/mode.rows
        mode.cellWidth = (mode.width)/mode.cols
        mode.colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
        mode.color = [['white']*mode.cols for row in range(mode.rows)]
        mode.info = []
        mode.drawFlag = False
        mode.freq = []
        mode.listforWC = []
        mode.rectangles = sorted(mode.freq, reverse = True) # https://www.afternerd.com/blog/python-sort-list/#:~:text=If%20you%20want%20to%20sort,They%20both%20accept%20it!
        mode.makeFreqList()
        for freq in mode.freq:
            freq = int(freq/sum(mode.freq))*200
        mode.findSpaceWrapper()
        mode.board = [[False]*mode.cols for row in range(mode.rows)]
        mode.currWord = ''
        mode.currFreq = 0
        mode.pressed = False
        
    #from the scraped twitter data, create a list of words to extract frequency data
    def makeFreqList(mode):
        d = TwitterMode.wordFreqDict
        for i in range(10):
            maxWord = max(d, key = lambda x:d[x]) # code modified from https://www.youtube.com/watch?v=XzyfhxnL5nA
            mode.freq.append(d[maxWord])
            mode.listforWC.append([maxWord, d[maxWord]])
            del d[maxWord]

    #idea from https://www.cs.cmu.edu/~112/notes/notes-recursion-part1.html#wrapperFunctions
    #wrapper function for findSpace function
    def findSpaceWrapper(mode):
        if mode.findSpace(mode.listforWC):
            mode.drawFlag = True

    #structural idea from https://www.cs.cmu.edu/~112/notes/notes-recursion-part2.html#nQueens
    #recursive function that finds if a rectangle can be placed on the canvas without overlapping
    #with one another. 
    def findSpace(mode, data):
        if data == [ ]:
            return True
        else:
            firstWord = data[0][0]
            firstFreq = data[0][1]
            for row1 in range(len(mode.board)):
                for col1 in range(len(mode.board[0])):
                    for row2 in range(len(mode.board)):
                        for col2 in range(len(mode.board[0])):
                            if mode.isValid(row1, col1, row2, col2, firstFreq):
                                mode.info.append((firstWord, firstFreq, row1, col1, row2, col2))
                                color = random.choice(mode.colors)
                                for row in range(row1, row2+1):
                                    for col in range(col1, col2+1):
                                        mode.board[row][col] = True
                                        mode.color[row][col] = color
                                solution = mode.findSpace(data[1:])
                                if solution != None:
                                    a0, b0, a1, b1 = mode.getCellBounds(row1, col1)
                                    c0, d0, c1, d1 = mode.getCellBounds(row2, col2)
                                    mode.rectCoord.append((a0, b0, c1, d1, firstWord, firstFreq))
                                    return solution
                                mode.info.remove((firstWord, firstFreq, row1, col1, row2, col2))
                                for row in range(row1, row2+1):
                                    for col in range(col1, col2+1):
                                        mode.board[row][col] = False
            return None

    #idea from nQueens.py from:
    #https://www.cs.cmu.edu/~112/notes/notes-recursion-part2.html#nQueens
    #function that checks whether placing the rectangle at the given row, col value
    #is a legal move.
    def isValid(app, row1, col1, row2, col2, first):  
        if (row1 != row2 or col1 != col2):
            if ((abs(row2-row1)+1)*(abs(col2-col1)+1) == first
                and app.board[row1][col1] == False
                and app.board[row2][col2] == False):
                return True
        return False

    #draws the treemap based on the coordinates of legal rectangles
    def drawTreeMap(mode, canvas):
        for rect in mode.info:
            firstWord, firstFreq, row1, col1, row2, col2 = rect
            for row in range(row1, row2+1):
                for col in range(col1, col2+1):
                    mode.board[row][col] == True
                    a0, b0, a1, b1 = mode.getCellBounds(row1, col1)
                    c0, d0, c1, d1 = mode.getCellBounds(row2, col2)
                    color = mode.color[row][col]
                    canvas.create_rectangle(a0, b0, c1, d1, fill = color)
                    if abs(row1-row2) < abs(col1-col2):
                        canvas.create_text((a0+c1)/2, (b0+d1)/2, text = firstWord, 
                        font = f'Arial {firstFreq*10} bold', fill = 'black')
                    else:
                        canvas.create_text((a0+c1)/2, (b0+d1)/2, text = firstWord, 
                        font = f'Arial {firstFreq*10} bold', fill = 'black', angle = 90)

    #controller function
    def keyPressed(mode, event):
        if event.key == 'Left':
            mode.app.setActiveMode(mode.app.TwitterMode)
        
    #modified from course notes:
    #https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    #returns x, y coordinate values from the row, col input
    def getCellBounds(mode, row, col):
        x0 = col * mode.cellWidth 
        x1 = (col+1) * mode.cellWidth
        y0 = mode.ymargin + row * mode.cellHeight*(2.5)
        y1 = mode.ymargin + (row+1) * mode.cellHeight*(2.5)
        return x0, y0, x1, y1      

    #modified from course notes: 
    #https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    #returns row, col values from x, y coordinates
    def getCell(mode, x, y):
        row = int(y/mode.cellHeight)
        col = int(x/mode.cellWidth)
        return row, col

    #draws the title that explains what the treemap represents. 
    def drawTitle(mode, canvas):
        canvas.create_text(mode.width/2, mode.height/8, 
            text = f'Treemap: {TwitterMode.hashtag}',
            font = 'Courier 40 bold', fill = 'skyblue')
        canvas.create_text(mode.width/2, mode.height/4, 
            text = "   This is the treemap for your input hashtag!\
                    \n   The size of each rectangle is the frequency of that word\
                    \n   If you click on a word in the rectangle, \
                    you can see the specific frequency of the word.\
                    \n   Press the left key to enter another hashtag",
                    font = 'Courier 12 bold', fill = 'black')
        canvas.create_rectangle(mode.width-200, mode.height/6, 
        mode.width-20, mode.height/4.5, fill = 'lightgreen')
        sentiment = TwitterMode.avgOverallSentiment
        if 0.5 <= sentiment < 1.0:
            newSentiment = f'stongly positive({sentiment})'
        elif 0 < sentiment < 0.5:
            newSentiment = f'slightly positive({sentiment})'
        elif -0.5 < sentiment < 0:
            newSentiment = f'slightly negative({sentiment})'
        elif -1.0 < sentiment <= -0.5:
            newSentiment = f'stongly negative({sentiment})'
        elif sentiment == 0:
            newSentiment = f'neutral({sentiment})'
        canvas.create_text(mode.width-110, mode.height/5.25, text = f"Overall Sentiment:\n {newSentiment}")

    #controller function
    def mousePressed(mode, event):
        mode.currWord = ''
        mode.currFreq = 0
        if mode.pressed == False:
            for i in range(len(mode.rectCoord)):
                x0, y0, x1, y1, firstWord, firstFreq = mode.rectCoord[i]
                if x0 < event.x < x1 and y0 < event.y < y1:
                    mode.currWord = firstWord
                    mode.currFreq = firstFreq
        if mode.pressed == True:
            for i in range(len(mode.rectCoord)):
                x0, y0, x1, y1, firstWord, firstFreq = mode.rectCoord[i]
                if x0 < event.x < x1 and y0 < event.y < y1:
                    mode.currWord = firstWord
                    mode.currFreq = firstFreq
                else:
                    mode.pressed = False

    #draws the informatory rectangle at the bottom of the screen that is activated when 
    #each rectangle is clicked. visualizes the selected word and the frequency of it.
    def drawHover(mode, canvas):
        x0 = mode.width/3
        x1 = mode.width/1.5
        y0 = mode.height - 100
        y1 = mode.height - 25
        canvas.create_rectangle(x0, y0, x1, y1, fill = 'pink')
        canvas.create_text((x0+x1)/2, (y0+y1)/2, 
        text = f"Frequency of \n'{mode.currWord}':{mode.currFreq}", 
        font = 'Arial 20 bold')

    #the view
    def redrawAll(mode, canvas):
        mode.drawTitle(canvas)
        if mode.drawFlag == True:
            mode.drawTreeMap(canvas)
        mode.drawHover(canvas)
        
class MainInstructionMode(Mode):
    #the model
    def appStarted(mode):
        mode.buttonList = [[mode.width/4, mode.height-200, 'MapMode2020'], 
                            [3*(mode.width/4), mode.height-200, 'TwitterMode']]
        mode.buttonR = 80
        mode.buttonColorList = ['pink', 'skyblue']

    #controller function
    def mousePressed(mode, event):
        r = 80
        for button in mode.buttonList:
            cx, cy, currMode = button[0], button[1], button[2]
            if distance(cx, cy, event.x, event.y) <= r:
                if currMode == 'MapMode2020':
                    mode.app.setActiveMode(mode.app.MapMode2020)
                else:
                    mode.app.setActiveMode(mode.app.TwitterMode)

    #draws the instructions for the entire app.
    def drawInstructions(mode, canvas):
        canvas.create_text(mode.width/2, mode.height/2, 
            text = "\t\tThere are two different modes in this app.\
                    \n\n\t\t1.The first is Map Mode, where you can go and find statistical\
                    \n\t\tillustration of the result of this year's election.\
                    \n\n\t\t2.The second is Twitter mode, where you can enter hashtags related\
                    \n\t\tto the election to find the public sentiment on that hashtag and\
                    \n\t\tan analysis of the tweets on that hashtag. \
                    \n\t\t\t 3.Press on the 'Left' key to go back a page.\
                    \n\n\t\tPress on a button below to go to each mode!",
            font = 'Courier 16 bold', fill = 'black')
        
    #draws title for the main instruction page
    def drawTitle(mode, canvas):
        canvas.create_text(mode.width/2, mode.height/4, text = 'How to use this app',
            font = 'Courier 50 bold', fill = 'skyblue')

    #draws the buttons that lead to specific modes
    def drawButtons(mode, canvas):
        for i in range(len(mode.buttonList)):
            button = mode.buttonList[i]
            cx, cy, r = button[0], button[1], mode.buttonR
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill = mode.buttonColorList[i])
            canvas.create_text(cx, cy, text = button[2], font = 'Courier 16 bold')

    #the view
    def redrawAll(mode, canvas):
        mode.drawTitle(canvas)
        mode.drawInstructions(canvas)
        mode.drawButtons(canvas)

#code modified from course notes
class SplashScreenMode(Mode):
    #the model 
    #code modified from Jacob Feldgoise's tp https://www.youtube.com/watch?v=YTI5BfJE6FI
    def appStarted(mode): 
        #background image from https://ichef.bbci.co.uk/news/800/cpsprodpb/2704/production/_114788990_polltracker_index_promo976_v2.png
        backgroundLink = ("https://ichef.bbci.co.uk/news/800/cpsprodpb/2704/production/_114788990_polltracker_index_promo976_v2.png")
        mode.configureBackground(backgroundLink, 1.5)

    #code modified from Jacob Feldgoise's tp https://www.youtube.com/watch?v=YTI5BfJE6FI
    #scales the image so that it matches the canvas
    def configureBackground(mode, link, scale):
        background = mode.app.loadImage(link)
        mode.background = mode.app.scaleImage(background, scale)

    #code modified from Jacob Feldgoise's tp https://www.youtube.com/watch?v=YTI5BfJE6FI
    #draws the background with the given image. 
    def drawBackground(mode, canvas):
        canvas.create_image(mode.width/2, mode.height/2,
        image = ImageTk.PhotoImage(mode.background))

    #the view
    def redrawAll(mode, canvas):
        mode.drawBackground(canvas)
        canvas.create_text(mode.width/2, mode.height/4, text='Road to 270!', font='Courier 60 bold', fill= 'black')
        canvas.create_text(mode.width/2, mode.height/2, text='Click to get started', font='Courier 40 bold', fill = 'black')
        
    #controller function
    def mousePressed(mode, event):
        mode.app.setActiveMode(mode.app.MainInstructionMode)

#modified from https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#subclassingModalApp
class MyModalApp(ModalApp):
    #the model 
    def appStarted(app):
        app.SplashScreenMode = SplashScreenMode()
        app.MainInstructionMode = MainInstructionMode()
        app.MapMode2020 = MapMode2020()
        app.VisualizeState = VisualizeState()
        app.TwitterMode = TwitterMode()
        app.LoadingScreenMode = LoadingScreenMode()
        app.WordCloudMode = WordCloudMode()
        app.setActiveMode(app.SplashScreenMode)
        app.timerDelay = 50

app = MyModalApp(width=800, height=800) 

